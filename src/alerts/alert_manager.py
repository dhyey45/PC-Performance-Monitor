import time
from collections import deque
from dataclasses import dataclass


@dataclass
class Thresholds:
    cpu: float = 90.0
    ram: float = 90.0
    gpu: float = 95.0
    temp: float = 85.0
    disk: float = 90.0


@dataclass
class Alert:
    ts: float
    level: str  # "warning" | "critical"
    metric: str
    message: str


class AlertManager:
    def __init__(self, thresholds: Thresholds | None = None, cooldown: float = 60.0):
        self.t = thresholds or Thresholds()
        self.cooldown = cooldown
        self.log: deque[Alert] = deque(maxlen=200)
        self._last: dict[str, float] = {}

    def check(self, snap) -> list[Alert]:
        t = self.t
        temps = [v for v in snap.temps.values() if v is not None]
        readings = [
            ("CPU", snap.cpu["percent"], t.cpu, "%"),
            ("RAM", snap.memory["percent"], t.ram, "%"),
            ("GPU", snap.gpu["util"] if snap.gpu else None, t.gpu, "%"),
            ("Temperature", max(temps) if temps else None, t.temp, "°C"),
            ("Storage", snap.storage["max_percent"], t.disk, "%"),
        ]
        now, fired = time.time(), []
        for name, value, limit, unit in readings:
            if value is None or value < limit or now - self._last.get(name, 0) < self.cooldown:
                continue
            self._last[name] = now
            level = "critical" if value >= limit + 5 else "warning"
            alert = Alert(now, level, name, f"{name} at {value:.0f}{unit} (limit {limit:.0f}{unit})")
            fired.append(alert)
            self.log.appendleft(alert)
        return fired
