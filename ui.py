import shutil
from state import state

def draw_logo():
    print("""


    ██  ██ ▄▄ ▄▄▄▄  ▄▄▄▄▄ ██     ▄▄▄▄▄  ▄▄▄▄  ▄▄▄   ▄▄▄▄ ▄▄ ▄▄ 
    ██▄▄██ ██ ██▄██ ██▄▄  ██     ██▄▄  ██ ▄▄ ██▀██ ██▀▀▀ ▀███▀ 
     ▀██▀  ██ ██▄█▀ ██▄▄▄ ██████ ██▄▄▄ ▀███▀ ██▀██ ▀████   █   


    Vibe with control

""" + "=" * shutil.get_terminal_size().columns)

def draw_menu():
    chat_history_ui = f" CHAT_HISTORY[{int(len(state.chat_history)/2)}]" if state.chat_history else ""

    print("=" * shutil.get_terminal_size().columns, end="\n")
    print(' '.join(list([my_file.name for my_file in state.files_context])) + chat_history_ui, end="\n\n")