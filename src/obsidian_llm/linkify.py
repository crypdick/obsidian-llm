import logging
import random
from copy import deepcopy

from obsidian_llm.diff_generator import add_processed_for_key
from obsidian_llm.diff_generator import apply_diff
from obsidian_llm.io import enumerate_markdown_files
from obsidian_llm.io import read_md
from obsidian_llm.io import splice_content
from obsidian_llm.io import split_content
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

        # Split the content into chunks to send to the LLM and chunks to keep as is
        chunks_to_send, chunks_to_keep = split_content(
            content, skip_processed_for_tags="linkify"
        )
        if not chunks_to_send:
            # this can happen if the file only has ineligible content, or if it has already been processed
            logging.debug(f"No content to send to the LLM in {file_path}. Skipping.")
            continue
        # Process chunks to send through the LLM, keeping track of the original indices
        processed_chunks = []
        logging.info(f"Processing {len(chunks_to_send)} chunks in {file_path}.")
        for idx, chunk in chunks_to_send:
            processed_chunk = suggest_links_llm(chunk)
            processed_chunks.append((idx, processed_chunk))

        # Splice the processed chunks and the chunks to keep back together
        new_content = splice_content(chunks_to_keep, processed_chunks)

        if new_content != original_content:
            logging.info(f"Changes detected in {file_path}. Applying diff.")
            apply_diff(new_content=new_content, old_file=file_path, auto_apply=False)
        else:
            logging.info(f"No changes detected in {file_path}. Skipping.")
        add_processed_for_key(file_path, "linkify")

    logging.info(f"Linkification completed for {len(md_files)} notes.")


def suggest_links_llm(content: str) -> str:
    """
    Suggests new wikilinks for the given content using an LLM.

    :param content: The content of a markdown file.
    :return: The content with suggested wikilinks.
    """
    client = get_oai_client()
    # note: we already filter out code blocks, quote blocks, front matter, etc. in split_content
    prompt = """You are an assistant that helps add missing wikilinks. You should not change the meaning of the content or expand upon the content.

    Guidelines:
    - Add wikilinks to salient terms, phrases, or concepts
    - Do NOT edit existing wikilinks! Ignore them. Only suggest new wikilinks.
    - Do NOT suggest external links, only internal (wiki) links
    - Personal names are prefixed with an '@' symbol, e.g. '[[@John Doe]]'
    - Book titles are prefixed with a '(BOOK) ', e.g. '[[(BOOK) Moby Dick]]'
    - Article titles should follow Wikipedia article title conventions
    - Only pipe the link to relabel a link, e.g. use simply [[apple]] instead of [[apple|apple]]
    - Do NOT edit `inline code`
    - Avoid repeatedly linking to the same target article
    """
    task = f"wikilink this content:\n{content}\n"
    response = query_llm(prompt=prompt, task=task, client=client)
    return response
