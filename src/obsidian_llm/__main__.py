"""Command-line interface."""

import logging
import os

import click
from dotenv import load_dotenv

from obsidian_llm.alias_suggester import generate_all_aliases


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
    "-t",
    type=click.Choice(["aliases"]),
    default="aliases",
)
@click.version_option()
def main(vault_path, task) -> None:
    """Obsidian Vault Improvement Assistant."""
    if not vault_path:
        logging.info(
            "Vault path not provided. Using environment variable OBSIDIAN_VAULT_PATH."
        )
        vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
        if not vault_path:
            logging.error(
                "Vault path not provided. Please provide a valid path to the vault."
            )
            return

    if task == "aliases":
        generate_all_aliases(vault_path)
    else:
        logging.error(f"Invalid task: {task}. Please provide a valid task.")
        return


if __name__ == "__main__":
    main(prog_name="obsidian-llm")  # pragma: no cover
