"""run_command tool"""

import subprocess
from tools import register_tool


def _execute(command: str, timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout + result.stderr
        if len(output) > 5000:
            output = output[:5000] + "\n... (truncated)"
        if result.returncode != 0:
            return f"Exit code {result.returncode}\n{output}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout}s"
    except Exception as e:
        return f"Error: {e}"


def register():
    register_tool(
        name="run_command",
        description="执行 shell 命令并返回输出",
        parameters={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "要执行的 shell 命令",
                },
                "timeout": {
                    "type": "integer",
                    "description": "超时时间（秒），默认 30",
                    "default": 30,
                },
            },
            "required": ["command"],
        },
        execute_fn=_execute,
    )
