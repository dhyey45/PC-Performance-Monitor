import pytest

from src.monitor.snapshot import Snapshot


@pytest.fixture
def make_snapshot():
    def _make(cpu=10, ram=30, gpu=None, temp=45, disk=40):
        return Snapshot(
            ts=0.0,
            cpu={"percent": cpu, "per_core": [cpu], "cores": 4, "threads": 8, "freq_mhz": 3000},
            memory={"percent": ram, "used_gb": 4, "total_gb": 16, "swap_percent": 0},
            gpu={"util": gpu, "temp_c": None} if gpu is not None else None,
            temps={"cpu": temp, "gpu": None},
            storage={"max_percent": disk, "partitions": [], "read_mb_s": 0, "write_mb_s": 0},
        )
    return _make
