import logging
import click
from obsidian_llm.diff_generator import apply_diff
from obsidian_llm.diff_generator import apply_new_frontmatter
from obsidian_llm.io import enumerate_markdown_files
from obsidian_llm.io import parse_frontmatter
from obsidian_llm.llm import query_llm

def bump_journal_status(vault_path: str) -> None:
    """
    Scans all .md files in the `Journal/` path and checks whether it is incomplete (tagged with `📓/🟥️`)
    and decides whether to bump its status based on the presence of action items identified by ChatGPT.
    """
    journal_files = [f for f in enumerate_markdown_files(vault_path) if f.startswith("Journal/")]
    incomplete_tag = "📓/🟥️"
    captured_tag = "📓/🟨"
    processed_tag = "📓/🟩️"

    for file_path in journal_files:
        frontmatter_dict, _ = parse_frontmatter(file_path)
        if frontmatter_dict and incomplete_tag in frontmatter_dict.get("tags", []):
            content = read_md(file_path)
            action_items = query_llm(content, "Extract action items")

            if action_items:
                logging.info(f"Action items found in {file_path}:")
                logging.info(action_items)
                click.prompt("Please capture the action items into your task manager and press Enter to continue")
                new_status = captured_tag
            else:
                logging.info(f"No action items found in {file_path}. Marking as processed.")
                new_status = processed_tag

            # Update the tags in the frontmatter
            frontmatter_dict["tags"] = [tag for tag in frontmatter_dict["tags"] if tag != incomplete_tag]
            frontmatter_dict["tags"].append(new_status)

            new_content = apply_new_frontmatter(frontmatter_dict, file_path)
            apply_diff(new_content, file_path, auto_apply=True)
        else:
            logging.info(f"Skipping {file_path}, not marked as incomplete or not in Journal/ path.")

    logging.info("Journal status bumping complete.")
