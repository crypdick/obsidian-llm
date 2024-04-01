import logging
import os
import re

def list_conflict_files(vault_path: str) -> list:
    """
    Lists all files within the given vault directory that contain Syncthing conflict markers.

    :param vault_path: Path to the vault directory.
    :return: List of paths to files that contain conflict markers.
    """
    conflict_files = []
    conflict_pattern = re.compile(r'\.sync-conflict-\d{8}-\d{6}\.md$')
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
    for file_path in sync_conflicts:
        # extract the original file path by removing everything after the .sync-conflict marker
        original_file_path = re.sub(r'\.sync-conflict-\d{8}-\d{6}', '', file_path)
        # TODO: Implement the merging logic
        logging.info(f"Original file: {original_file_path}, Conflict file: {file_path}")
        # TODO
        # merge the original file with the conflict file using meld
        # TODO
