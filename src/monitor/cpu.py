import psutil


def read() -> dict:
    per_core = psutil.cpu_percent(interval=None, percpu=True)
    freq = psutil.cpu_freq()
    return {
        "percent": sum(per_core) / len(per_core) if per_core else 0.0,
        "per_core": per_core,
        "cores": psutil.cpu_count(logical=False) or psutil.cpu_count(),
        "threads": psutil.cpu_count(),
        "freq_mhz": freq.current if freq else None,
    }
