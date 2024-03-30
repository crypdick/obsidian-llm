import logging

from obsidian_llm.markdown_enumerator import enumerate_markdown_files


def test_enumerate_markdown_files(vault_path):
    try:
        md_files = enumerate_markdown_files(vault_path)
        logging.info(f"Markdown files enumerated successfully: {md_files}")
    except Exception as e:
        logging.error("An error occurred while enumerating markdown files.")
        logging.error("Error trace:", exc_info=True)
