import logging
import os

from obsidian_llm.io import enumerate_markdown_files


def fix_file_names(vault_path):
    """Fix file names."""
    logging.info("Fixing file names")
    md_fpaths = enumerate_markdown_files(vault_path)
    for fpath in md_fpaths:
        # remove illegal characters that conflict with Android OS
        # e.g. ?, [, ], {, }, <, >, :, ", |, *, \
        new_file = None
        for illegal_char in [
            "?",
            "[",
            "]",
            "{",
            "}",
            "<",
            ">",
            ":",
            '"',
            "|",
            "*",
            "\\",
        ]:
            if illegal_char in fpath:
                new_file = fpath.replace(illegal_char, "")
        if new_file:
            os.rename(fpath, new_file)
            logging.info(f"Renamed {fpath} to {new_file}")
