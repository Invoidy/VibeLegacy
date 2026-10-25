from dataclasses import dataclass, field

from models import MyFile, FileBackup


@dataclass
class State:
    files_context: set[MyFile] = field(default_factory=set)
    is_code_generating: bool = False
    chat_history: list[dict] = field(default_factory=list)

    undo_stack: list[set[FileBackup]] = field(default_factory=list)
    redo_stack: list[set[FileBackup]] = field(default_factory=list)

state: State = State()