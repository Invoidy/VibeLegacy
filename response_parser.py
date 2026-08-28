from state import state

FILE_LABEL = "File: "
SEARCH_MARKER = "\n<<<<<<< SEARCH\n"
DIVIDER_MARKER = "\n=======\n"
REPLACE_MARKER = "\n>>>>>>> REPLACE"

def do_changes(response: str):
    edited_response = response
    changes = {}
    pending_data = {}

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

                path, new_data = prepare_file_edit(file_name, find, replace, pending_data)
                changes[path] = new_data
        except Exception as e:
            print(e)
            return

    original_data = {}
    try:
        original_data = {path: path.read_text(encoding="UTF-8") for path in changes}

        for path, new_data in changes.items():
            path.write_text(new_data, encoding="UTF-8")
    except Exception as e:
        for path, data in original_data.items():
            try:
                path.write_text(data, encoding="UTF-8")
            except Exception:
                pass
        print(e)


def prepare_file_edit(file_name: str, find: str, replace: str, pending_data: dict):

    for file in state.files_context:
        if file_name == file.name:
            file_data = pending_data.get(file.path, file.path.read_text(encoding="UTF-8"))

            if file_data.find(find) == -1:
                raise Exception(f"Find data not found in {file_name}")

            file_data = file_data.replace(find, replace)
            pending_data[file.path] = file_data
            return file.path, file_data
    else:
        raise Exception(f"File not found: {file_name}")
