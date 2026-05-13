"""权限分级 — safe / auto / confirm"""

PERMISSION_LEVELS = {
    "read_file": "safe",
    "grep": "safe",
    "glob_files": "safe",
    "write_file": "auto",
    "edit_file": "auto",
    "run_command": "confirm",
}


def check_permission(tool_name: str, arguments: dict) -> bool:
    level = PERMISSION_LEVELS.get(tool_name, "confirm")

    if level == "safe":
        return True

    if level == "auto":
        print(f"  [{tool_name}] {_summarize(tool_name, arguments)}")
        return True

    if level == "confirm":
        print(f"  [confirm] {_summarize(tool_name, arguments)}")
        answer = input("  Execute? [y/N] ").strip().lower()
        return answer in ("y", "yes")

    return True


def _summarize(tool_name: str, arguments: dict) -> str:
    if tool_name == "run_command":
        return arguments.get("command", "")
    if tool_name == "write_file":
        path = arguments.get("file_path", "?")
        size = len(arguments.get("content", ""))
        return f"write {path} ({size} chars)"
    if tool_name == "edit_file":
        return f"edit {arguments.get('file_path', '?')}"
    return str(arguments)[:80]
