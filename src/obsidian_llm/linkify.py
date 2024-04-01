import logging
import random
from copy import deepcopy

from obsidian_llm.diff_generator import apply_diff
from obsidian_llm.io import enumerate_markdown_files
from obsidian_llm.io import parse_frontmatter
from obsidian_llm.io import read_md
from obsidian_llm.llm import get_oai_client
from obsidian_llm.llm import query_llm


def linkify_all_notes(vault_path):
    """
    Examines the body of all notes in the vault and suggests new wikilinks.

    In particular, this function does not add new content to the notes, but rather
    suggests which words or phrases should be [[linked]], whether or not the target
    note exists. The suggestions are done by an LLM. The user can then review the suggestions
    and decide whether to accept, reject, or edit them.

    :param vault_path: Path to the Obsidian vault.
    """
    logging.info("Linkifying notes")
    md_files = enumerate_markdown_files(vault_path)
    # shuffle the files to avoid repeating the same order
    random.shuffle(md_files)
    for file_path in md_files:
        content = read_md(file_path)
        original_content = deepcopy(content)
        # Remove the frontmatter if it exists
        _, frontmatter_str = parse_frontmatter(file_path)
        if frontmatter_str:
            content = content.replace(frontmatter_str, "", 1)
        else:
            frontmatter_str = ""

        new_content = suggest_links_llm(content)
        new_content = frontmatter_str + new_content
        # check if the content ends with a newline, and if not, add one
        if not new_content.endswith("\n"):
            new_content += "\n"

        if new_content != original_content:
            logging.info(f"Changes detected in {file_path}. Applying diff.")
            apply_diff(new_content=new_content, old_file=file_path, auto_apply=False)
        else:
            logging.info(f"No changes detected in {file_path}. Skipping.")


def suggest_links_llm(content: str) -> str:
    """
    Suggests new wikilinks for the given content using an LLM.

    :param content: The content of a markdown file.
    :return: The content with suggested wikilinks.
    """
    client = get_oai_client()
    prompt = """You are an assistant that helps add missing wikilinks. You should not change the meaning of the content or expand upon the content.

    Guidelines:
    - Add wikilinks to salient terms, phrases, or concepts
    - Do NOT modify existing wikilinks! Ignore them. Only suggest new wikilinks.
    - Do NOT suggest external links, only internal (wiki) links
    - Personal names are prefixed with an '@' symbol, e.g. '[[@John Doe]]'
    - Book titles are prefixed with a '(BOOK) ', e.g. '[[(BOOK) Moby Dick]]'
    - Article titles should follow Wikipedia article title conventions
    - Only pipe the link to relabel the link, e.g. use [[apple]] instead of [[apple|apple]]
    - Do NOT modify code blocks or inline code
    - Do not wrap your response in triple backticks
    """
    task = "wikilink this content: ```\n" + content + "\n```"
    response = query_llm(prompt=prompt, task=task, client=client)
    return response
