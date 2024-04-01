import glob
import logging
import os
import re
import traceback

import yaml


def read_md(file_path: str) -> str:
    with open(file_path) as file:
        content = file.read()
    return content


def read_md_body(file_path: str) -> str:
    """
    Reads the body of the markdown file, excluding the frontmatter.

    :param file_path: Path to the markdown file.
    :return: The body content of the markdown file.
    """
    content = read_md(file_path)
    _, frontmatter_str = parse_frontmatter(file_path)
    if frontmatter_str:
        content = content.replace(frontmatter_str, "", 1)
    return content


def enumerate_markdown_files(vault_path):
    """
    Recursively lists all markdown (.md) files within the given Obsidian vault directory.

    :param vault_path: Path to the Obsidian vault directory.
    :return: List of paths to markdown files found within the vault.
    """
    banned_dirs = [".obsidian/", "venv/", "Templates/"]
    try:
        # Construct the search pattern to match `.md` files
        search_pattern = os.path.join(vault_path, "**", "*.md")
        # Use glob to find all markdown files recursively
        md_files = glob.glob(search_pattern, recursive=True)
        # ignore files in the `.obsidian` directory or `venv` directory
        md_files = [
            file
            for file in md_files
            if not any(banned_dir in file for banned_dir in banned_dirs)
        ]
        logging.info(
            f"Found {len(md_files)} markdown files in the vault at {vault_path}"
        )
        return md_files
    except Exception as e:
        logging.error(f"An error occurred while enumerating markdown files: {e}")
        logging.error(f"Error trace: {traceback.format_exc()}")
        return []


def parse_frontmatter(file_path):
    """
    Verifies if the given markdown file contains a YAML frontmatter block.

    :param file_path: Path to the markdown file.
    :return: A tuple of (frontmatter_dict, frontmatter_str) if frontmatter is present, otherwise (None, None).
    """

    try:
        with open(file_path, encoding="utf-8") as file:
            content = file.read()
            frontmatter_dict, frontmatter_str = parse_frontmatter_content(content)
            if frontmatter_dict:
                logging.debug(
                    f"Frontmatter block found and parsed successfully for {file_path}."
                )
            else:
                logging.debug(f"No frontmatter block found in {file_path}.")

            return frontmatter_dict, frontmatter_str

    except Exception as e:
        logging.error(
            "An error occurred while verifying frontmatter: %s", e, exc_info=True
        )
        return None, None


def parse_frontmatter_content(content: str):
    frontmatter_pattern = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)
    match = frontmatter_pattern.search(content)
    if match:
        frontmatter_str = match.group(0)
        frontmatter_dict = yaml.safe_load(match.group(1))
        return frontmatter_dict, frontmatter_str
    else:
        return None, None


def list_files_with_tag(vault_path: str, tag: str) -> list:
    """
    Lists all markdown files within the given Obsidian vault directory that contain the specified tag in their YAML frontmatter.

    :param vault_path: Path to the Obsidian vault directory.
    :param tag: The tag to search for in the frontmatter.
    :return: List of paths to markdown files that contain the specified tag.
    """
    tagged_files = []
    md_files = enumerate_markdown_files(vault_path)
    for file_path in md_files:
        frontmatter_dict, _ = parse_frontmatter(file_path)
        if frontmatter_dict and "tags" in frontmatter_dict:
            tags = frontmatter_dict["tags"]
            if not isinstance(tags, (list, str)):
                raise ValueError(
                    f"Tags in {file_path} must be a list or str, got {tags} of type {type(tags)}"
                )
            if isinstance(tags, list) and tag in tags:
                tagged_files.append(file_path)
            elif isinstance(tags, str) and tag == tags:
                tagged_files.append(file_path)
            else:
                logging.debug(f"Tag {tag} not found in {tags} for {file_path}.")
    logging.info(f"Found {len(tagged_files)} files tagged with {tag}.")
    return tagged_files


def count_links_in_file(file_path: str) -> int:
    """
    Counts the number of [[wikilinks]] in the body of a markdown file, excluding the frontmatter.

    :param file_path: Path to the markdown file.
    :return: The number of [[wikilinks]] found in the file.
    """
    body = read_md_body(file_path)
    # Define the pattern to match [[wikilinks]]
    wikilink_pattern = re.compile(r"\[\[(.*?)\]\]")
    # Find all matches of the pattern
    links = wikilink_pattern.findall(body)
    logging.debug(f"Found {len(links)} links in file {file_path}.")
    return len(links)


