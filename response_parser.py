from state import state

FILE_LABEL = "File: "
SEARCH_MARKER = "\n<<<<<<< SEARCH\n"
DIVIDER_MARKER = "\n=======\n"
REPLACE_MARKER = "\n>>>>>>> REPLACE"

def do_changes(response: str):
    edited_response = response

    while True:
        try:
            find_file = edited_response.find(FILE_LABEL)

            if find_file == -1:
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

                edit_file(file_name, find, replace)
        except Exception as e:
            print(e)


def edit_file(file_name: str, find: str, replace: str):

    for file in state.files_context:
        if file_name == file.name:
            with open(file.path, "r", encoding="UTF-8") as f:
                file_data = f.read()

            if file_data.find(find) == -1:
                raise Exception(f"Find data not found in {file_name}")

            file_data = file_data.replace(find, replace)

            with open(file.path, "w", encoding="UTF-8") as f:
                f.write(file_data)
            break
    else:
        raise Exception(f"File not found: {file_name}")