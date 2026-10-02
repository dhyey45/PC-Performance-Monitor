"""NVIDIA GPU stats via NVML. Returns None when no supported GPU is present."""
try:
    import pynvml

    pynvml.nvmlInit()
    _HANDLE = pynvml.nvmlDeviceGetHandleByIndex(0)
except Exception:  # no driver / no NVIDIA GPU / package missing
    pynvml = None
    _HANDLE = None


def read():
    if _HANDLE is None:
        return None
    try:
        util = pynvml.nvmlDeviceGetUtilizationRates(_HANDLE)
        mem = pynvml.nvmlDeviceGetMemoryInfo(_HANDLE)
        name = pynvml.nvmlDeviceGetName(_HANDLE)
        return {
            "name": name.decode() if isinstance(name, bytes) else name,
            "util": float(util.gpu),
            "mem_used_gb": mem.used / 2**30,
            "mem_total_gb": mem.total / 2**30,
            "temp_c": float(pynvml.nvmlDeviceGetTemperature(_HANDLE, pynvml.NVML_TEMPERATURE_GPU)),
        }
    except Exception:
        return None
