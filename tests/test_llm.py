import os
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from obsidian_llm.llm import OpenAI
from obsidian_llm.llm import get_oai_client


def test_get_oai_client_no_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    # Check if RuntimeError is raised when OPENAI_API_KEY is not set
    # set the environment variable to None in context
    with pytest.raises(
        RuntimeError, match="OPENAI_API_KEY environment variable is not set."
    ):
        get_oai_client()


@patch("obsidian_llm.llm.OpenAI")
def test_get_oai_client_with_api_key(mock_openai, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    mock_openai_instance = MagicMock()
    mock_openai.return_value = mock_openai_instance

    # Call the function and check if OpenAI was initialized with the correct key
    get_oai_client()
    mock_openai.assert_called_once_with(api_key="test_key")
