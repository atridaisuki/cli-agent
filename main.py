"""CLI Agent 入口"""

from pathlib import Path
from openai import OpenAI
from config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL
from agent import Agent


def main():
    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    system_prompt = Path("prompts/system.md").read_text(encoding="utf-8")
    agent = Agent(client, LLM_MODEL, system_prompt)

    print("CLI Agent ready. Type /exit to quit.\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not user_input:
            continue
        if user_input == "/exit":
            print("Bye.")
            break

        agent.run(user_input)
        print()


if __name__ == "__main__":
    main()
