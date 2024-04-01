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

        # Split the content into chunks to send to the LLM and chunks to keep as is
        chunks_to_send, chunks_to_keep = split_content(content)
        # Process chunks to send through the LLM
        processed_chunks = [suggest_links_llm(chunk) for chunk in chunks_to_send]
        # Splice the processed chunks and the chunks to keep back together
        new_content = splice_content(chunks_to_send, chunks_to_keep, processed_chunks)
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


def split_content(content: str) -> tuple:
    """
    Splits the content into chunks to send to the LLM and chunks to keep as is.

    :param content: The content of a markdown file.
    :return: A tuple containing a list of chunks to send and a list of chunks to keep.
    """
    chunks_to_send = []
    chunks_to_keep = []
    lines = content.split("\n")
    buffer = []
    for line in lines:
        if line.startswith(">"):
            if buffer:
                chunks_to_send.append("\n".join(buffer))
                buffer = []
            chunks_to_keep.append(line)
        else:
            buffer.append(line)
    if buffer:
        chunks_to_send.append("\n".join(buffer))
    return chunks_to_send, chunks_to_keep


def splice_content(chunks_to_send: list, chunks_to_keep: list, processed_chunks: list) -> str:
    """
    Splices the processed chunks and the chunks to keep back together.

    :param processed_chunks: A list of content chunks processed by the LLM.
    :param chunks_to_keep: A list of content chunks to keep as is.
    :return: The spliced content.
    """
    content = ""
    keep_index = 0
    send_index = 0
    while keep_index < len(chunks_to_keep) or send_index < len(processed_chunks):
        if keep_index < len(chunks_to_keep):
            content += chunks_to_keep[keep_index] + "\n"
            keep_index += 1
        if send_index < len(processed_chunks):
            content += processed_chunks[send_index] + "\n"
            send_index += 1
    return content.strip("\n")
    # Create an iterator for the processed chunks
    processed_chunks_iter = iter(processed_chunks)
    content = ""
    for original_chunk in chunks_to_send:
        # If the original chunk was meant to be processed, replace it with the processed chunk
        if original_chunk in chunks_to_send:
            content += next(processed_chunks_iter) + "\n"
        # If the original chunk was meant to be kept, keep it as is
        else:
            content += original_chunk + "\n"
    # Ensure that any remaining chunks to keep are added to the content
    for chunk in chunks_to_keep:
        content += chunk + "\n"
    return content.strip("\n")
