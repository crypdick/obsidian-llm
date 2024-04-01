import logging
from copy import deepcopy
from tempfile import NamedTemporaryFile

from obsidian_llm.diff_generator import apply_diff
from obsidian_llm.io import enumerate_markdown_files
from obsidian_llm.io import parse_frontmatter
from obsidian_llm.io import read_md
from obsidian_llm.llm import get_oai_client


def linkify_all_notes(vault_path):
    """
    Examins the body of all notes in the vault and suggests new WikiLinks.

    In particular, this function does not add new content to the notes, but rather
    suggests which words or phrases should be [[linked]], whether or not the target
    note exists. The suggestions are done by an LLM. The user can then review the suggestions
    and decide whether to accept, reject, or edit them.

    :param vault_path: Path to the Obsidian vault.
    """
    logging.info("Linkifying notes")
    md_files = enumerate_markdown_files(vault_path)
    for file_path in md_files:
        content = read_md(file_path)
        original_content = deepcopy(content)
        # Remove the frontmatter if it exists
        _, frontmatter_str = parse_frontmatter(file_path)
        if frontmatter_str:
            content = content.replace(frontmatter_str, "", 1)

        new_content = suggest_links_llm(content)
        new_content = frontmatter_str + new_content

def suggest_links_llm(content: str) -> str:
    """
    Suggests new WikiLinks for the given content using an LLM.

    :param content: The content of a markdown file.
    :return: The content with suggested WikiLinks.
    """
    client = get_oai_client()
    response = client.create_completion(
        prompt=f"Suggest links for the following content:\n{content}",
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7
    )
    suggestion = response.choices[0].text.strip()
    return suggestion

        if new_content != original_content:
            logging.info(f"Changes detected in {file_path}.")
            apply_diff(new_content, file_path, auto_apply=False)
