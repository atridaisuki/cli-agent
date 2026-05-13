"""
Agent — ReAct 核心循环

while True:
    调 LLM（流式）
    如果 stop_reason == end_turn → 返回文本
    如果有 tool_calls → 执行工具 → 结果追加 → 继续循环
"""

import json
from openai import OpenAI
from tools import get_tool_definitions, execute_tool
from permissions import check_permission
from session import SessionStore
from context import ContextCompressor


class Agent:
    def __init__(self, client: OpenAI, model: str, system_prompt: str,
                 session_store: SessionStore, compressor: ContextCompressor):
        self.client = client
        self.model = model
        self.system_prompt = system_prompt
        self.session_store = session_store
        self.compressor = compressor
        self.messages: list = []
        self.session_id: str = session_store.new_session_id()

    def run(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        # 压缩检查
        if self.compressor.should_compress(self.messages):
            print("  [compacting context...]")
            self.messages = self.compressor.compress(self.messages)

        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self._build_messages(),
                tools=get_tool_definitions(),
                stream=True,
            )

            assistant_message = self._collect_stream(response)
            self.messages.append(assistant_message)

            if not assistant_message.get("tool_calls"):
                self._auto_save()
                return assistant_message.get("content", "")

            for tool_call in assistant_message["tool_calls"]:
                name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])
                print(f"  → {name}({self._summarize_args(args)})")

                if not check_permission(name, args):
                    result = "User denied this operation."
                else:
                    result = execute_tool(name, args)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": result,
                })

    def _build_messages(self) -> list:
        return [{"role": "system", "content": self.system_prompt}] + self.messages

    def _collect_stream(self, stream) -> dict:
        content_parts = []
        reasoning_parts = []
        tool_calls_map = {}

        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            # DeepSeek 的 reasoning_content（思考过程）
            reasoning = getattr(delta, "reasoning_content", None)
            if reasoning:
                reasoning_parts.append(reasoning)

            if delta.content:
                print(delta.content, end="", flush=True)
                content_parts.append(delta.content)

            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    idx = tc_delta.index
                    if idx not in tool_calls_map:
                        tool_calls_map[idx] = {
                            "id": "",
                            "type": "function",
                            "function": {"name": "", "arguments": ""},
                        }
                    if tc_delta.id:
                        tool_calls_map[idx]["id"] = tc_delta.id
                    if tc_delta.function:
                        if tc_delta.function.name:
                            tool_calls_map[idx]["function"]["name"] += tc_delta.function.name
                        if tc_delta.function.arguments:
                            tool_calls_map[idx]["function"]["arguments"] += tc_delta.function.arguments

        if content_parts:
            print()

        message = {"role": "assistant"}
        content = "".join(content_parts)
        if content:
            message["content"] = content
        if tool_calls_map:
            message["tool_calls"] = [tool_calls_map[i] for i in sorted(tool_calls_map)]
        else:
            message["content"] = content or ""

        # DeepSeek 要求把 reasoning_content 传回
        reasoning = "".join(reasoning_parts)
        if reasoning:
            message["reasoning_content"] = reasoning

        return message

    def _summarize_args(self, args: dict) -> str:
        parts = []
        for k, v in args.items():
            s = str(v)
            if len(s) > 40:
                s = s[:40] + "..."
            parts.append(f"{k}={s}")
        return ", ".join(parts)

    def _auto_save(self):
        self.session_store.save(self.session_id, self.messages)

    def load_session(self, session_id: str):
        self.session_id = session_id
        self.messages = self.session_store.load(session_id)

    def new_session(self):
        self.session_id = self.session_store.new_session_id()
        self.messages = []
