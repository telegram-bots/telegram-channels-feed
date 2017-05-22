def read_to_string(file_path) -> str:
    with open(file_path, 'r') as file:
        data = file.read()
    return data
