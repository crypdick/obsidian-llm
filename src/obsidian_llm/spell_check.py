import logging
import os

from spellchecker import SpellChecker

from obsidian_llm.io import enumerate_markdown_files


def spell_check_titles(vault_path: str) -> None:
    """
    Scans all the titles of the markdown files in the given vault path and suggests misspellings.

    :param vault_path: Path to the Obsidian vault directory.
    :return: None. Outputs a report of suggested misspellings.
    """
    md_files = enumerate_markdown_files(vault_path)
    spell = SpellChecker()
    report = {}

    for file_path in md_files:
        title = (
            os.path.basename(file_path)
            .replace(".md", "")
            .replace("-", " ")
            .replace("_", " ")
        )
        # Tokenize the title into words
        words = title.split()
        # Find those words that may be misspelled
        misspelled = spell.unknown(words)
        if misspelled:
            report[file_path] = list(misspelled)

    if report:
        logging.info("Spell check report for titles:")
        for file_path, misspellings in report.items():
            logging.info(f"{file_path}: {', '.join(misspellings)}")
    else:
        logging.info("No misspellings found in titles.")
