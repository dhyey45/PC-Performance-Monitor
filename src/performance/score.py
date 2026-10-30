import math

WEIGHTS = {"cpu": 0.30, "ram": 0.25, "gpu": 0.15, "temp": 0.15, "disk": 0.15}


def _coerce_percent(value, default=0.0) -> float:
    """Normalize sensor values to a safe 0..100 range."""
    if value is None:
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(number):
        return default
    return max(0.0, min(100.0, number))


def _headroom(value: float, good: float, bad: float) -> float:
    """100 when value <= good, 0 when value >= bad, linear in between."""
    value = _coerce_percent(value)
    if bad <= good:
        return 0.0
    return max(0.0, min(100.0, 100.0 * (bad - value) / (bad - good)))


def compute_score(snap) -> tuple[int, dict]:
    """Return (0-100 score, per-component sub-scores). Missing sensors are skipped."""
    cpu = getattr(snap, "cpu", {}) or {}
    memory = getattr(snap, "memory", {}) or {}
    storage = getattr(snap, "storage", {}) or {}
    gpu = getattr(snap, "gpu", None)
    temps = getattr(snap, "temps", {}) or {}

    parts = {
        "cpu": _headroom(cpu.get("percent"), 50, 100),
        "ram": _headroom(memory.get("percent"), 60, 100),
        "disk": _headroom(storage.get("max_percent"), 70, 100),
    }
    if gpu:
        parts["gpu"] = _headroom(gpu.get("util"), 60, 100)
    sensor_temps = [float(v) for v in temps.values() if v is not None]
    if sensor_temps:
        parts["temp"] = _headroom(max(sensor_temps), 60, 95)

    total = sum(WEIGHTS[k] for k in parts)
    if not total:
        return 0, {}
    score = sum(WEIGHTS[k] * v for k, v in parts.items()) / total
    return round(score), parts


def grade(score: float) -> str:
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 55:
        return "Fair"
    return "Needs Attention"
