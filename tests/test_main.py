"""Test cases for the __main__ module."""

import pytest
from click.testing import CliRunner

from obsidian_llm import __main__


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_fails(runner: CliRunner) -> None:
    """It exits with a status code of two."""
    result = runner.invoke(__main__.main, ["--vault-path", "/path/to/fake/vault"])
    assert result.exit_code == 2
