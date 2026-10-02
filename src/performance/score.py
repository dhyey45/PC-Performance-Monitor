WEIGHTS = {"cpu": 0.30, "ram": 0.25, "gpu": 0.15, "temp": 0.15, "disk": 0.15}


def _headroom(value: float, good: float, bad: float) -> float:
    """100 when value <= good, 0 when value >= bad, linear in between."""
    return max(0.0, min(100.0, 100.0 * (bad - value) / (bad - good)))


def compute_score(snap) -> tuple[int, dict]:
    """Return (0-100 score, per-component sub-scores). Missing sensors are skipped."""
    parts = {
        "cpu": _headroom(snap.cpu["percent"], 50, 100),
        "ram": _headroom(snap.memory["percent"], 60, 100),
        "disk": _headroom(snap.storage["max_percent"], 70, 100),
    }
    if snap.gpu:
        parts["gpu"] = _headroom(snap.gpu["util"], 60, 100)
    temps = [v for v in snap.temps.values() if v is not None]
    if temps:
        parts["temp"] = _headroom(max(temps), 60, 95)
    total = sum(WEIGHTS[k] for k in parts)
    score = sum(WEIGHTS[k] * v for k, v in parts.items()) / total
    return round(score), parts


def grade(score: float) -> str:
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 55:
        return "Fair"
    return "Needs attention"
