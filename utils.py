from pathlib import Path
from models import MyFile, FileBackup
from state import state

from binaryornot.check import is_binary

FILE_LABEL = "File: "


def generate_files_tree() -> set[MyFile]:
    result = set()

    for file in Path.cwd().rglob("*"):
        if file.is_file():
            result.add(MyFile(file, str(file.relative_to(Path.cwd())).replace("\\", "/")))

    return result


def find_file_from_project(search: str) -> set[MyFile]:
    file_tree = generate_files_tree()

    search_names = search.split(" ")

    final_set = set()

    for name in search_names:
        for file in file_tree:
            if file.name == name:
                if is_binary(file.path):
                    print("Sorry, you cannot add media files yet.")
                    continue
                final_set.add(file)

    if not final_set:
        print("No files found")

    return final_set


def save_copy_of_files(response: str):  # on AI EDIT
    state.redo_stack.clear()

    find_starts = response.split(FILE_LABEL)
    files_to_save = set([file[:file.find("\n")] for file in find_starts])

    backups = set()
    for my_file in state.files_context:
        if my_file.name in files_to_save:
            try:
                with open(my_file.path, "r", encoding="UTF-8", newline="") as f:
                    backups.add(FileBackup(my_file, f.read()))
            except (OSError, UnicodeDecodeError):
                continue

    if backups:
        state.undo_stack.append(backups)


def _snapshot(backups: set[FileBackup]) -> set[FileBackup]:
    snap = set()
    for b in backups:
        try:
            with open(b.my_file.path, "r", encoding="UTF-8", newline="") as f:
                snap.add(FileBackup(b.my_file, f.read()))
        except FileNotFoundError:
            pass
    return snap


def _restore(backups: set[FileBackup]) -> None:
    for b in backups:

        if not b.my_file.path.exists():
            continue

        with open(b.my_file.path, "w", encoding="UTF-8", newline="") as f:
            f.write(b.code)


def undo_files() -> None:
    if not state.undo_stack:
        print("Nothing to undo")
        return
    backups = state.undo_stack.pop()
    state.redo_stack.append(_snapshot(backups))
    _restore(backups)


def redo_files() -> None:
    if not state.redo_stack:
        print("Nothing to redo")
        return
    backups = state.redo_stack.pop()
    state.undo_stack.append(_snapshot(backups))
    _restore(backups)



def check_if_first_start():
    fp = Path(__file__).resolve().parent / "first_start"

    if fp.exists():
        fp.unlink()
        return True
    else:
        return False
