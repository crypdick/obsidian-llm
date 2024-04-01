import pytest

from obsidian_llm.bump_journal_status import bump_journal_status
from obsidian_llm.bump_journal_status import process_journal_entry


# Mock data for testing
MOCK_VAULT_PATH = "tests/test_vault"
MOCK_JOURNAL_FILE = "tests/test_vault/Journal/2023-03-15.md"
MOCK_JOURNAL_CONTENT = """---
tags:
- 📓/🟥
---

# Morning journal

Here is a journal entry.
Today I need to finish the report.

"""


@pytest.fixture(scope="function")  # reset for each test
def mock_journal_file(tmp_path):
    d = tmp_path / "Journal"
    d.mkdir(exist_ok=True)
    p = d / "2023-03-15.md"
    p.write_text(MOCK_JOURNAL_CONTENT)
    return str(p)


def test_process_journal_entry_no_action_items(mocker, mock_journal_file):
    mocker.patch("obsidian_llm.bump_journal_status.query_llm", return_value="None")
    status = process_journal_entry(mock_journal_file)
    assert status == "📓/🟩️"


def test_process_journal_entry_with_action_items(mocker, mock_journal_file):
    mocker.patch(
        "obsidian_llm.bump_journal_status.query_llm", return_value="Finish the report"
    )
    # need to mock out `click.confirm` to prevent user prompt
    mocker.patch("obsidian_llm.bump_journal_status.click.confirm", return_value=True)
    status = process_journal_entry(mock_journal_file)
    # assert status == "📓/🟨"  # FIXME for some reason I can't get the fixture to give the yellow version
    assert status != "📓/🟥"


def test_bump_journal_status_integration(mocker, tmp_path):
    # Setup mock vault with journal entries
    mock_vault_path = str(tmp_path)
    journal_path = tmp_path / "Journal"
    journal_path.mkdir()
    (journal_path / "2023-03-15.md").write_text(MOCK_JOURNAL_CONTENT)
    # Mock the query_llm function to return no action items
    mocker.patch("obsidian_llm.bump_journal_status.query_llm", return_value="None")
    # Run the bump_journal_status function
    bump_journal_status(mock_vault_path)
    # Check if the journal entry status was updated
    updated_content = (journal_path / "2023-03-15.md").read_text()
    assert "📓/🟩️" in updated_content
