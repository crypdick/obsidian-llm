import logging
import re

import yaml


def parse_frontmatter(file_path):
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