def split_content(content: str, skip_processed_for_tags: str | None = None) -> tuple:
    """
    Splits the content into chunks to send to the LLM and chunks to keep as is.

    The content is withold from the LLM:
    - YAML frontmatter
    - code blocks (lines enclosed by triple backticks)
    - quote blocks (lines starting with `>`)

    We enumerate the chunks to make it possible to splice the chunks in the right order later.

    :param content: The content of a markdown file.
    :return: A tuple containing a list of chunks to send and a list of chunks to keep.
    """
    chunks_to_send = []
    chunks_to_keep = []
    chunk_idx = 0

    def save_chunk(chunk, send):
        nonlocal chunk_idx
        if not send:
            chunks_to_keep.append((chunk_idx, chunk))
        else:
            chunks_to_send.append((chunk_idx, chunk))
        chunk_idx += 1

    # Remove the frontmatter if it exists
    frontmatter_dict, frontmatter_str = parse_frontmatter_content(content)
    if frontmatter_str:
        # check if we have already processed this file for linkification, and if so skip it
        if frontmatter_dict and "processed_for" in frontmatter_dict:
            if skip_processed_for_tags and any(
                tag in frontmatter_dict["processed_for"]
                for tag in skip_processed_for_tags
            ):
                logging.info(f"Skipping already processed file.")
                return [], []

        save_chunk(frontmatter_str, send=False)
        content = content.replace(frontmatter_str, "", 1)

    lines = content.split("\n")
    buffer = []
    for line in lines:
        # detect code blocks or block comments
        if line.strip().startswith(("```", "%%")):
            if buffer:  # reached end of code block; save the buffer as a chunk
                buffer.append(line)
                save_chunk("\n".join(buffer), send=False)
                buffer = []
            else:
                # check if this is a single line code block, e.g. ```css```
                if len(line.strip()) > 3 and line.strip().count("`") == 6:
                    save_chunk(line, send=False)
                else:  # start of code block; start buffering
                    buffer.append(line)
        elif buffer:  # inside code block; keep buffering
            buffer.append(line)
        elif line.strip() == "":
            save_chunk(line, send=False)
        elif line.strip().startswith(
            (
                # ignore diary tags
                "gratitude::",
                "dream::",
                "highlight::",
                "hope::",
                "lesson::",
                # ignore Templater code
                "{%",
                "- {{",
                "- <",
                "|",  # ignore markdown tables
                ">",  # ignore quotes
                "$$",  # ignore math blocks
                # ignore horizontal rules
                "---",
                "***",
                "___",
                "* * *",
                "- - -",
                "_ _ _",
                "![",  # ignore images or transcluded content
                "#",  # ignore headings
                # ignore URLs
                "https://",
                "http://",
                "<iframe",  # ignore iframes
                "<img",  # ignore images
                "<div",  # ignore divs
                "<span",  # ignore spans
                "<a ",  # ignore links
                "<!--",  # ignore HTML comments
                "</",  # ignore closing tags
                "* [x]",  # ignore completed tasks
            )
        ):
            save_chunk(line, send=False)
        elif len(line.strip()) < 3:  # ignore lines with less than 3 characters
            save_chunk(line, send=False)
        elif not any(char.isalpha() for char in line):
            # ignore lines with no alphabetic characters
            save_chunk(line, send=False)
        elif line.strip().startswith("[[") and line.strip().endswith("]]"):
            # ignore lines that are already wikilinks
            save_chunk(line, send=False)
        else:
            save_chunk(line, send=True)
    return chunks_to_send, chunks_to_keep


def splice_content(chunks_to_keep: list, processed_chunks: list) -> str:
    """
    Splices the processed chunks and the chunks to keep back together, preserving the original order.

    :param processed_chunks: A list of content chunks processed by the LLM.
    :param chunks_to_keep: A list of content chunks to keep as is.
    :return: The spliced content.
    """
    chunks = sorted(processed_chunks + chunks_to_keep, key=lambda x: x[0])
    new_content = "\n".join([chunk for _, chunk in chunks])
    # ensure the content ends with a newline
    if not new_content.endswith("\n"):
        new_content += "\n"
    return new_content
