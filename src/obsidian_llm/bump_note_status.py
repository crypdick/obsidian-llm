import logging

from obsidian_llm.diff_generator import apply_diff
from obsidian_llm.diff_generator import apply_new_frontmatter
from obsidian_llm.io import count_links_in_file
from obsidian_llm.io import list_files_with_tag
from obsidian_llm.io import parse_frontmatter


def bump_all_note_status(vault_path: str) -> None:
    """scans all notes currently tagged as stubs (`📝/🟥️`) and decide whether to bump its status.

    In particular, we count the number of links in the body of the note and suggest a status based on that. Note status are as follows:
    - `📝/🟥️`: *Stub*. 0 links.
    - `📝/🟧️`: *Processing*. 1-4 links.
    - `📝/🟩️`: *Evergreen*. 5+ links.
    """
    status_tags = {
        "Stub": "📝/🟥",
        "Processing": "📝/🟧️",
        "Evergreen": "📝/🟩",
        "Malformed": "📝",
    }
    stubs = list_files_with_tag(vault_path, status_tags["Malformed"])
    stubs.extend(list_files_with_tag(vault_path, status_tags["Stub"]))

    num_changed = 0
    for file_path in stubs:
        num_links = count_links_in_file(file_path)
        updated = bump_note_status_for_file(file_path, num_links, status_tags)
        num_changed += updated
        # note: no need to add processed_for key, since the status is already updated

    logging.info(f"Bumped status for {num_changed} notes of {len(stubs)} stubs.")


def bump_note_status_for_file(file_path: str, num_links: int, status_tags: dict) -> int:
    """
    Updates the status of a note based on the number of links it contains.

    :param file_path: Path to the markdown file.
    :param num_links: Number of links in the note.
    :param status_tags: Dictionary mapping status tags to their descriptions.
    """
    # Determine the new status based on the number of links
    if num_links == 0:
        logging.info(f"Not updating status for {file_path}: no links found.")
        return 0
    elif 1 <= num_links <= 4:
        new_status = status_tags["Processing"]
    else:
        new_status = status_tags["Evergreen"]

    # Read the current frontmatter
    frontmatter_dict, frontmatter_str = parse_frontmatter(file_path)
    assert frontmatter_dict is not None

    # Update the tags in the frontmatter

    # Remove old status tags and add the new status
    if (
        isinstance(frontmatter_dict["tags"], str)
        and frontmatter_dict["tags"] != new_status
    ):
        frontmatter_dict["tags"] = [new_status]
    elif isinstance(frontmatter_dict["tags"], list):
        frontmatter_dict["tags"] = [
            tag
            for tag in frontmatter_dict["tags"]
            if tag in status_tags and tag != new_status
        ]
        frontmatter_dict["tags"].append(new_status)
    else:
        logging.exception(
            f"Invalid tags found in {file_path}: {frontmatter_dict['tags']}."
        )
        raise ValueError(
            f"Invalid tags found in frontmatter of {file_path}: {frontmatter_dict['tags']}."
        )

    new_content = apply_new_frontmatter(frontmatter_dict, file_path)
    apply_diff(new_content, file_path, auto_apply=True)

    return 1
