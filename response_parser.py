# Example of find-replace block:
#
#
#
# File: path/to/file.ext
# ```
# <<<<<<< SEARCH
# [exact existing lines, character-for-character, including whitespace/indentation]
# =======
# [new lines that replace them]
# >>>>>>> REPLACE
# ```
#

from state import state
from dataclasses import dataclass, field

FILE_LABEL = "File: "
SEARCH_MARKER = "\n<<<<<<< SEARCH\n"
DIVIDER_MARKER = "\n=======\n"
REPLACE_MARKER = "\n>>>>>>> REPLACE"

@dataclass
class Errors:
    error_replaces: list = field(default_factory=list)
    error_index: int = 0

def do_changes(response: str) -> Errors:
    edited_response = response
    errors = Errors()

    while True:
        try:
            find_file = edited_response.find(FILE_LABEL)

            if find_file == -1:

                if len(errors.error_replaces) > 0:
                    print(f"Formatting errors have been detected in the blocks {errors.error_replaces}. Tip: You can ask the model to rewrite them OR type /undo to undo changes.")

                break
            else:
                find_search = edited_response.find(SEARCH_MARKER, find_file)
                find_divider = edited_response.find(DIVIDER_MARKER, find_file)
                find_replace = edited_response.find(REPLACE_MARKER, find_file)

                if -1 in (find_search, find_divider, find_replace):
                    edited_response = edited_response[find_file + len(FILE_LABEL):]
                    continue

                file_name_end = edited_response.find("\n", find_file + len(FILE_LABEL))
                file_name = edited_response[find_file + len(FILE_LABEL):file_name_end].strip()

                find = edited_response[find_search + len(SEARCH_MARKER):find_divider]
                replace = edited_response[find_divider + len(DIVIDER_MARKER):find_replace]

                edited_response = edited_response[find_replace + len(REPLACE_MARKER):]

                edit_file(file_name, find, replace, errors)
        except Exception as e:
            print(e)

    return errors


def edit_file(file_name: str, find: str, replace: str, errors):
    errors.error_index += 1

    for file in state.files_context:
        if file_name == file.name:
            with open(file.path, "r", encoding="UTF-8") as f:
                file_data = f.read()

            if file_data.find(find) == -1:
                errors.error_replaces.append(errors.error_index)
                raise Exception(f"!!! Find data not found in {file_name} !!! ERROR")

            file_data = file_data.replace(find, replace)

            with open(file.path, "w", encoding="UTF-8") as f:
                f.write(file_data)
            break
    else:
        errors.error_replaces.append(errors.error_index)
        raise Exception(f"!!! File not found: {file_name} !!! ERROR")