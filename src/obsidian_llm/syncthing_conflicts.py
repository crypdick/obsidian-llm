import logging
import os
import re

from obsidian_llm.diff_generator import run_meld


def list_conflict_files(vault_path: str) -> list:
    """
    Lists all files within the given vault directory that contain Syncthing conflict markers.

    :param vault_path: Path to the vault directory.
    :return: List of paths to files that contain conflict markers.
    """
    conflict_files = []
    conflict_pattern = re.compile(r"\.sync-conflict-.*\.md$")
    for root, _, files in os.walk(vault_path):
        for file in files:
            if conflict_pattern.search(file):
                conflict_files.append(os.path.join(root, file))
    return conflict_files


def merge_syncthing_conflicts(vault_path: str) -> None:
    """
    Scans all files for Syncthing conflict markers and attempts to resolve them.

    In particular, files named `/path/to/<filename>.sync-conflict-<code>.md` will
    get merged into the original file `/path/to/<filename>.md` using the `meld` diff tool.

    :param vault_path: Path to the Obsidian vault.
    """
    logging.info("Merging Syncthing conflicts")
    sync_conflicts = list_conflict_files(vault_path)
    for conflict_file_path in sync_conflicts:
        # extract the original file path by removing everything after the .sync-conflict marker
        original_file_path = re.sub(r"\.sync-conflict-.*", "", conflict_file_path)
        # add back the .md extension
        original_file_path += ".md"

        logging.info(
            f"Original file: {original_file_path}, Conflict file: {conflict_file_path}"
        )
        run_meld(original_file_path, conflict_file_path)

        # move the conflict file to /tmp after merging
        backup_file_path = os.path.join("/tmp", os.path.basename(conflict_file_path))
        os.rename(conflict_file_path, backup_file_path)
        logging.info(f"Moved conflict file to {backup_file_path} after merging.")
