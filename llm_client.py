from __future__ import annotations

import os
from typing import Optional

from prompt_builder import SYSTEM_PROMPT, build_user_prompt


class MissingApiKeyError(RuntimeError):
    """Raised when OPENAI_API_KEY is not set."""
    pass


class SqlGenerationError(RuntimeError):
    """Raised when SQL generation fails."""
    pass


def generate_sql_from_request(
    natural_language_request: str,
    model: Optional[str] = None,
    temperature: float = 0.2,
    system_prompt: Optional[str] = None,
    examples_text: str = '',
) -> str:
    # ✅ Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise MissingApiKeyError(
            "OPENAI_API_KEY is not set. Check your .env file."
        )

    # ✅ Import OpenAI safely
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SqlGenerationError(
            "The openai package is not installed. Run: pip install openai"
        ) from exc

    client = OpenAI(api_key=api_key)

    # ✅ Use safer default model
    selected_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # ✅ Prepare system prompt
    system_input = system_prompt or SYSTEM_PROMPT
    system_text = system_input
    if examples_text:
        system_text = f"{system_input}\n\nExamples:\n{examples_text}"

    # ✅ Call OpenAI API safely
    try:
        response = client.responses.create(
            model=selected_model,
            temperature=temperature,
            input=[
                {
                    "role": "system",
                    "content": [
                        {"type": "input_text", "text": system_text}
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": build_user_prompt(natural_language_request),
                        }
                    ],
                },
            ],
        )
    except Exception as exc:
        raise SqlGenerationError(f"OpenAI API error: {exc}") from exc

    # ✅ Extract output
    output_text = getattr(response, "output_text", "").strip()

    if not output_text:
        raise SqlGenerationError("The model returned an empty response.")

    return output_text