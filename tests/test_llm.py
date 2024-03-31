import os
from unittest.mock import patch

import pytest
from openai import OpenAI

from obsidian_llm.llm import get_oai_client


def test_get_oai_client_no_api_key():
    # Ensure the environment variable is not set
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]

    # Check if RuntimeError is raised when OPENAI_API_KEY is not set
    with pytest.raises(
        RuntimeError, match="OPENAI_API_KEY environment variable is not set."
    ):
        get_oai_client()


@patch.object(OpenAI, "__init__", return_value=None)  # Mock the OpenAI class
def test_get_oai_client_with_api_key(mock_openai):
    # Set the environment variable
    os.environ["OPENAI_API_KEY"] = "test_key"

    # Call the function and check if OpenAI was initialized with the correct key
    get_oai_client()
    mock_openai.assert_called_once_with(api_key="test_key")
