import time
from pathlib import Path
import shutil
from time import sleep

from response_parser import do_changes
from state import state
from utils import undo_files, redo_files, update_last_change_code_save
from models import MyFile

import pytest

def do_changes_test(full_output: str):
    status = do_changes(full_output)
    if status.files_backups:
        state.undo_stack.append(status.files_backups)
        state.redo_stack.clear()
    update_last_change_code_save(status.success_files)
    return status

@pytest.fixture
def input_calls(monkeypatch):
    calls = []

    def confirm(prompt=""):
        calls.append(prompt)
        return "Y"

    monkeypatch.setattr("builtins.input", confirm)
    return calls

test_dir = Path(__file__).resolve().parent
polygon_folder = test_dir / "polygon"

state.files_context.update({MyFile(path=polygon_folder / "somefile.py", name="somefile.py"),
                            MyFile(path=polygon_folder / "another.py", name="another.py")})



ANSWER_somefile = """
There is your code <3
File: somefile.py
```
<<<<<<< SEARCH
def pls_refactor_me():
    print("=(")
=======
def i_am_ready():
    print("=)")
>>>>>>> REPLACE
```
"""

ANSWER_another = """
File: another.py
```
<<<<<<< SEARCH
time.sleep(0.02)
=======
time.sleep(0.01)
>>>>>>> REPLACE
``` 
"""

def recreate_polygon():

    state.undo_stack.clear()
    state.redo_stack.clear()

    if polygon_folder.exists():
        shutil.rmtree(polygon_folder)

    polygon_folder.mkdir()

    with open(polygon_folder / "somefile.py", "w+") as f:
        f.write("""def some_func():
    print("yay")

def some_func2():
    print("yay2")

def pls_refactor_me():
    print("=(")
""")
    with open(polygon_folder / "another.py", "w+") as f:
            f.write("""import sys
import time

print("Starting system:")
for i in range(101):
    sys.stdout.write(f"\\rProgress: [{i}%]")
    sys.stdout.flush()
    time.sleep(0.02)
print("\\nTest successful passed!")
""")

def edit_manually_somefile_file():
    with open(polygon_folder / "somefile.py", "w+") as f:
        f.write("edited")


def test_redo_warns_after_manual_edit(input_calls):
    recreate_polygon()

    do_changes_test(ANSWER_somefile)
    undo_files()
    assert input_calls == []

    edit_manually_somefile_file()

    redo_files()

    assert len(input_calls) == 1


def test_undo_warns_after_manual_edit(input_calls):
    recreate_polygon()

    do_changes_test(ANSWER_somefile)
    assert input_calls == []

    edit_manually_somefile_file()

    undo_files()

    assert len(input_calls) == 1

    redo_files()

    assert len(input_calls) == 1


def test_undo_redo_without_manual_edits_does_not_warn(input_calls):
    recreate_polygon()

    do_changes_test(ANSWER_somefile)
    assert input_calls == []

    undo_files()
    assert input_calls == []

    redo_files()
    assert input_calls == []

def test_two_edits_then_undo_undo(input_calls):
    recreate_polygon()

    do_changes_test(ANSWER_somefile)
    do_changes_test(ANSWER_another)

    edit_manually_somefile_file()

    undo_files()
    assert input_calls == []

    undo_files()
    assert len(input_calls) == 1