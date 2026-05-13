"""Skill Manager — 扫描 skills/ 目录，加载 SKILL.md"""

from pathlib import Path
from typing import Optional


class SkillManager:
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = Path(skills_dir)
        self.skills: dict = {}

    def load_all(self):
        if not self.skills_dir.exists():
            return
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                skill = self._parse(skill_file)
                if skill:
                    self.skills[skill["name"]] = skill

    def _parse(self, path: Path) -> Optional[dict]:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            return None
        parts = text.split("---", 2)
        if len(parts) < 3:
            return None

        meta = self._parse_yaml_simple(parts[1])
        if not meta:
            return None

        content = parts[2].strip()
        return {
            "name": meta.get("name", path.parent.name),
            "description": meta.get("description", ""),
            "invocable": meta.get("invocable", "both"),
            "argument_hint": meta.get("argument-hint", ""),
            "content": content,
            "dir": path.parent,
        }

    def _parse_yaml_simple(self, text: str) -> Optional[dict]:
        """简易 YAML 解析，不依赖 pyyaml"""
        result = {}
        for line in text.strip().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                result[key] = value
        return result if result else None

    def get_skill(self, name: str) -> Optional[dict]:
        return self.skills.get(name)

    def list_skills(self) -> list:
        return [
            {"name": s["name"], "description": s["description"], "hint": s["argument_hint"]}
            for s in self.skills.values()
            if s["invocable"] in ("both", "user")
        ]

    def find_script(self, skill: dict) -> Optional[str]:
        """查找 Skill 目录下的可执行脚本"""
        skill_dir = skill["dir"]
        for ext in (".py", ".sh", ".ts"):
            candidates = list(skill_dir.glob(f"*{ext}"))
            if candidates:
                return str(candidates[0])
        return None
