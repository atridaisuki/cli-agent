"""read_file tool"""

from tools import register_tool


def _execute(file_path: str) -> str:
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        if len(content) > 10000:
            return content[:10000] + f"\n... (truncated, total {len(content)} chars)"
        return content
    except FileNotFoundError:
        return f"Error: file not found: {file_path}"
    except Exception as e:
        return f"Error reading file: {e}"


def register():
    register_tool(
        name="read_file",
        description="读取指定路径的文件内容",
        parameters={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要读取的文件绝对路径或相对路径",
                }
            },
            "required": ["file_path"],
        },
        execute_fn=_execute,
    )
