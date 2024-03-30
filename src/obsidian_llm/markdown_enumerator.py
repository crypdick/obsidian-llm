import glob
import logging
import os
import traceback


def enumerate_markdown_files(vault_path):
    """
    Recursively lists all markdown (.md) files within the given Obsidian vault directory.

    :param vault_path: Path to the Obsidian vault directory.
    :return: List of paths to markdown files found within the vault.
    """
    try:
        # Construct the search pattern to match `.md` files
        search_pattern = os.path.join(vault_path, "**", "*.md")
        # Use glob to find all markdown files recursively
        md_files = glob.glob(search_pattern, recursive=True)
        # ignore files in the `.obsidian` directory or `venv` directory
        md_files = [
            file
            for file in md_files
            if ".obsidian/" not in file and "venv/" not in file
        ]
        logging.info(
            f"Found {len(md_files)} markdown files in the vault at {vault_path}"
        )
        return md_files
    except Exception as e:
        logging.error(f"An error occurred while enumerating markdown files: {e}")
        logging.error(f"Error trace: {traceback.format_exc()}")
        return []
