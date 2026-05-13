"""edit_file tool — 字符串替换编辑"""

from tools import register_tool


def _execute(file_path: str, old_string: str, new_string: str) -> str:
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return f"Error: file not found: {file_path}"
    except Exception as e:
        return f"Error reading file: {e}"

    count = content.count(old_string)
    if count == 0:
        return f"Error: old_string not found in {file_path}"
    if count > 1:
        return f"Error: old_string matches {count} times, must be unique. Provide more context."

    new_content = content.replace(old_string, new_string, 1)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return f"Edited {file_path}: replaced 1 occurrence"


def register():
    register_tool(
        name="edit_file",
        description="通过字符串替换编辑文件。old_string 必须在文件中唯一匹配",
        parameters={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要编辑的文件路径",
                },
                "old_string": {
                    "type": "string",
                    "description": "要被替换的原始字符串（必须唯一）",
                },
                "new_string": {
                    "type": "string",
                    "description": "替换后的新字符串",
                },
            },
            "required": ["file_path", "old_string", "new_string"],
        },
        execute_fn=_execute,
    )
