import logging
import re

import yaml


def verify_frontmatter(file_path):
    """
    Verifies if the given markdown file contains a YAML frontmatter block.

    :param file_path: Path to the markdown file.
    :return: A tuple of (frontmatter_dict, frontmatter_str) if frontmatter is present, otherwise (None, None).
    """
    frontmatter_pattern = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)

    try:
        with open(file_path, encoding="utf-8") as file:
            content = file.read()
            match = frontmatter_pattern.search(content)
            if match:
                frontmatter_str = match.group(0)
                frontmatter_dict = yaml.safe_load(match.group(1))
                logging.info("Frontmatter block found and parsed successfully.")
                return frontmatter_dict, frontmatter_str
            else:
                logging.info(f"No frontmatter block found in {file_path}.")
                return None, None
    except Exception as e:
        logging.error(
            "An error occurred while verifying frontmatter: %s", e, exc_info=True
        )
        return None, None


def parse_frontmatter(frontmatter_section: str) -> dict:
    """Given a YAML frontmatter section from verify_frontmatter, parse it into a dictionary."""

    try:
        frontmatter_dict = yaml.safe_load(frontmatter_section)
        logging.info("Parsed frontmatter successfully: %s", frontmatter_dict)
        return frontmatter_dict
    except Exception as e:
        logging.error(
            "An error occurred while parsing frontmatter: %s", e, exc_info=True
        )
        return {}
