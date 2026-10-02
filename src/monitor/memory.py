import psutil


def read() -> dict:
    vm, sw = psutil.virtual_memory(), psutil.swap_memory()
    return {
        "percent": vm.percent,
        "used_gb": vm.used / 2**30,
        "total_gb": vm.total / 2**30,
        "swap_percent": sw.percent,
    }
