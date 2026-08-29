from dataclasses import dataclass, field

from utils import MyFile


@dataclass
class State:
    files_context: set[MyFile] = field(default_factory=set)
    is_code_generating: bool = False
    chat_history: list[dict] = field(default_factory=list)

    unedited_added_files: dict[str, str] = field(default_factory=dict)

state: State = State()