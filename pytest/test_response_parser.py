from pathlib import Path
import shutil

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

@pytest.fixture(autouse=True)
def always_yes(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "Y")

test_dir = Path(__file__).resolve().parent
polygon_folder = test_dir / "polygon"

state.files_context.update({MyFile(path=polygon_folder / "somefile.py", name="somefile.py"),
                            MyFile(path=polygon_folder / "another.py", name="another.py")})

SOMEFILE_ORIGINAL = """def some_func():
    print("yay")

def some_func2():
    print("yay2")

def pls_refactor_me():
    print("=(")
"""

SOMEFILE_AFTER_AI = """def some_func():
    print("yay")

def some_func2():
    print("yay2")

def i_am_ready():
    print("=)")
"""

SOMEFILE_AFTER_AI_2 = """def some_func():
    print("yay")

def some_func2():
    print("yay2")

def i_am_done():
    print("=D")
"""

ANOTHER_ORIGINAL = """import sys
import time

print("Starting system:")
for i in range(101):
    sys.stdout.write(f"\\rProgress: [{i}%]")
    sys.stdout.flush()
    time.sleep(0.02)
print("\\nTest successful passed!")
"""

ANOTHER_AFTER_AI = """import sys
import time

print("Starting system:")
for i in range(101):
    sys.stdout.write(f"\\rProgress: [{i}%]")
    sys.stdout.flush()
    time.sleep(0.01)
print("\\nTest successful passed!")
"""

ANSWER_STEP_1 = """
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

ANSWER_STEP_2 = """
There is your code <3
File: somefile.py
```
<<<<<<< SEARCH
def i_am_ready():
    print("=)")
=======
def i_am_done():
    print("=D")
>>>>>>> REPLACE
```
"""

ANSWER_TWO_FILES = """
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

Also i made next optimizations as tip

File: another.py
```
<<<<<<< SEARCH
time.sleep(0.02)
=======
time.sleep(0.01)
>>>>>>> REPLACE
```
"""

ANSWER_OTHER_BRANCH = """
There is your code <3
File: somefile.py
```
<<<<<<< SEARCH
def pls_refactor_me():
    print("=(")
=======
def i_am_different():
    print(":D")
>>>>>>> REPLACE
```
"""

SOMEFILE_OTHER_BRANCH = """def some_func():
    print("yay")

def some_func2():
    print("yay2")

def i_am_different():
    print(":D")
"""

MANUAL_NOTE = "\n# my manual note\n"


def read_file(name):
    with open(polygon_folder / name, "r") as f:
        return f.read()


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

def test_correct():
    recreate_polygon()

    answer = """
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
    errors = do_changes_test(answer)
    assert errors.error_replaces == []

    with open(polygon_folder / "somefile.py", "r") as f:
        code = f.read()
        assert code == """def some_func():
    print("yay")

def some_func2():
    print("yay2")

def i_am_ready():
    print("=)")
"""

def test_file_not_found():
    recreate_polygon()
    answer = """
There is your code <3
File: fake.py
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
    errors = do_changes_test(answer)
    assert errors.error_replaces == [1]

def test_search_not_found():
    recreate_polygon()
    answer = """
There is your code <3
File: fake.py
```
<<<<<<< SEARCH
def pls_refactor_me():
    print("=(")
what am doing here???
=======
def i_am_ready():
    print("=)")
>>>>>>> REPLACE
```
"""
    errors = do_changes_test(answer)
    assert errors.error_replaces == [1]

def test_multi_success_replace():
    recreate_polygon()
    answer = """
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

Also i made next optimizations as tip

File: another.py
```
<<<<<<< SEARCH
time.sleep(0.02)
=======
time.sleep(0.01)
>>>>>>> REPLACE
``` 
"""
    do_changes_test(answer)

    with open(polygon_folder / "somefile.py", "r") as f:
        code = f.read()
        assert code == """def some_func():
    print("yay")

def some_func2():
    print("yay2")

def i_am_ready():
    print("=)")
"""
    with open(polygon_folder / "another.py", "r") as f:
        code = f.read()
        assert code == """import sys
import time

print("Starting system:")
for i in range(101):
    sys.stdout.write(f"\\rProgress: [{i}%]")
    sys.stdout.flush()
    time.sleep(0.01)
print("\\nTest successful passed!")
"""

def test_success_and_error():
    recreate_polygon()
    answer = """
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

Also i made next optimizations as tip

File: another.py
```
<<<<<<< SEARCH
time.sleep(999)
=======
time.sleep(0.01)
>>>>>>> REPLACE
``` 
"""
    errors = do_changes_test(answer)

    with open(polygon_folder / "somefile.py", "r") as f:
        code = f.read()
        assert code == """def some_func():
    print("yay")

def some_func2():
    print("yay2")

def i_am_ready():
    print("=)")
"""
    with open(polygon_folder / "another.py", "r") as f:
        code = f.read()
        assert code == """import sys
import time

print("Starting system:")
for i in range(101):
    sys.stdout.write(f"\\rProgress: [{i}%]")
    sys.stdout.flush()
    time.sleep(0.02)
