from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class MyFile:
    path: Path
    name: str

@dataclass(frozen=True)
class FileBackup:
    my_file: MyFile
    code: str