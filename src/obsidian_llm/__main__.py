"""Command-line interface."""

import logging
import os

import click
from dotenv import load_dotenv

from obsidian_llm.alias_suggester import generate_all_aliases
from obsidian_llm.bump_note_status import bump_all_note_status
from obsidian_llm.linkify import linkify_all_notes
from obsidian_llm.spell_check import spell_check_titles
from obsidian_llm.syncthing_conflicts import merge_syncthing_conflicts


logging.basicConfig(level=logging.INFO)

# load configuration from .env file
load_dotenv()


@click.command()
@click.argument(
    "vault_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    required=False,
)
@click.option(
    "--task",
    type=click.Choice(
        [
            "aliases",
            "bump-note-status",
            "bump-journal-status",
            "merge-syncthing-conflicts",
            "linkify",
            "spell-check-titles",
        ]
    ),
    default="aliases",
)
@click.option("--test-vault", is_flag=True, help="Run tests.")
@click.version_option()
def main(vault_path, task, test_vault) -> None:
    """Obsidian Vault Improvement Assistant."""
    if not vault_path:
        use_vault = "TEST_OBSIDIAN_VAULT_PATH" if test_vault else "OBSIDIAN_VAULT_PATH"
        logging.info(
            f"Vault path not provided. Using environment variable {use_vault}."
        )
        vault_path = os.getenv(use_vault)
        if not vault_path:
            logging.error(
                "Vault path not provided. Please provide a valid path to the vault or configure in `.env`."
            )
            return

    if task == "aliases":
        logging.info("Generating aliases")
        generate_all_aliases(vault_path)
    elif task == "bump-note-status":
        logging.info("Bumping note status")
        bump_all_note_status(vault_path)
    elif task == "merge-syncthing-conflicts":
        logging.info("Merging Syncthing conflicts")
        merge_syncthing_conflicts(vault_path)
    elif task == "linkify":
        logging.info("Linkifying notes")
        linkify_all_notes(vault_path)
    elif task == "spell-check-titles":
        logging.info("Spell checking titles")
        spell_check_titles(vault_path)
    else:
        logging.error(f"Invalid task: {task}. Please provide a valid task.")
        return


if __name__ == "__main__":
    main(prog_name="obsidian-llm")  # pragma: no cover
