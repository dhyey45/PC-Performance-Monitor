import time

from . import cpu, gpu, memory, storage, temperature
from .snapshot import Snapshot


def collect() -> Snapshot:
    g = gpu.read()
    return Snapshot(time.time(), cpu.read(), memory.read(), g, temperature.read(g), storage.read())
