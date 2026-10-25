from dataclasses import dataclass, field

from models import MyFile, FileBackup


@dataclass
class State:
    _files_context: set[MyFile] = field(default_factory=set)
    is_code_generating: bool = False
    chat_history: list[dict] = field(default_factory=list)

    undo_stack: list[set[FileBackup]] = field(default_factory=list)
    redo_stack: list[set[FileBackup]] = field(default_factory=list)

    @property
    def files_context(self) -> set[MyFile]:
        new_files_context = set([myfile for myfile in self._files_context if myfile.path.exists()])
        self._files_context = new_files_context
        return self._files_context

    @files_context.setter
    def files_context(self, value):
        self._files_context = value


state: State = State()