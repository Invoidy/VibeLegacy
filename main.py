import os
import shutil
from pathlib import Path

import generate
from utils import find_file_from_project, undo_files, redo_files
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
            generate.run_generation(command)
            ui.draw_menu()
            continue

        if command == "/exit":
            break
        elif command == "/config":
            config_folder = Path(__file__).resolve().parent
            print(config_folder / ".CONFIG_ME")
            os.startfile(config_folder)
        elif command == "/help":
            print("""
            Commands:

              /help                  Show this help message
              /add <file>            Add file(s) to the context
              /drop <file>           Remove file(s) from the context
              /dropall               Remove all files from the context
              /clear                 Clear chat history
              /undo                  Undo AI edits, one step at a time
              /redo                  Redo what /undo reverted, including your manual edits
              /config                Opens config file's directory
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
        elif command == "/redo":
            redo_files()

        else:
            print(f"Unknown command. Try '/help' for more information.")

        ui.draw_menu()

    except KeyboardInterrupt:
        print("\n" + "=" * shutil.get_terminal_size().columns, end="")
        if not state.is_code_generating:
            break