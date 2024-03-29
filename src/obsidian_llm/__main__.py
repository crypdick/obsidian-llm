"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Obsidian Llm."""


if __name__ == "__main__":
    main(prog_name="obsidian-llm")  # pragma: no cover
