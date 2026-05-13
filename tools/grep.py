"""grep tool — 内容搜索"""

import os
import re
from tools import register_tool

SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".idea", "venv"}


def _execute(pattern: str, path: str = ".", file_type: str = None) -> str:
    results = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            if file_type and not fname.endswith(file_type):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        if re.search(pattern, line):
                            results.append(f"{fpath}:{i}: {line.rstrip()}")
            except (OSError, IOError):
                continue
            if len(results) > 50:
                results.append("... (truncated at 50 matches)")
                return "\n".join(results)
    return "\n".join(results) if results else "No matches found"


def register():
    register_tool(
        name="grep",
        description="在文件中搜索匹配正则表达式的内容",
        parameters={
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "正则表达式搜索模式",
                },
                "path": {
                    "type": "string",
                    "description": "搜索的起始目录，默认当前目录",
                    "default": ".",
                },
                "file_type": {
                    "type": "string",
                    "description": "按文件后缀过滤，如 .py .ts .js",
                },
            },
            "required": ["pattern"],
        },
        execute_fn=_execute,
    )
