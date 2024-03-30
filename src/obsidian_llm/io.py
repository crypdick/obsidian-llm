def read_md(file_path: str) -> str:
    with open(file_path) as file:
        content = file.read()
    return content
