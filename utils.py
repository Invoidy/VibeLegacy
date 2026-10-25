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

    final_set = set()

    for myFile in state.files_context:
        if myFile.name in files_to_save:
            with open(myFile.path, "r", encoding="UTF-8") as f:
                final_set.add(FileBackup(myFile, f.read()))

    if final_set:
        state.undo_stack.append(final_set)


def undo_files():  # UNDO
    if not state.undo_stack:
        print("Nothing to undo")
        return

    append_redo_stack()

    for fileBackup in state.undo_stack[-1]:
        with open(fileBackup.my_file.path, "w+", encoding="UTF-8") as f:
            f.write(fileBackup.code)

    state.undo_stack.pop()


def append_redo_stack():
    final_set = set()

    for fileBackup in state.undo_stack[-1]:
        try:
            with open(fileBackup.my_file.path, "r", encoding="UTF-8") as f:
                final_set.add(FileBackup(fileBackup.my_file, f.read()))
        except FileNotFoundError:
            pass

    state.redo_stack.append(final_set)

def redo_files():  # REDO
    if not state.redo_stack:
        print("Nothing to redo")
        return

    append_undo_stack()

    for fileBackup in state.redo_stack[-1]:
        with open(fileBackup.my_file.path, "w+", encoding="UTF-8") as f:
            f.write(fileBackup.code)

    state.redo_stack.pop()

def append_undo_stack():
    final_set = set()

    for fileBackup in state.redo_stack[-1]:
        try:
            with open(fileBackup.my_file.path, "r", encoding="UTF-8") as f:
                final_set.add(FileBackup(fileBackup.my_file, f.read()))
        except FileNotFoundError:
            pass

    state.undo_stack.append(final_set)



def check_if_first_start():
    fp = Path(__file__).resolve().parent / "first_start"

    if fp.exists():
        fp.unlink()
        return True
    else:
        return False
