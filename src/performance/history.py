import sqlite3
import time
from pathlib import Path

DB_PATH = Path.home() / ".pc-performance-monitor" / "history.db"


class History:
    """Persists a sample every `every` seconds to SQLite so history survives restarts."""

    def __init__(self, path: Path = DB_PATH, every: float = 10.0):
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.execute("CREATE TABLE IF NOT EXISTS samples "
                        "(ts REAL, cpu REAL, ram REAL, gpu REAL, temp REAL, score REAL)")
        self.every, self._last = every, 0.0

    def record(self, snap, score: float) -> None:
        if snap.ts - self._last < self.every:
            return
        self._last = snap.ts
        temps = [v for v in snap.temps.values() if v is not None]
        self.db.execute("INSERT INTO samples VALUES (?,?,?,?,?,?)", (
            snap.ts, snap.cpu["percent"], snap.memory["percent"],
            snap.gpu["util"] if snap.gpu else None, max(temps) if temps else None, score))
        self.db.commit()

    def recent_scores(self, minutes: int = 60) -> list[float]:
        rows = self.db.execute("SELECT score FROM samples WHERE ts > ? ORDER BY ts",
                               (time.time() - minutes * 60,)).fetchall()
        return [r[0] for r in rows]

    def summary(self, hours: int = 24) -> dict:
        row = self.db.execute("SELECT AVG(score), MIN(score), MAX(score), AVG(cpu), AVG(ram), COUNT(*) "
                              "FROM samples WHERE ts > ?", (time.time() - hours * 3600,)).fetchone()
        keys = ("avg_score", "min_score", "max_score", "avg_cpu", "avg_ram", "samples")
        return {k: (v or 0) for k, v in zip(keys, row)}
