import shutil

import generate
from utils import find_file_from_project, save_copy_of_files, undo_files
import ui
from state import state
from multiline_input import multiline_input

ui.draw_logo()

while True:
    try:
        command = multiline_input("> ")

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
              /undo                   Restore files to their state before the last AI request
              /exit                  Exit VibeLegacy

            Anything without "/" is treated as a request to the AI.
            """)
        elif command.startswith("/add "):
            found_files = find_file_from_project(command[5:].strip())
            state.files_context.update(found_files)

        elif command.startswith("/drop "):
            found_files = find_file_from_project(command[5:].strip())
            state.files_context -= found_files

        elif command == "/dropall":
            state.files_context.clear()
        elif command == "/clear":
            state.chat_history.clear()
        elif command == "/undo":
            undo_files()

        else:
            print(f"Unknown command. Try '/help' for more information.")

        ui.draw_menu()

    except KeyboardInterrupt:
        print("\n" + "=" * shutil.get_terminal_size().columns, end="")
        if not state.is_code_generating:
            break