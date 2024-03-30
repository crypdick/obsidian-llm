import logging
import subprocess
from tempfile import NamedTemporaryFile

import yaml

from .frontmatter_verifier import verify_frontmatter


def generate_diff_and_update(file_path, new_aliases, frontmatter_dict, content):
    """
    Generates a diff between the original markdown file and a temporary file with proposed alias additions.
    Opens the proposed diff in `meld` for user to review and accept, reject, or edit the changes.

    :param file_path: Path to the original markdown file.
    :param new_aliases: List of new aliases to be added.
    :param frontmatter_dict: Parsed frontmatter of the markdown file as a dictionary.
    :param content: The full content of the markdown file.
    """
    logging.info(
        f"Starting the diff generation process for {file_path} with new aliases: {new_aliases}"
    )
    if not new_aliases:
        logging.info(
            f"No new aliases suggested for {file_path}. Skipping diff generation."
        )
        return

    # Update the aliases in the frontmatter
    if "aliases" in frontmatter_dict:
        # Ensure no duplicates are added
        unique_new_aliases = [
            alias for alias in new_aliases if alias not in frontmatter_dict["aliases"]
        ]
        frontmatter_dict["aliases"].extend(unique_new_aliases)
    else:
        logging.info(f"No existing aliases found in {file_path}. Adding new aliases.")
        frontmatter_dict["aliases"] = new_aliases

    # Add 'processed_for' key to mark the file as processed
    if "processed_for" not in frontmatter_dict:
        frontmatter_dict["processed_for"] = []
    frontmatter_dict["processed_for"].append("new_aliases")

    # Serialize the updated frontmatter back to a YAML string
    updated_frontmatter_content = yaml.dump(
        frontmatter_dict, default_flow_style=False, sort_keys=False
    )
    updated_frontmatter_content = "---\n" + updated_frontmatter_content + "---\n"

    # Replace the original frontmatter in the file content with the updated frontmatter content
    new_content = content.replace(
        verify_frontmatter(file_path)[1], updated_frontmatter_content, 1
    )

    # Write the updated content back to the original file
    try:
        with NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write(new_content)
            temp_file_path = temp_file.name

        # Open the diff in meld for user review, and wait for the user to close the meld window
        subprocess.run(["meld", file_path, temp_file_path])
        logging.info(
            f"Updated file {file_path} with new aliases and marked as processed."
        )
    except Exception as e:
        logging.error(
            f"An error occurred while updating file {file_path} with new aliases: {e}"
        )
        logging.error("Error trace:", exc_info=True)
