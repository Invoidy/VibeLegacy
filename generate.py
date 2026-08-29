from openai import OpenAI

import prompts
from response_parser import do_changes
from state import state
from settings import settings
import ui

client = OpenAI(base_url=settings.BASE_URL, api_key=settings.API_KEY)

def generate(task: str):
    state.is_code_generating = True

    messages = (
        [{"role": "developer", "content": prompts.build_developer_prompt()}] +
        state.chat_history +
        [{"role": "user", "content": task}]
    )

    waiting_animation = ui.WaitingAnimation()
    full_output = ""

    waiting_animation.start()
    try:
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
