import shutil
import sys
import threading

from state import state


class WaitingAnimation:
    def __init__(self, text):
        self._stop_event = threading.Event()
        self._thread = None
        self.text = text

    def start(self):
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self):
        if self._thread is None:
            return

        self._stop_event.set()
        self._thread.join()
        sys.stdout.write("\r" + " " * 32 + "\r")
        sys.stdout.flush()
        self._thread = None

    def _animate(self):
        frames = "|/-\\"
        frame_index = 0

        while not self._stop_event.is_set():
            sys.stdout.write(f"\r{self.text}... {frames[frame_index]}")
            sys.stdout.flush()
            frame_index = (frame_index + 1) % len(frames)
            self._stop_event.wait(0.12)

def draw_logo():
    print("""


    ██  ██ ▄▄ ▄▄▄▄  ▄▄▄▄▄ ██     ▄▄▄▄▄  ▄▄▄▄  ▄▄▄   ▄▄▄▄ ▄▄ ▄▄ 
    ██▄▄██ ██ ██▄██ ██▄▄  ██     ██▄▄  ██ ▄▄ ██▀██ ██▀▀▀ ▀███▀ 
     ▀██▀  ██ ██▄█▀ ██▄▄▄ ██████ ██▄▄▄ ▀███▀ ██▀██ ▀████   █   


    Vibe with control | @Invoidy

""" + "=" * shutil.get_terminal_size().columns)

def draw_menu():
    chat_history_ui = f" CHAT_HISTORY[{int(len(state.chat_history)/2)}]" if state.chat_history else ""

    print("=" * shutil.get_terminal_size().columns, end="\n")
    print(' '.join(list([my_file.name for my_file in state.files_context])) + chat_history_ui, end="\n\n")
