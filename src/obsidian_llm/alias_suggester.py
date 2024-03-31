import logging
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

from .diff_generator import apply_diff
from .diff_generator import get_alias_diff
from .io import parse_frontmatter
from .io import enumerate_markdown_files


load_dotenv()  # Load environment variables from .env file

prefix_blacklist = [
    "(POST) ",
    "(ARTICLE) ",
    "(REVIEW) ",
    "(VIDEO) ",
    "(PODCAST) ",
    "(RECIPE) ",
    "(BOOK) ",
    "(MOVIE) ",
    "(PILLAR) ",
    "(VISION) ",
    "(PAPER) ",
    "(PROMPT) ",
    "@",
]

substring_blacklist = ["/Journal/", "/Templates/"]


def generate_all_aliases(vault_path: str):
    md_files = enumerate_markdown_files(vault_path)
    for file_path in md_files:
        # do not attempt to add aliases to files in blacklisted directories
        if any(substring in file_path for substring in substring_blacklist):
            logging.info(f"Skipping blacklisted file: {file_path}")
            continue
        # parse fpath stem as document title
        document_title = os.path.splitext(os.path.basename(file_path))[0]
        # check if document title is blacklisted
        if any(prefix in document_title.upper() for prefix in prefix_blacklist):
            logging.info(f"Skipping blacklisted file: {file_path}")
            continue

        try:
            frontmatter_dict, frontmatter_str = parse_frontmatter(file_path)
            if frontmatter_dict:
                if (
                    "processed_for" in frontmatter_dict
                    and "new_aliases" in frontmatter_dict["processed_for"]
                ):
                    logging.info(f"Skipping already processed file: {file_path}")
                    continue

                existing_aliases = frontmatter_dict.get("aliases", [])
                new_aliases = generate_alias_suggestions(
                    document_title, existing_aliases
                )

                new_content = get_alias_diff(
                    file_path,
                    new_aliases,
                    frontmatter_dict,
                )
                apply_diff(new_content, file_path)

                logging.info(
                    f"Diff generated and user decision processed for {file_path}."
                )

            else:
                continue
        except Exception as e:
            logging.error(f"An error occurred while processing file {file_path}: {e}")
            logging.error("Error trace:", exc_info=True)


def generate_alias_suggestions(document_title: str, existing_aliases=None):
    """
    Generates alias suggestions for a given document title using AutoGPT, excluding existing aliases.

    :param document_title: Title of the document for which to generate aliases.
    :param existing_aliases: List of existing aliases to exclude from the suggestions.
    :return: A list of suggested aliases or None if an error occurs or no new suggestions are made.
    """
    if existing_aliases is None:
        existing_aliases = []

    assert document_title != "", "Document title cannot be empty."

    try:
        # Load your OpenAI API key from an environment variable
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not client.api_key:
            logging.error("OPENAI_API_KEY environment variable is not set.")
            return None

        # Construct the prompt for AutoGPT
        prompt = """You are an assistant helping a user generate alias or redirect suggestions for a document title. Reasons for creating alias redirects include:

    * Alternative names redirect to the most appropriate article title (e.g., Edson Arantes do Nascimento redirects to Pelé).
    * Plurals (e.g., Greenhouse gases redirects to Greenhouse gas).
    * Closely related words (e.g., Symbiont redirects to Symbiosis).
    * Adjectives or adverbs point to noun forms (e.g., Treasonous redirects to Treason)
    * Less specific forms of names, for which the article subject is still the primary topic (e.g., Einstein redirects to Albert Einstein)
    * More specific forms of names (e.g., Articles of Confederation and Perpetual Union redirects to Articles of Confederation).
    * Abbreviations and initialisms (e.g., ADHD redirects to Attention deficit hyperactivity disorder (ADHD)).
    * Alternative spellings or punctuation. e.g., Colour redirects to Color, and Al-Jazeera redirects to Al Jazeera.
    * Representations using ASCII characters, that is, common transliterations (e.g., Pele also redirects to Pelé while Kurt Goedel and Kurt Godel redirect to Kurt Gödel).

    Suggested aliases should be new-line delimited with no additional formatting (do not number or bullet the list). If none of these reasons apply, simply reply with "None".
    The suggestions should be synonymous with the original article title. Suggest two aliases max."""

        # Send the prompt to AutoGPT
        task = f"Generate alias suggestions for the document title '{document_title}'"
        if existing_aliases:
            task += f", excluding the following existing aliases: {', '.join(existing_aliases)}"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": task,
                },
            ],
            max_tokens=50,
            n=1,
            stop=None,
            temperature=0.5,
        )

        suggestions = response.choices[0].message.content.strip()
        if suggestions.lower() == "none":
            # Short-circuit if no suggestions are generated
            logging.info(f"LLM suggested no new aliases for '{document_title}'.")
            return None

        # Extract and return the suggested aliases
        # this parsing is necessary because the LLM API doesn't always follow directions
        suggestions = suggestions.split("\n")
        # if the suggestions are numbered (e.g. "1. <item>"), remove the numbering
        suggestions = [
            re.sub(r"^\d+\.\s*", "", suggestion) for suggestion in suggestions
        ]
        # if the suggestions are bulleted (e.g. "- <item>", "* <item>"), remove the bullet
        suggestions = [
            re.sub(r"^[*-]\s*", "", suggestion) for suggestion in suggestions
        ]
        # Filter out any existing aliases from the suggestions
        filtered_suggestions = [
            suggestion
            for suggestion in suggestions
            if suggestion not in existing_aliases
        ]

        if not filtered_suggestions:
            logging.info(
                f"No new alias suggestions generated for '{document_title}' after filtering existing aliases."
            )
            return None

        logging.info(
            f"Generated aliases for '{document_title}': {filtered_suggestions}"
        )
        return filtered_suggestions
    except Exception as e:
        logging.error(f"An error occurred while generating alias suggestions: {e}")
        logging.error("Error trace:", exc_info=True)
        return None
