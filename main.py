"""CLI Agent 入口"""

from pathlib import Path
from openai import OpenAI
from config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL
from agent import Agent
from session import SessionStore
from context import ContextCompressor
from skills import SkillManager

SLASH_COMMANDS = {
    "/exit": "退出",
    "/clear": "清空当前对话",
    "/save": "保存当前会话",
    "/resume": "恢复最近的会话",
    "/sessions": "列出所有会话",
    "/skills": "列出可用 Skills",
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


def handle_skill(skill_name: str, args: str, agent: Agent, skill_manager: SkillManager):
    """调用 Skill"""
    skill = skill_manager.get_skill(skill_name)
    if not skill:
        print(f"  Unknown skill: {skill_name}")
        return

    script = skill_manager.find_script(skill)
    if script:
        command = f"python {script} --log-dir data/sessions {args}".strip()
        agent.run(f"执行命令并展示结果: {command}")
    else:
        original_prompt = agent.system_prompt
        agent.system_prompt = original_prompt + f"\n\n---\n# Active Skill: {skill['name']}\n{skill['content']}"
        agent.run(args or f"Execute the {skill_name} skill")
        agent.system_prompt = original_prompt


def main():
    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    system_prompt = Path("prompts/system.md").read_text(encoding="utf-8")
    session_store = SessionStore()
    compressor = ContextCompressor(client, LLM_MODEL)
    agent = Agent(client, LLM_MODEL, system_prompt, session_store, compressor)

    skill_manager = SkillManager()
    skill_manager.load_all()

    print(f"CLI Agent ready. Session: {agent.session_id}")
    skills_count = len(skill_manager.skills)
    if skills_count:
        print(f"Loaded {skills_count} skill(s).")
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
            parts = user_input[1:].split(None, 1)
            cmd_name = parts[0]
            cmd_args = parts[1] if len(parts) > 1 else ""

            if f"/{cmd_name}" in SLASH_COMMANDS:
                if cmd_name == "skills":
                    skills_list = skill_manager.list_skills()
                    if skills_list:
                        for s in skills_list:
                            hint = f" {s['hint']}" if s['hint'] else ""
                            print(f"  /{s['name']}{hint} — {s['description']}")
                    else:
                        print("  No skills loaded.")
                elif not handle_slash(f"/{cmd_name}", agent):
                    print("Bye.")
                    break
                continue

            if skill_manager.get_skill(cmd_name):
                handle_skill(cmd_name, cmd_args, agent, skill_manager)
                print()
                continue

            print(f"  Unknown command: /{cmd_name}")
            continue

        agent.run(user_input)
        print()


if __name__ == "__main__":
    main()
