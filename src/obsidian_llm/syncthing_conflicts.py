import logging
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
        # TODO
        # merge the original file with the conflict file using meld
        # TODO
