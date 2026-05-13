"""CLI Agent 入口"""

from pathlib import Path
from openai import OpenAI
from config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL
from agent import Agent
from session import SessionStore
from context import ContextCompressor

SLASH_COMMANDS = {
    "/exit": "退出",
    "/clear": "清空当前对话",
    "/save": "保存当前会话",
    "/resume": "恢复最近的会话",
    "/sessions": "列出所有会话",
    "/help": "显示帮助",
}


def handle_slash(command: str, agent: Agent) -> bool:
    """处理斜杠命令。返回 False 表示退出。"""
    if command == "/exit":
        return False
    elif command == "/clear":
        agent.new_session()
        print("  Conversation cleared. New session started.")
    elif command == "/save":
        agent._auto_save()
        print(f"  Saved: {agent.session_id}")
    elif command == "/resume":
        latest = agent.session_store.get_latest()
        if latest:
            agent.load_session(latest)
            print(f"  Resumed: {latest} ({len(agent.messages)} messages)")
        else:
            print("  No sessions found.")
    elif command == "/sessions":
        sessions = agent.session_store.list_sessions()
        if sessions:
            for sid in sessions[:10]:
                print(f"  {sid}")
        else:
            print("  No sessions yet.")
    elif command == "/help":
        for cmd, desc in SLASH_COMMANDS.items():
            print(f"  {cmd:12s} {desc}")
    return True


def main():
    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    system_prompt = Path("prompts/system.md").read_text(encoding="utf-8")
    session_store = SessionStore()
    compressor = ContextCompressor(client, LLM_MODEL)
    agent = Agent(client, LLM_MODEL, system_prompt, session_store, compressor)

    print(f"CLI Agent ready. Session: {agent.session_id}")
    print("Type /help for commands, /exit to quit.\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            if not handle_slash(user_input, agent):
                print("Bye.")
                break
            continue

        agent.run(user_input)
        print()


if __name__ == "__main__":
    main()
