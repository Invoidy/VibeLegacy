import shutil

import generate
from utils import find_file_from_project, save_copy_of_files
import ui

ui.draw_logo()

from state import state

while True:
    try:
        command = input("> ")

        if not command:
            ui.draw_menu()
            continue

        if not command.startswith("/"):
            save_copy_of_files()
            generate.run_generation(command)
            ui.draw_menu()
            continue

        if command == "/exit":
            break
        elif command == "/help":
            print("""
            Commands:

              /help                  Show this help message
              /add <file>            Add file(s) to the context
              /drop <file>           Remove file(s) from the context
              /dropall               Remove all files from the context
              /clear                 Clear chat history
              /exit                  Exit VibeLegacy

            Anything without "/" is treated as a request to the AI.
            """)
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
        else:
            print(f"Unknown command. Try '/help' for more information.")

        ui.draw_menu()

    except KeyboardInterrupt:
        print("\n" + "=" * shutil.get_terminal_size().columns, end="")
        if not state.is_code_generating:
            break
    except Exception:
        raise