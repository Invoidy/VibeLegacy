import shutil

import generate
from utils import find_file_from_project, save_copy_of_files, undo_files, check_if_first_start
import ui
from state import state
from pathlib import Path
import os

ui.draw_logo()

if check_if_first_start():
    import locale
    language = locale.getlocale()[0]

    print("\n" + "=" * shutil.get_terminal_size().columns, end="")
    print("""Welcome to VibeLegacy!

    Before you start, configure the `.CONFIG_ME` file with your API settings.
    
    You can view all available commands with `/help`.
    
    Main commands:
    
    * `/add <file>` — attach a file to the conversation
    * `/drop <file>` — remove an attached file
    * `/clear` — clear the message history
    
    Once configured, just describe what you want to build or change, and VibeLegacy will handle the code changes.
    
    Have fun vibing — with control.
    """)

    print("\n" + "=" * shutil.get_terminal_size().columns, end="")

    print("""Добро пожаловать в VibeLegacy!

    Перед началом работы настройте файл `.CONFIG_ME`, указав необходимые API-настройки.

    Посмотреть все доступные команды можно с помощью `/help`.

    Основные команды:

    * `/add <file>` — добавить файл к разговору
    * `/drop <file>` — убрать прикреплённый файл
    * `/clear` — очистить историю сообщений

    После настройки просто опишите, что вы хотите создать или изменить, и VibeLegacy внесёт необходимые изменения в код.

    Приятного вайба — но с контролем.
    """)

    print("\n" + "=" * shutil.get_terminal_size().columns, end="")

    env_folder = Path(__file__).resolve().parent
    os.startfile(env_folder)
    exit(0)

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
              /undo                   Restore files to their state before the last AI request
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
        elif command == "/undo":
            undo_files()

        else:
            print(f"Unknown command. Try '/help' for more information.")

        ui.draw_menu()

    except KeyboardInterrupt:
        print("\n" + "=" * shutil.get_terminal_size().columns, end="")
        if not state.is_code_generating:
            break
    except Exception:
        raise
