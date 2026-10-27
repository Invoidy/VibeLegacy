from openai import OpenAI

import prompts
from response_parser import do_changes
from state import state
from settings import settings
import ui
from models import FileBackup

FILE_LABEL = "File: "

client = OpenAI(base_url=settings.BASE_URL, api_key=settings.API_KEY)

def generate(task: str):
    state.is_code_generating = True

    messages = (
        [{"role": "developer", "content": prompts.build_developer_prompt()}] +
        state.chat_history +
        [{"role": "user", "content": task}]
    )

    waiting_animation = ui.WaitingAnimation(text="Waiting for AI response")
    full_output = ""

    waiting_animation.start()
    try:
        if settings.REASONING:
            response = client.chat.completions.create(
                model=settings.MODEL,
                messages=messages,
                extra_body={"reasoning": {"effort": settings.REASONING}},
                stream=True
            )
        else:
            response = client.chat.completions.create(
                model=settings.MODEL,
                messages=messages,
                stream=True
            )

        for chunk in response:
            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                waiting_animation.stop()
                print(content, end="", flush=True)
                full_output += content
    finally:
        waiting_animation.stop()

    print("\n")

    do_changes(full_output)


    find_starts = full_output.split(FILE_LABEL)
    files_to_save = set([file[:file.find("\n")] for file in find_starts])
    backups = set()
    for my_file in state.files_context:
        if my_file.name in files_to_save:
            try:
                with open(my_file.path, "r", encoding="UTF-8", newline="") as f:
                    backups.add(FileBackup(my_file, f.read()))
            except (OSError, UnicodeDecodeError):
                continue
    state.last_change_code_save = backups

    state.chat_history += [
        {"role": "user", "content": task},
        {"role": "assistant", "content": full_output}
    ]


def run_generation(new_task: str):
    try:
        generate(new_task)
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\n[Generation stopped]")
    finally:
        state.is_code_generating = False
