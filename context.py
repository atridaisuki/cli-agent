"""Context Manager — token 估算 + LLM 摘要压缩"""

import re
import json
from openai import OpenAI

CJK_PATTERN = re.compile(r'[一-鿿㐀-䶿]')


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    cjk_chars = len(CJK_PATTERN.findall(text))
    other_chars = len(text) - cjk_chars
    return int(cjk_chars / 1.5 + other_chars / 4)


def estimate_messages_tokens(messages: list) -> int:
    total = 0
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            total += estimate_tokens(content)
        elif isinstance(content, list):
            for part in content:
                total += estimate_tokens(str(part))
        if msg.get("tool_calls"):
            total += estimate_tokens(json.dumps(msg["tool_calls"]))
        if msg.get("reasoning_content"):
            total += estimate_tokens(msg["reasoning_content"])
    return total


class ContextCompressor:
    def __init__(self, client: OpenAI, model: str, max_budget: int = 120000):
        self.client = client
        self.model = model
        self.max_budget = max_budget
        self.compress_threshold = 0.6

    def should_compress(self, messages: list) -> bool:
        tokens = estimate_messages_tokens(messages)
        return tokens > self.max_budget * self.compress_threshold

    def compress(self, messages: list) -> list:
        if len(messages) <= 6:
            return messages

        recent = messages[-6:]
        old = messages[:-6]

        summary = self._summarize(old)

        return [
            {"role": "user", "content": f"[Previous conversation summary]\n{summary}"},
            {"role": "assistant", "content": "Understood, I have the context from our previous conversation."},
            *recent,
        ]

    def _summarize(self, messages: list) -> str:
        conversation_text = self._messages_to_text(messages)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Summarize this conversation concisely. "
                        "Keep: file paths mentioned, changes made, current task status, key decisions. "
                        "Drop: tool call details, intermediate exploration, reasoning process. "
                        "Output in the same language as the conversation."
                    ),
                },
                {"role": "user", "content": conversation_text},
            ],
            max_tokens=1000,
        )
        return response.choices[0].message.content

    def _messages_to_text(self, messages: list) -> str:
        parts = []
        for msg in messages:
            role = msg.get("role", "?")
            content = msg.get("content", "")
            if isinstance(content, str) and content:
                parts.append(f"[{role}] {content[:500]}")
            if msg.get("tool_calls"):
                for tc in msg["tool_calls"]:
                    name = tc.get("function", {}).get("name", "?")
                    parts.append(f"[tool_call] {name}")
        return "\n".join(parts)
