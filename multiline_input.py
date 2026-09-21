"""

[AI GENERATED]

A replacement for the regular input() with multiline input "like in Codex":

    Enter        -> submit the text
    Shift+Enter  -> new line
    Alt+Enter    -> new line (fallback)
    Ctrl+J       -> new line (fallback)

Pasting multiline text works as usual.

Usage:

    from codex_input import multiline_input

    text = multiline_input("> ")
    print(text)


HOW IT WORKS (and why Shift+Enter is caught even in a bare cmd.exe)
--------------------------------------------------------------------
The Win32 Console API hands the application a KEY_EVENT_RECORD structure that
has a dwControlKeyState field with the SHIFT_PRESSED bit (0x0010). This bit is
also set for the Enter key (VK_RETURN). So in cmd.exe it IS possible to tell
Enter from Shift+Enter — but only if you read console events
(ReadConsoleInput) rather than stdin bytes. When reading bytes, both Enter and
Shift+Enter produce the same '\r'.

prompt_toolkit does read events (the ConsoleInputReader class), but it loses
Shift specifically for Enter: its shift mapping has arrows/Home/End/Tab but not
Enter, and the Keys enum has no ShiftEnter value. So below we:

  1) Force prompt_toolkit on Windows to use the classic ConsoleInputReader
     instead of Vt100ConsoleInputReader. The VT mode turns key presses into
     escape sequences via conhost, and the Shift information for Enter is lost
     there.

  2) Patch ConsoleInputReader._event_to_key_presses: if Enter (VK_RETURN)
     arrives and SHIFT_PRESSED is set in ControlKeyState, we emit the sequence
     [Escape, Enter]. prompt_toolkit treats such a pair as Alt+Enter, to which
     we bind inserting a newline. This gives us a separate key combination
     without touching the Keys enum.

  3) For Unix/ConPTY/PyCharm we additionally register the ANSI sequences that
     terminals use to encode Shift+Enter (xterm modifyOtherKeys and the kitty
     keyboard protocol), routing them to the same newline handler.

Installing the dependency:
    pip install prompt_toolkit
"""

from __future__ import annotations

import sys

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.keys import Keys
except ImportError:
    sys.stderr.write(
        "Не найдена библиотека prompt_toolkit.\n"
        "Установите её командой:\n\n"
        "    pip install prompt_toolkit\n\n"
    )
    raise


__all__ = ["multiline_input"]


IS_WINDOWS = sys.platform == "win32"


# ---------------------------------------------------------------------------
# 1 and 2. Windows backend patch: teach it to distinguish Shift+Enter
# ---------------------------------------------------------------------------

def _patch_windows_shift_enter() -> bool:
    """
    Patches the prompt_toolkit Win32 backend so that Shift+Enter arrives as a
    distinct combination (Escape + Enter, i.e. Alt+Enter in the library's
    terms).

    Returns True if the patch was applied successfully.
    """
    if not IS_WINDOWS:
        return False

    try:
        from prompt_toolkit.input import win32 as ptk_win32
        from prompt_toolkit.key_binding.key_processor import KeyPress
    except Exception:
        return False

    ConsoleInputReader = getattr(ptk_win32, "ConsoleInputReader", None)
    Win32Input = getattr(ptk_win32, "Win32Input", None)

    if ConsoleInputReader is None or Win32Input is None:
        return False

    # --- 1) Force the classic (non-VT) console event reader -----------------
    original_init = Win32Input.__init__

    def patched_init(self, stdin=None) -> None:
        original_init(self, stdin)
        # If the library picked VT mode, fall back to reading console events,
        # where ControlKeyState with the Shift flag is available.
        if getattr(self, "_use_virtual_terminal_input", False):
            try:
                self.console_input_reader = ConsoleInputReader()
                self._use_virtual_terminal_input = False
            except Exception:
                # If for some reason it didn't work, leave things as they were:
                # Shift+Enter simply won't work, everything else keeps going.
                pass

    Win32Input.__init__ = patched_init

    # --- 2) Patch the key event parsing -------------------------------------
    original_event_to_key_presses = ConsoleInputReader._event_to_key_presses

    SHIFT_PRESSED = getattr(ConsoleInputReader, "SHIFT_PRESSED", 0x0010)
    LEFT_ALT_PRESSED = getattr(ConsoleInputReader, "LEFT_ALT_PRESSED", 0x0002)
    LEFT_CTRL_PRESSED = getattr(ConsoleInputReader, "LEFT_CTRL_PRESSED", 0x0008)
    RIGHT_CTRL_PRESSED = getattr(ConsoleInputReader, "RIGHT_CTRL_PRESSED", 0x0004)

    VK_RETURN = 0x0D

    def patched_event_to_key_presses(self, ev):
        control_key_state = ev.ControlKeyState

        shift = bool(control_key_state & SHIFT_PRESSED)
        alt = bool(control_key_state & LEFT_ALT_PRESSED)
        ctrl = bool(
            control_key_state & LEFT_CTRL_PRESSED
            or control_key_state & RIGHT_CTRL_PRESSED
        )

        is_enter = ev.VirtualKeyCode == VK_RETURN

        # Exactly Shift+Enter (without Ctrl and Alt) -> emit it as Escape+Enter,
        # which is equivalent to Alt+Enter for prompt_toolkit.
        if is_enter and shift and not alt and not ctrl:
            return [KeyPress(Keys.Escape, ""), KeyPress(Keys.ControlM, "\r")]

        return original_event_to_key_presses(self, ev)

    ConsoleInputReader._event_to_key_presses = patched_event_to_key_presses
    return True


