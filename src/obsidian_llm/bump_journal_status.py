import logging

import click

from obsidian_llm.diff_generator import apply_diff
from obsidian_llm.diff_generator import apply_new_frontmatter
from obsidian_llm.io import list_files_with_tag
from obsidian_llm.io import parse_frontmatter
from obsidian_llm.io import read_md
from obsidian_llm.io import split_content
from obsidian_llm.llm import query_llm


incomplete_tag = "📓/🟥"
captured_tag = "📓/🟨"
processed_tag = "📓/🟩️"


def bump_journal_status(vault_path: str) -> None:
    """
    Scans all .md files in the `Journal/` path and checks whether it is incomplete (tagged with `📓/🟥️`)
    and decides whether to bump its status based on the presence of action items identified by ChatGPT.
    """

    incomplete_journal_files = list_files_with_tag(vault_path, incomplete_tag)
    incomplete_journal_files = list(set(incomplete_journal_files))

    filename_blacklist = ["Tag Taxonomy.md", "Annually/"]
    incomplete_journal_files = [
        file_path
        for file_path in incomplete_journal_files
        if not any(blacklisted in file_path for blacklisted in filename_blacklist)
    ]

    logging.info(f"Found {len(incomplete_journal_files)} incomplete journal files.")

    for file_path in incomplete_journal_files:
        process_journal_entry(file_path)

    logging.info("Journal status bumping complete.")


def process_journal_entry(file_path):

    content = read_md(file_path=file_path)
    # delete everything after the `# Morning journal` header
    content = content.split("# Morning journal")[0]
    # delete everything after `## Notes Created This Week`
    content = content.split("## Notes Created This Week")[0]
    chunks_to_send, _chunks_to_keep = split_content(content)
    if not chunks_to_send:
        logging.debug(f"No content to send to the LLM in {file_path}. Skipping.")
        action_items = "None"
    else:
        body = "\n".join(chunk for _idx, chunk in chunks_to_send)

        action_items = query_llm(
            prompt="You are an assistant that reads journal entries and extracts action items. You report the action items as a newline-delimited list. If no action items are found, respond `None`.",
            task=f"Extract action items from this journal entry:\n{body}",
        )

    if action_items.strip().lower() == "none":
        new_status = processed_tag
    else:
        # report to the user the identified action items and wait for confirmation
        # make the report pretty
        action_items = action_items.split("\n")
        action_items = "\n".join(f"- {item}" for item in action_items)
        logging.info(f"Action items identified in {file_path}:\n{action_items}")
        if click.confirm(
            "Please add the action items to your task tracker. Hit enter to continue. Use Keyboard Interrupt to stop the process."
        ):
            new_status = captured_tag

    # Update the status of the journal file
    frontmatter_dict, frontmatter_str = parse_frontmatter(file_path)
    assert (
        frontmatter_dict is not None
    ), f"Something went wrong. {file_path} has no frontmatter yet it is tagged?"
    if isinstance(frontmatter_dict["tags"], str):
        frontmatter_dict["tags"] = [frontmatter_dict["tags"]]
    frontmatter_dict["tags"].remove(incomplete_tag)
    frontmatter_dict["tags"].append(new_status)
    # note: no need to add processed_for key, since the status is already updated
    new_content = apply_new_frontmatter(frontmatter_dict, file_path)
    apply_diff(new_content=new_content, old_file=file_path, auto_apply=True)

    return new_status
