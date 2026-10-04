<div align="center">

```
██  ██ ▄▄ ▄▄▄▄  ▄▄▄▄▄ ██     ▄▄▄▄▄  ▄▄▄▄  ▄▄▄   ▄▄▄▄ ▄▄ ▄▄
██▄▄██ ██ ██▄██ ██▄▄  ██     ██▄▄  ██ ▄▄ ██▀██ ██▀▀▀ ▀███▀
▀██▀  ██ ██▄█▀ ██▄▄▄ ██████ ██▄▄▄ ▀███▀ ██▀██ ▀████   █
```

**Vibe with control.**

![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue)
![License: GPL v3](https://img.shields.io/badge/license-GPLv3-blue)

</div>

VibeLegacy is a console AI coding assistant that edits your files through SEARCH/REPLACE blocks. The model proposes the changes; you decide what it can see, and you can roll back the last request it did.

## Key features

- **Lightweight.** No heavy IDE plugin and no autonomous agent loop: a small console app with a handful of dependencies that starts instantly.
- **Low cost per task.** The model receives only the files you attach and answers with compact SEARCH/REPLACE blocks instead of rewriting whole files, so each task uses far fewer tokens.
- **Full control.** You choose what the model sees, it can only edit those files, and `/undo` reverts the last request.

## Usage

Open a terminal in the root of the project you want to work on and run the executable:

```bash
cd path/to/your/project
vibelegacy.exe
```

Files are looked up relative to the directory you launched from, so use paths like `src/app.py` or `utils.py`.

**Type a request to talk to the model. Anything starting with `/` is a command.**

| Command | Description |
| --- | --- |
| `/help` | Show the help message |
| `/add path/to/file` | Add a file to the context. Separate several paths with spaces. |
| `/drop path/to/file` | Remove a file from the context. Separate several paths with spaces. |
| `/dropall` | Remove all files from the context |
| `/clear` | Clear the chat history |
| `/undo` | Restore files to their state before the last AI request |
| `/exit` | Exit VibeLegacy |

**Input shortcuts**

| Key | Action |
| --- | --- |
| `Enter` | Send the message |
| `Shift+Enter` / `Alt+Enter` / `Ctrl+J` | Insert a new line |
| `Ctrl+C` | Stop the current generation (or exit when idle) |
| `RMB` | Paste a text in console |

### Example workflow

```text
> /add app.py tests/test_app.py
> Add input validation to parse_config() and raise ValueError on empty keys
  ... the response streams in, SEARCH/REPLACE blocks are applied to your files ...
> /undo        # not happy with the result? roll it back
```

## Configuration (`.CONFIG_ME`)

On the very first launch VibeLegacy creates a `.CONFIG_ME` file next to `vibelegacy.exe`, opens the folder, and exits. Fill it in, then start the app again.

```ini
BASE_URL=https://openrouter.ai/api/v1
API_KEY=
MODEL=openai/gpt-6-luna
REASONING=high
```

| Variable | Description |
| --- | --- |
| `BASE_URL` | Base URL of any OpenAI-compatible API. Defaults to OpenRouter. |
| `API_KEY` | Your API key for that provider. Required. |
| `MODEL` | Model identifier, in the format your provider expects. |
| `REASONING` | Reasoning effort (for example `low`, `medium`, `high`), passed to the API as `reasoning.effort`. Leave empty to disable. |

## Installation and build

**Requirements**

- Python 3.14 or newer
- pip

**Build a standalone executable with Nuitka**

```bash
git clone https://github.com/Invoidy/VibeLegacy.git
cd VibeLegacy

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

pip install nuitka
python -m nuitka --standalone --remove-output --output-dir=dist --output-filename=vibelegacy.exe --include-data-files=first_start=first_start --windows-icon-from-ico=logo.ico main.py
```

The result is placed in `dist/main.dist/` (`dist` is already in `.gitignore`), with `vibelegacy.exe` inside. Keep the `first_start` marker file next to the executable so the first-run setup works.

## Features

- Lightweight, low cost per task, full control (see [Key features](#key-features))
- Context built from the files you choose with `/add`
- Streamed responses with a live waiting indicator
- Chat history that carries over between requests (`/clear` to reset)
- One-command rollback with `/undo`
- Any OpenAI-compatible API, OpenRouter by default
- Configurable reasoning effort
- Multi-line input with Shift+Enter, even in a plain Windows console

## How it works

1. You send a request. VibeLegacy snapshots the attached files, then builds a developer prompt containing the rules and the full content of every attached file.
2. The prompt, the chat history and your request are sent to the model, and the answer is streamed to your terminal.
3. The response is scanned for edit blocks and each one is applied to the matching attached file.

**Edit format**

````text
File: path/to/file.ext
```
<<<<<<< SEARCH
[exact existing lines]
=======
[new lines that replace them]
>>>>>>> REPLACE
```
````

If a block can't be applied (the SEARCH text isn't found, or the file isn't attached), VibeLegacy skips it, applies the remaining blocks, and prints the numbers of the failed ones. You can ask the model to rewrite them or run `/undo`.

**Modules**

| File | Role |
| --- | --- |
| `main.py` | Command loop and entry point |
| `generate.py` | Request to the model and response streaming |
| `response_parser.py` | Parsing and applying SEARCH/REPLACE blocks |
| `prompts.py` | Developer prompt and attached-file context |
| `settings.py` | Loading and validating `.CONFIG_ME` |
| `state.py` | Shared state: context files, chat history, snapshots |
| `utils.py` | File lookup, snapshots, undo, first-start check |
| `ui.py` | Logo, status line, waiting animation |
| `multiline_input.py` | Multi-line prompt built on prompt_toolkit |
| `models.py` | `MyFile` data class |

## Development

Tests live in the `pytest/` folder and cover the response parser. Run them from the repository root:

```bash
python -m pytest pytest/
```

The tests create a scratch directory at `pytest/polygon/`, which is ignored by git.

**Contributing**

Issues and pull requests are welcome. For larger changes, please open an issue first to discuss what you would like to change, and include or update tests when you touch the parser.

## License and author

Distributed under the **GNU General Public License v3.0**. See [LICENSE](LICENSE) for details.

Created by **@Invoidy**.

*Have fun vibing, with control.*
