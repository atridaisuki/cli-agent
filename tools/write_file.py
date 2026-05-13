"""write_file tool"""

import os
from tools import register_tool


def _execute(file_path: str, content: str) -> str:
    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Written to {file_path} ({len(content)} chars)"
    except Exception as e:
        return f"Error: {e}"


def register():
    register_tool(
        name="write_file",
        description="创建或覆写文件",
        parameters={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要写入的文件路径",
                },
                "content": {
                    "type": "string",
                    "description": "文件内容",
                },
            },
            "required": ["file_path", "content"],
        },
        execute_fn=_execute,
    )
