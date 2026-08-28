import time

import test
from response_parser import do_changes
from state import state


def generate(task: str):
    state.is_code_generating = True

    # print([{"role": "developer", "content": prompts.build_developer_prompt()}]
    #       + state.chat_history +
    #       [{"role": "user", "content": task}])

    output = test.test_response

    for char in output:
        time.sleep(0.001)
        print(char, end="", flush=True)

    do_changes(output)
    state.chat_history += [{"role": "user", "content": task}, {"role": "assistant", "content": output}]


def run_generation(new_task: str):
    try:
        generate(new_task)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        state.is_code_generating = False
