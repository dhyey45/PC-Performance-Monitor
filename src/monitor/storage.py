import time

import psutil

_prev = None


def read() -> dict:
    global _prev
    parts = []
    for p in psutil.disk_partitions(all=False):
        if p.fstype in ("", "squashfs") or "cdrom" in p.opts:
            continue
        try:
            u = psutil.disk_usage(p.mountpoint)
        except OSError:
            continue
        parts.append({"mount": p.mountpoint, "percent": u.percent,
                      "used_gb": u.used / 2**30, "total_gb": u.total / 2**30})
    r = w = 0.0
    io, now = psutil.disk_io_counters(), time.time()
    if io:
        if _prev:
            dt = max(now - _prev[0], 1e-6)
            r = (io.read_bytes - _prev[1]) / dt / 2**20
            w = (io.write_bytes - _prev[2]) / dt / 2**20
        _prev = (now, io.read_bytes, io.write_bytes)
    return {"partitions": parts, "read_mb_s": r, "write_mb_s": w,
            "max_percent": max((p["percent"] for p in parts), default=0.0)}
