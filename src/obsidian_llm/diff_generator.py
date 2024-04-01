import logging
import subprocess
from tempfile import NamedTemporaryFile

import yaml
from beartype import beartype

from .io import parse_frontmatter
from .io import read_md


def get_alias_diff(file_path, new_aliases, frontmatter_dict: dict | None):
    """
    Generates a diff between the original markdown file and a temporary file with proposed alias additions.
    Opens the proposed diff in `meld` for user to review and accept, reject, or edit the changes.

    :param file_path: Path to the original markdown file.
    :param new_aliases: List of new aliases to be added.
    :param frontmatter_dict: Parsed frontmatter of the markdown file as a dictionary.
    :param content: The full content of the markdown file.
    """
    if not new_aliases and not frontmatter_dict:
        logging.info(f"No new aliases or frontmatter found in {file_path}.")
        return
    logging.info(
        f"Starting the diff generation process for {file_path} with new aliases: {new_aliases}"
    )
    if not new_aliases:
        # do not add new aliases; just add processed_for key
        new_aliases = []
    if not frontmatter_dict:
        frontmatter_dict = {}

    # Update the aliases in the frontmatter
    if "aliases" in frontmatter_dict and isinstance(frontmatter_dict["aliases"], list):
        # Ensure no duplicates are added to the existing aliases
        unique_new_aliases = [
            alias for alias in new_aliases if alias not in frontmatter_dict["aliases"]
        ]
        frontmatter_dict["aliases"].extend(unique_new_aliases)
    else:
        logging.info(f"No existing aliases found in {file_path}. Adding new aliases.")
        if len(new_aliases) > 0:
            frontmatter_dict["aliases"] = new_aliases

    # if the aliases value is not a list or is an empty list, set it to an empty list
    if "aliases" in frontmatter_dict and (
        not isinstance(frontmatter_dict["aliases"], list)
    ):
        frontmatter_dict["aliases"] = []

    new_content = apply_new_frontmatter(frontmatter_dict, file_path)

    return new_content


def add_processed_for_key(file_path: str, key: str):
    """
    Add a 'processed_for' key to the frontmatter of a markdown file to mark it as processed for a specific task.

    :param file_path: Path to the markdown file.
    :param key: The key to add to the 'processed_for' list in the frontmatter.
    """
    frontmatter_dict, _ = parse_frontmatter(file_path)
    if frontmatter_dict:
        if "processed_for" not in frontmatter_dict:
            frontmatter_dict["processed_for"] = []
        if key not in frontmatter_dict["processed_for"]:
            frontmatter_dict["processed_for"].append(key)
        new_content = apply_new_frontmatter(frontmatter_dict, file_path)
        apply_diff(new_content, file_path, auto_apply=True)
    else:
        logging.error(
            f"Frontmatter not found in {file_path}. Cannot add processed_for key."
        )


def apply_new_frontmatter(frontmatter_dict: dict, file_path: str) -> str:
    """
    Replace the frontmatter in the original file with the updated frontmatter content.
    """
    # Serialize the updated frontmatter back to a YAML string
    updated_frontmatter_content = yaml.dump(
        frontmatter_dict,
        default_flow_style=False,
        sort_keys=False,
        indent=2,
        allow_unicode=True,  # important to preserve emojis
    )
    updated_frontmatter_content = "---\n" + updated_frontmatter_content + "---\n"

    # Replace the original frontmatter in the file content with the updated frontmatter content
    old_content = read_md(file_path)
    new_content = old_content.replace(
        parse_frontmatter(file_path)[1], updated_frontmatter_content, 1
    )
    return new_content


@beartype
def apply_diff(new_content: str | None, old_file, auto_apply: bool = False):
    """
    Apply the diff to the original file content and open the diff in meld for user review.

    :param new_content: The new content to be applied to the original file.
    :param old_file: The original file path.
    """
    if not new_content:
        return
    try:
        with NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write(new_content)
            temp_file_path = temp_file.name

        if auto_apply:
            # Automatically apply the diff to the original file
            with open(temp_file_path) as file:
                new_content = file.read()
                with open(old_file, "w") as file:
                    file.write(new_content)
            logging.info(f"Updated file {old_file} with new content without review.")
            return
        else:
            run_meld(old_file, temp_file_path)

    except Exception as e:
        logging.error(
            f"An error occurred while updating file {old_file} with new content: {e}"
        )
        logging.error("Error trace:", exc_info=True)


def run_meld(old_file, new_file):
    # Open the diff in meld for user review, and wait for the user to close the meld window
    # when the user saves within meld, the file will be updated.
    logging.info(f"Running: `meld {old_file} {new_file}`")
    subprocess.run(["meld", old_file, new_file])
    logging.info(f"User reviewed suggested diff for {old_file}.")
