import logging
import os
from functools import cache

from openai import OpenAI


@cache
def get_oai_client():

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

    client = OpenAI(api_key=api_key)
    return client


def query_llm(
    prompt: str, task: str, model: str = "gpt-3.5-turbo", client: OpenAI | None = None
) -> str:
    """
    Query the LLM API with the given prompt and return the response.

    :param prompt: The prompt to send to the LLM API.
    :param task: The task to perform with the prompt.
    :param model: The model to use for the query.
    :return: The response from the LLM API.
    """
    client = client or get_oai_client()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": task,
                },
            ],
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"An error occurred while querying the LLM: {e}")
        logging.error("Error trace:", exc_info=True)
        raise e
