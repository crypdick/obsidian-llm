"""Command-line interface."""

import logging

import click
from dotenv import load_dotenv

from .alias_suggester import generate_alias_suggestions
from .diff_generator import generate_diff_and_update
from .frontmatter_verifier import verify_frontmatter
from .markdown_enumerator import enumerate_markdown_files


# Ensure environment variables are loaded
load_dotenv()


@click.command()
@click.argument(
    "vault_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    required=True,
    help="Path to the vault directory. This directory must exist and be readable.",
)
@click.version_option()
def main(vault_path) -> None:
    """Obsidian Vault Improvement Assistant."""
    logging.basicConfig(level=logging.INFO)
    md_files = enumerate_markdown_files(vault_path)
    for file_path in md_files:
        try:
            content = ""
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            frontmatter_dict, frontmatter_str = verify_frontmatter(file_path)
            if frontmatter_dict:
                if (
                    "processed_for" in frontmatter_dict
                    and "new_aliases" in frontmatter_dict["processed_for"]
                ):
                    logging.info(f"Skipping already processed file: {file_path}")
                    continue
                document_title = frontmatter_dict.get("title", "")
                existing_aliases = frontmatter_dict.get("aliases", [])
                new_aliases = generate_alias_suggestions(
                    document_title, existing_aliases
                )
                if new_aliases:
                    if "processed_for" not in frontmatter_dict:
                        frontmatter_dict["processed_for"] = []
                    frontmatter_dict["processed_for"].append("new_aliases")
                    generate_diff_and_update(
                        file_path, new_aliases, frontmatter_dict, content
                    )
                    logging.info(
                        f"Diff generated and user decision processed for {file_path}."
                    )
                else:
                    logging.info(f"No new aliases suggested for {file_path}. Skipping.")
            else:
                continue
        except Exception as e:
            logging.error(f"An error occurred while processing file {file_path}: {e}")
            logging.error("Error trace:", exc_info=True)


if __name__ == "__main__":
    main(prog_name="obsidian-llm")  # pragma: no cover