# ---------------------------------------------------------------------------
# 3. Shift+Enter ANSI sequences for Unix / ConPTY / PyCharm
# ---------------------------------------------------------------------------

def _patch_vt100_shift_enter() -> None:
    """
    Registers the sequences that modern terminals use to encode Shift+Enter
    and routes them to Keys.ControlJ (which for us means "new line").

    Affects PyCharm, Windows Terminal, VS Code, iTerm2, kitty, etc.
    """
    try:
        from prompt_toolkit.input import ansi_escape_sequences as seqs
    except Exception:
        return

    table = getattr(seqs, "ANSI_SEQUENCES", None)
    if table is None:
        return

    shift_enter_sequences = [
        "\x1b[27;2;13~",  # xterm modifyOtherKeys mode 2
        "\x1b[13;2u",     # kitty keyboard protocol / CSI-u
    ]

    # IMPORTANT: overwrite forcibly. By default prompt_toolkit maps
    # "\x1b[27;2;13~" to Keys.ControlM, i.e. plain Enter — and in such a
    # terminal Shift+Enter would SUBMIT the input instead of adding a newline.
    for seq in shift_enter_sequences:
        try:
            table[seq] = Keys.ControlJ
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Key bindings
# ---------------------------------------------------------------------------

def _build_keybindings() -> KeyBindings:
    kb = KeyBindings()

    @kb.add("enter")
    def _submit(event) -> None:
        """Plain Enter — submit the entered text."""
        event.current_buffer.validate_and_handle()

    @kb.add("escape", "enter")
    def _newline_alt_enter(event) -> None:
        """
        Alt+Enter, and on Windows after our patch — Shift+Enter as well
        (we translate it into exactly this Escape+Enter pair).
        """
        event.current_buffer.insert_text("\n")

    @kb.add("c-j")
    def _newline_ctrl_j(event) -> None:
        """Ctrl+J, and also Shift+Enter in terminals with VT encoding."""
        event.current_buffer.insert_text("\n")

    return kb


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------

_PATCHED = False
_SESSION: PromptSession | None = None


def _ensure_patched() -> None:
    global _PATCHED
    if _PATCHED:
        return
    _patch_windows_shift_enter()
    _patch_vt100_shift_enter()
    _PATCHED = True


def multiline_input(prompt: str = "> ", default: str = "") -> str:
    """
    Multiline input — a replacement for the regular input().

    Enter submits the text, Shift+Enter (as well as Alt+Enter and Ctrl+J)
    inserts a newline.

    :param prompt:  the input prompt.
    :param default: text the input field is pre-filled with.
    :return:        the entered text, may contain '\\n' characters.

    Exceptions are propagated outward, just like with the regular input():
      * KeyboardInterrupt — Ctrl+C
      * EOFError          — Ctrl+D (Unix) / Ctrl+Z+Enter (Windows)
    """
    global _SESSION

    _ensure_patched()

    # The session is created once and reused: this preserves the input history
    # between calls (up/down arrows) and avoids the cost of re-initializing
    # the terminal.
    if _SESSION is None:
        _SESSION = PromptSession(
            key_bindings=_build_keybindings(),
            multiline=True,
        )

    return _SESSION.prompt(prompt, default=default)