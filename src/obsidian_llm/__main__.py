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
    type=click.Choice(["aliases"]),
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
        generate_all_aliases(vault_path)
    else:
        logging.error(f"Invalid task: {task}. Please provide a valid task.")
        return


if __name__ == "__main__":
    main(prog_name="obsidian-llm")  # pragma: no cover
