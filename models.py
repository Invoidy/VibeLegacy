from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class MyFile:
    path: Path
    name: str