import shutil

import generate
from utils import find_file_from_project
import ui

ui.draw_logo()

from state import state

while True:
    try:
        command = input("> ")

        if not command.startswith("/"):
            generate.run_generation(command)
            ui.draw_menu()
            continue

        if command == "/exit":
            break
        elif command == "/help":
            print("TODO") #TODO
        elif command.startswith("/add "):
            founded_files = find_file_from_project(command[5:].strip())
            state.files_context.update(founded_files)

        elif command.startswith("/drop "):
            founded_files = find_file_from_project(command[5:].strip())
            state.files_context -= founded_files

        elif command == "/dropall":
            state.files_context.clear()
        elif command == "/clear":
            state.chat_history.clear()

        ui.draw_menu()

    except KeyboardInterrupt:
        print("\n" + "=" * shutil.get_terminal_size().columns, end="")
        if not state.is_code_generating:
            break
    except Exception:
        raise