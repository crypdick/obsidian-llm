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
        corrections = {word: spell.correction(word) for word in misspelled}
        if corrections:
            report[file_path] = corrections

    # Format and output the report
    if len(report) > 0:
        logging.info("Spell check report for titles:\n")
        for file_path, corrections in report.items():
            corrections_str = ', '.join([f"{mispelled} --> {corrected}" for mispelled, corrected in corrections.items()])
            logging.info(f"{file_path}:\n  {corrections_str}\n")
    else:
        logging.info("No misspellings found in titles.")
