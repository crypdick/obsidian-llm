from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from obsidian_llm.alias_suggester import generate_alias_suggestions


def test_generate_alias_suggestions_empty_title():
    with pytest.raises(AssertionError):
        generate_alias_suggestions("")


@patch("obsidian_llm.llm.os.getenv")
def test_generate_alias_suggestions_no_api_key(mock_getenv):
    mock_getenv.return_value = None
    with pytest.raises(RuntimeError):
        generate_alias_suggestions("test title")


@patch("obsidian_llm.llm.os.getenv")
@patch("obsidian_llm.llm.OpenAI")
def test_generate_alias_suggestions_with_existing_aliases_and_new_suggestions(
    mock_openai, mock_getenv
):
    mock_getenv.return_value = "test_api_key"
    mock_openai_instance = MagicMock()
    mock_openai.return_value = mock_openai_instance
    mock_openai_instance.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="alias3\nalias4"))]
    )
    result = generate_alias_suggestions(
        "test title", existing_aliases=["alias1", "alias2"]
    )
    assert result == ["alias3", "alias4"]


@patch("obsidian_llm.llm.os.getenv")
@patch("obsidian_llm.llm.OpenAI")
def test_generate_alias_suggestions_with_existing_aliases_and_no_new_suggestions(
    mock_openai, mock_getenv
):
    mock_getenv.return_value = "test_api_key"
    mock_openai_instance = MagicMock()
    mock_openai.return_value = mock_openai_instance
    mock_openai_instance.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="alias1\nalias2"))]
    )
    result = generate_alias_suggestions(
        "test title", existing_aliases=["alias1", "alias2"]
    )
    assert result is None


@patch("obsidian_llm.llm.os.getenv")
@patch("obsidian_llm.llm.OpenAI")
def test_generate_alias_suggestions_with_existing_aliases_and_none_suggestions(
    mock_openai, mock_getenv
):
    mock_getenv.return_value = "test_api_key"
    mock_openai_instance = MagicMock()
    mock_openai.return_value = mock_openai_instance
    mock_openai_instance.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="None"))]
    )
    result = generate_alias_suggestions(
        "test title", existing_aliases=["alias1", "alias2"]
    )
    assert result is None
