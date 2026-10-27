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

def _show_warning(backups: set[FileBackup]) -> bool:
    manually_changed = set()

    for snap in _snapshot(backups):
        if not snap in state.last_change_code_save:
            manually_changed.add(snap)

    if manually_changed:
        action = input(f"{" ".join([m.my_file.name for m in manually_changed])} were edited manually. \nProceeding will erase your manual changes in it. Continue? [y/N]:")

        if action in ["", "n", "N"]:
            return True
        elif action in ["y", "Y"]:
            return False
        else:
            print("Wrong input. Try again.")
    return False

def undo_files() -> None:
    if not state.undo_stack:
        print("Nothing to undo")
        return
    backups = state.undo_stack[-1]

    is_cancel = _show_warning(backups)
    if is_cancel:
        print("Canceled")
        return

    state.undo_stack.pop()
    state.redo_stack.append(_snapshot(backups))
    _restore(backups)
    print("Changes discarded. Use /redo to restore them.")
    backup_files(backups)


def redo_files() -> None:
    if not state.redo_stack:
        print("Nothing to redo")
        return
    backups = state.redo_stack[-1]

    is_cancel = _show_warning(backups)
    if is_cancel:
        print("Canceled")
        return

    state.redo_stack.pop()
    state.undo_stack.append(_snapshot(backups))
    _restore(backups)
    print("Changes restored. Use /undo to discard them.")
    backup_files(backups)


def backup_files(backups: set[FileBackup]) -> None:
    state.last_change_code_save = _snapshot(backups)


def check_if_first_start():
    fp = Path(__file__).resolve().parent / "first_start"

    if fp.exists():
        fp.unlink()
        return True
    else:
        return False
