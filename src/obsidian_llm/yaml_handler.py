import logging

import yaml


def parse_yaml_frontmatter(file_content):
    """
    Parses the YAML frontmatter from a markdown file content.

    :param file_content: The content of the markdown file.
    :return: A tuple of (frontmatter_dict, frontmatter_str) if frontmatter is found, otherwise (None, None).
    """
    try:
        frontmatter_start = file_content.find("---")
        frontmatter_end = file_content.find("---", frontmatter_start + 3)
        if frontmatter_start != -1 and frontmatter_end != -1:
            frontmatter_str = file_content[frontmatter_start : frontmatter_end + 3]
            frontmatter_dict = yaml.safe_load(
                file_content[frontmatter_start + 3 : frontmatter_end]
            )
            logging.info("YAML frontmatter parsed successfully.")
            return frontmatter_dict, frontmatter_str
        else:
            logging.info("No YAML frontmatter found.")
            return None, None
    except Exception as e:
        logging.error("An error occurred while parsing YAML frontmatter.")
        logging.error("Error trace:", exc_info=True)
        return None, None


def update_aliases(frontmatter_dict, new_aliases):
    """
    Updates the aliases in the frontmatter dictionary with new aliases.

    :param frontmatter_dict: The frontmatter dictionary.
    :param new_aliases: List of new aliases to be added.
    :return: Updated frontmatter dictionary.
    """
    try:
        if "aliases" in frontmatter_dict:
            existing_aliases = frontmatter_dict["aliases"]
            if not isinstance(existing_aliases, list):
                existing_aliases = [existing_aliases]
            updated_aliases = list(set(existing_aliases + new_aliases))
        else:
            updated_aliases = new_aliases

        frontmatter_dict["aliases"] = updated_aliases
        logging.info("Aliases updated successfully in the frontmatter dictionary.")
        return frontmatter_dict
    except Exception as e:
        logging.error(
            "An error occurred while updating aliases in the frontmatter dictionary."
        )
        logging.error("Error trace:", exc_info=True)
        return frontmatter_dict


def serialize_yaml_frontmatter(frontmatter_dict):
    """
    Serializes the frontmatter dictionary back to a YAML string.

    :param frontmatter_dict: The frontmatter dictionary to be serialized.
    :return: Serialized YAML string.
    """
    try:
        yaml_str = yaml.dump(
            frontmatter_dict, default_flow_style=False, sort_keys=False
        )
        yaml_str = "---\n" + yaml_str + "---\n"
        logging.info("Frontmatter dictionary serialized to YAML string successfully.")
        return yaml_str
    except Exception as e:
        logging.error(
            "An error occurred while serializing the frontmatter dictionary to YAML string."
        )
        logging.error("Error trace:", exc_info=True)
        return ""
