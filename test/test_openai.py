
import os

import pytest
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def test_openai_api_connection():
    """Verify that the OpenAI API responds successfully."""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        pytest.skip("OPENAI_API_KEY is not configured.")

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-5-mini",
        input="Reply with the word OK."
    )

    assert response.output_text
    assert isinstance(response.output_text, str)
