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


def _safe_float(value, default=None):
    if value is None:
        return default
    try:
        n = float(value)
    except (TypeError, ValueError):
        return default
    if n != n or n in (float("inf"), float("-inf")):
        return default
    return n


class AlertManager:
    def __init__(self, thresholds: Thresholds | None = None, cooldown: float = 60.0):
        self.t = thresholds or Thresholds()
        self.cooldown = cooldown
        self.log: deque[Alert] = deque(maxlen=200)
        self._last: dict[str, float] = {}

    def check(self, snap) -> list[Alert]:
        t = self.t
        cpu = getattr(snap, "cpu", {}) or {}
        memory = getattr(snap, "memory", {}) or {}
        gpu = getattr(snap, "gpu", None) or {}
        temps = getattr(snap, "temps", {}) or {}
        storage = getattr(snap, "storage", {}) or {}

        temps_list = [
            _safe_float(v)
            for v in temps.values()
            if _safe_float(v) is not None
        ]
        readings = [
            ("CPU", _safe_float(cpu.get("percent")), t.cpu, "%"),
            ("RAM", _safe_float(memory.get("percent")), t.ram, "%"),
            ("GPU", _safe_float(gpu.get("util")) if gpu else None, t.gpu, "%"),
            ("Temperature", max(temps_list) if temps_list else None, t.temp, "°C"),
            ("Storage", _safe_float(storage.get("max_percent")), t.disk, "%"),
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
