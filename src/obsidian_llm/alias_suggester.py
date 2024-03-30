import logging
import os
import re

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()  # Load environment variables from .env file


def generate_alias_suggestions(document_title, existing_aliases=None):
    """
    Generates alias suggestions for a given document title using AutoGPT, excluding existing aliases.

    :param document_title: Title of the document for which to generate aliases.
    :param existing_aliases: List of existing aliases to exclude from the suggestions.
    :return: A list of suggested aliases or None if an error occurs or no new suggestions are made.
    """
    if existing_aliases is None:
        existing_aliases = []

    try:
        # Load your OpenAI API key from an environment variable
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not client.api_key:
            logging.error("OPENAI_API_KEY environment variable is not set.")
            return None

        # Construct the prompt for AutoGPT
        prompt = f"""You are an assistant helping a user generate alias or redirect suggestions for a document title. Reasons for creating alias redirects include:

    * Alternative names redirect to the most appropriate article title (e.g., Edson Arantes do Nascimento redirects to Pelé).
    * Plurals (e.g., Greenhouse gases redirects to Greenhouse gas).
    * Closely related words (e.g., Symbiont redirects to Symbiosis).
    * Adjectives or adverbs point to noun forms (e.g., Treasonous redirects to Treason)
    * Less specific forms of names, for which the article subject is still the primary topic (e.g., Einstein redirects to Albert Einstein)
    * More specific forms of names (e.g., Articles of Confederation and Perpetual Union redirects to Articles of Confederation).
    * Abbreviations and initialisms (e.g., ADHD redirects to Attention deficit hyperactivity disorder (ADHD)).
    * Alternative spellings or punctuation. e.g., Colour redirects to Color, and Al-Jazeera redirects to Al Jazeera.
    * Representations using ASCII characters, that is, common transliterations (e.g., Pele also redirects to Pelé while Kurt Goedel and Kurt Godel redirect to Kurt Gödel).

    Suggested aliases should be new-line delimited with no additional formatting (do not number or bullet the list). If none of these reasons apply, simply reply with "None". The suggestions should be synonymous with the original article title. Suggest two aliases max. \n\nSuggested aliases:"""

        # Send the prompt to AutoGPT
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"Generate alias suggestions for the document title '{document_title}', excluding the following existing aliases: {', '.join(existing_aliases)}.",
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
            logging.info(f"No new alias suggestions generated for '{document_title}'.")
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
