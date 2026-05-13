"""Session Store — JSONL 会话持久化（原子写入）"""

import json
from pathlib import Path
from datetime import datetime


class SessionStore:
    def __init__(self, sessions_dir: str = "data/sessions"):
        self.dir = Path(sessions_dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def save(self, session_id: str, messages: list):
        path = self.dir / f"{session_id}.jsonl"
        tmp_path = path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            for msg in messages:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")
        tmp_path.replace(path)

    def load(self, session_id: str) -> list:
        path = self.dir / f"{session_id}.jsonl"
        if not path.exists():
            return []
        messages = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    messages.append(json.loads(line))
        return messages

    def list_sessions(self) -> list:
        files = sorted(self.dir.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)
        return [f.stem for f in files]

    def get_latest(self) -> str | None:
        sessions = self.list_sessions()
        return sessions[0] if sessions else None

    def new_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
