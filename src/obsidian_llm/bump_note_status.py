from obsidian_llm.io import count_links_in_file
from obsidian_llm.io import list_files_with_tag


def bump_note_status(vault_path: str) -> None:
    """scans all notes currently tagged as stubs (`📝/🟥️`) and decide whether to bump its status.

    In particular, we count the number of links in the body of the note and suggest a status based on that. Note status are as follows:
    - `📝/🟥️`: *Stub*. 0 links.
    - `📝/🟧️`: *Processing*. 1-4 links.
    - `📝/🟩️`: *Evergreen*. 5+ links.
    """
    # Define the status tags
    status_tags = {"📝/🟥️": "Stub", "📝/🟧️": "Processing", "📝/🟩️": "Evergreen"}
    stubs = list_files_with_tag(vault_path, "📝")
    stubs.extend(list_files_with_tag(vault_path, "📝/🟥️"))

    for file_path in stubs:
        num_links = count_links_in_file(file_path)
        bump_note_status_for_file(file_path, num_links, status_tags)
