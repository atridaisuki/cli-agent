"""glob_files tool — 文件名模式搜索"""

import glob as glob_module
import os
from tools import register_tool


def _execute(pattern: str, path: str = ".") -> str:
    full_pattern = os.path.join(path, pattern)
    matches = sorted(glob_module.glob(full_pattern, recursive=True))
    if not matches:
        return "No files matched"
    if len(matches) > 100:
        matches = matches[:100]
        matches.append("... (truncated at 100)")
    return "\n".join(matches)


def register():
    register_tool(
        name="glob_files",
        description="按 glob 模式搜索文件名（支持 ** 递归）",
        parameters={
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "glob 模式，如 **/*.py、src/**/*.ts",
                },
                "path": {
                    "type": "string",
                    "description": "搜索的起始目录，默认当前目录",
                    "default": ".",
                },
            },
            "required": ["pattern"],
        },
        execute_fn=_execute,
    )
