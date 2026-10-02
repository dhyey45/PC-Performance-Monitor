import psutil


def top_processes(n: int = 15, sort_by: str = "cpu") -> list[dict]:
    """Top processes by CPU (normalised to 0-100% of the whole machine) or memory."""
    cores = psutil.cpu_count() or 1
    rows = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
        i = p.info
        rows.append({
            "pid": i["pid"],
            "name": i["name"] or "?",
            "cpu": (i["cpu_percent"] or 0.0) / cores,
            "mem_mb": i["memory_info"].rss / 2**20 if i["memory_info"] else 0.0,
        })
    rows.sort(key=lambda r: r["cpu" if sort_by == "cpu" else "mem_mb"], reverse=True)
    return rows[:n]
