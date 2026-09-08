from pathlib import Path
import shutil

from response_parser import do_changes
from state import state
from models import MyFile

test_dir = Path(__file__).resolve().parent
polygon_folder = test_dir / "polygon"

state.files_context.update({MyFile(path=polygon_folder / "somefile.py", name="somefile.py"),
                            MyFile(path=polygon_folder / "another.py", name="another.py")})

def recreate_polygon():

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
    errors = do_changes(answer)
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
    errors = do_changes(answer)
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
    errors = do_changes(answer)
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
    do_changes(answer)

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
    errors = do_changes(answer)

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