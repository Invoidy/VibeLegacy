from pathlib import Path
from models import MyFile
from state import state


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
                final_set.add(file)

    if not final_set:
        print("No files found")

    return final_set

def save_copy_of_files():
    for myFile in state.files_context:
        with open(myFile.path, "r", encoding="UTF-8") as f:
            file_content = f.read()
            state.unedited_added_files[myFile.name] = file_content
def undo_files():
    for myFile in state.files_context:
        if myFile.name in state.unedited_added_files:
            with open(myFile.path, "w", encoding="UTF-8") as f:
                f.write(state.unedited_added_files[myFile.name])

def check_if_first_start():
    fp = Path(__file__).resolve().parent / "first_start"

    if fp.exists():
        fp.unlink()
        return True
    else:
        return False
