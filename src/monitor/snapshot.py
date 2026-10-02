from dataclasses import dataclass
from typing import Optional


@dataclass
class Snapshot:
    ts: float
    cpu: dict
    memory: dict
    gpu: Optional[dict]
    temps: dict
    storage: dict
