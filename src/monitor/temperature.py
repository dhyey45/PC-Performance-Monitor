import psutil

_CPU_SENSORS = ("coretemp", "k10temp", "zenpower", "cpu_thermal", "acpitz")


def read(gpu_info=None) -> dict:
    """CPU temp comes from psutil (Linux/FreeBSD only); GPU temp comes from NVML."""
    cpu_t = None
    try:
        sensors = psutil.sensors_temperatures()
    except Exception:
        sensors = {}
    for key in _CPU_SENSORS:
        if sensors.get(key):
            cpu_t = max(s.current for s in sensors[key])
            break
    return {"cpu": cpu_t, "gpu": gpu_info["temp_c"] if gpu_info else None}