print("\\nTest successful passed!")
"""
    assert errors.error_replaces == [2]


def test_undo():
    recreate_polygon()

    errors = do_changes_test(ANSWER_STEP_1)
    assert errors.error_replaces == []
    assert read_file("somefile.py") == SOMEFILE_AFTER_AI

    undo_files()

    assert read_file("somefile.py") == SOMEFILE_ORIGINAL


def test_undo_nothing_to_undo():
    recreate_polygon()

    undo_files()

    assert read_file("somefile.py") == SOMEFILE_ORIGINAL
    assert read_file("another.py") == ANOTHER_ORIGINAL
    assert state.undo_stack == []
    assert state.redo_stack == []


def test_undo_multiple_files_in_one_turn():
    recreate_polygon()

    errors = do_changes_test(ANSWER_TWO_FILES)
    assert errors.error_replaces == []
    assert read_file("somefile.py") == SOMEFILE_AFTER_AI
    assert read_file("another.py") == ANOTHER_AFTER_AI

    undo_files()

    assert read_file("somefile.py") == SOMEFILE_ORIGINAL
    assert read_file("another.py") == ANOTHER_ORIGINAL


def test_undo_twice_goes_step_by_step():
    recreate_polygon()

    do_changes_test(ANSWER_STEP_1)
    do_changes_test(ANSWER_STEP_2)
    assert read_file("somefile.py") == SOMEFILE_AFTER_AI_2

    undo_files()
    assert read_file("somefile.py") == SOMEFILE_AFTER_AI

    undo_files()
    assert read_file("somefile.py") == SOMEFILE_ORIGINAL

    undo_files()
    assert read_file("somefile.py") == SOMEFILE_ORIGINAL


def test_redo():
    recreate_polygon()

    do_changes_test(ANSWER_STEP_1)
    undo_files()
    assert read_file("somefile.py") == SOMEFILE_ORIGINAL

    redo_files()

    assert read_file("somefile.py") == SOMEFILE_AFTER_AI


def test_redo_nothing_to_redo():
    recreate_polygon()

    redo_files()

    assert read_file("somefile.py") == SOMEFILE_ORIGINAL
    assert read_file("another.py") == ANOTHER_ORIGINAL
    assert state.undo_stack == []
    assert state.redo_stack == []


def test_redo_multiple_files_in_one_turn():
    recreate_polygon()

    do_changes_test(ANSWER_TWO_FILES)
    undo_files()
    assert read_file("somefile.py") == SOMEFILE_ORIGINAL
    assert read_file("another.py") == ANOTHER_ORIGINAL

    redo_files()

    assert read_file("somefile.py") == SOMEFILE_AFTER_AI
    assert read_file("another.py") == ANOTHER_AFTER_AI


def test_undo_redo_chain():
    recreate_polygon()

    do_changes_test(ANSWER_STEP_1)
    do_changes_test(ANSWER_STEP_2)

    undo_files()
    undo_files()
    assert read_file("somefile.py") == SOMEFILE_ORIGINAL

    redo_files()
    assert read_file("somefile.py") == SOMEFILE_AFTER_AI

    redo_files()
    assert read_file("somefile.py") == SOMEFILE_AFTER_AI_2

    redo_files()
    assert read_file("somefile.py") == SOMEFILE_AFTER_AI_2


def test_undo_after_redo():
    recreate_polygon()

    do_changes_test(ANSWER_STEP_1)
    undo_files()
    redo_files()
    assert read_file("somefile.py") == SOMEFILE_AFTER_AI

    undo_files()

    assert read_file("somefile.py") == SOMEFILE_ORIGINAL


def test_new_ai_turn_clears_redo():
    recreate_polygon()

    do_changes_test(ANSWER_STEP_1)
    undo_files()
    assert state.redo_stack != []

    errors = do_changes_test(ANSWER_OTHER_BRANCH)
    assert errors.error_replaces == []
    assert state.redo_stack == []
    assert read_file("somefile.py") == SOMEFILE_OTHER_BRANCH

    redo_files()

    assert read_file("somefile.py") == SOMEFILE_OTHER_BRANCH


def test_undo_after_new_branch_returns_to_original():
    recreate_polygon()

    do_changes_test(ANSWER_STEP_1)
    undo_files()
    do_changes_test(ANSWER_OTHER_BRANCH)

    undo_files()

    assert read_file("somefile.py") == SOMEFILE_ORIGINAL


def test_redo_brings_back_manual_edits():
    recreate_polygon()

    do_changes_test(ANSWER_STEP_1)

    with open(polygon_folder / "somefile.py", "a") as f:
        f.write(MANUAL_NOTE)
    assert read_file("somefile.py") == SOMEFILE_AFTER_AI + MANUAL_NOTE

    undo_files()
    assert read_file("somefile.py") == SOMEFILE_ORIGINAL

    redo_files()

    assert read_file("somefile.py") == SOMEFILE_AFTER_AI + MANUAL_NOTE