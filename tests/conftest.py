import pytest


@pytest.fixture
def vault_path():
    return "./test_vault"


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Remove requests.sessions.Session.request for all tests."""
    monkeypatch.delattr("requests.sessions.Session.request")


@pytest.fixture
def no_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
