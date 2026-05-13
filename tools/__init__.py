"""
Tool Registry — 工具注册与分发
"""

TOOL_REGISTRY = {}


def register_tool(name: str, description: str, parameters: dict, execute_fn):
    TOOL_REGISTRY[name] = {
        "definition": {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
        },
        "execute": execute_fn,
    }


def get_tool_definitions() -> list:
    return [t["definition"] for t in TOOL_REGISTRY.values()]


def execute_tool(name: str, arguments: dict) -> str:
    if name not in TOOL_REGISTRY:
        return f"Error: unknown tool '{name}'"
    try:
        return TOOL_REGISTRY[name]["execute"](**arguments)
    except Exception as e:
        return f"Error executing {name}: {type(e).__name__}: {e}"


def _register_all():
    from tools import read_file
    from tools import run_command

    read_file.register()
    run_command.register()


_register_all()
