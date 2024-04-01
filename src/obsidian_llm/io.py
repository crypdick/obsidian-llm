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
    # Read the content of the file
    content = read_md(file_path)
    # Remove the frontmatter if it exists
    _, frontmatter_str = parse_frontmatter(file_path)
    if frontmatter_str:
        content = content.replace(frontmatter_str, "", 1)
    # Define the pattern to match [[wikilinks]]
    wikilink_pattern = re.compile(r"\[\[(.*?)\]\]")
    # Find all matches of the pattern
    links = wikilink_pattern.findall(content)
    logging.debug(f"Found {len(links)} links in file {file_path}.")
    return len(links)
