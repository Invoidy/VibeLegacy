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


def _snapshot(backups: set[FileBackup]) -> set[FileBackup]:
    snap = set()
    for b in backups:
        try:
            with open(b.my_file.path, "r", encoding="UTF-8") as f:
                snap.add(FileBackup(b.my_file, f.read()))
        except FileNotFoundError:
            pass
    return snap


def _restore(backups: set[FileBackup]) -> None:
    for b in backups:

        if not b.my_file.path.exists():
            continue

        with open(b.my_file.path, "w", encoding="UTF-8") as f:
            f.write(b.code)

def _show_warning(backups: set[FileBackup]) -> bool:
    manually_changed = set()

    for b in backups:
        if not b.my_file.path.exists():
            continue

        with open(b.my_file.path, "r", encoding="UTF-8") as f:
            current = f.read()

        for element in state.last_change_code_save:
            if element.my_file.name == b.my_file.name and current != element.code:
                manually_changed.add(b)
                break

    if manually_changed:
        while True:
            names = " ".join(m.my_file.name for m in manually_changed)
            action = input(f"{names} were edited manually. \nProceeding will erase your manual changes in it. Continue? [y/N]:")

            if action in ["", "n", "N"]:
                return True
            elif action in ["y", "Y"]:
                return False
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
    update_last_change_code_save(set([b.my_file for b in backups]))


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
    update_last_change_code_save(set([b.my_file for b in backups]))

def update_last_change_code_save(backups: set[MyFile]) -> None:
    backups = set([b for b in backups if b.path.exists()])

    elements_to_add = set()
    elements_to_remove = set()

    for b in backups:
        for element in state.last_change_code_save:
            if b.name == element.my_file.name:
                elements_to_remove.add(element)

        with open(b.path, "r", encoding="UTF-8") as f:
            elements_to_add.add(FileBackup(b, f.read()))

    state.last_change_code_save -= elements_to_remove
    state.last_change_code_save |= elements_to_add


def check_if_first_start():
    fp = Path(__file__).resolve().parent / "first_start"

    if fp.exists():
        fp.unlink()
        return True
    else:
        return False
