"""
Nebius API client using the OpenAI Python SDK.

Base URL : https://api.tokenfactory.us-central1.nebius.com/v1/
Model    : deepseek-ai/DeepSeek-V3.2
"""

import json
import os
from typing import Any

from openai import AsyncOpenAI

NEBIUS_BASE_URL = "https://api.tokenfactory.us-central1.nebius.com/v1/"
MODEL_NAME = "deepseek-ai/DeepSeek-V3.2"


class LLMService:
    """Thin wrapper around the Nebius OpenAI-compatible API."""

    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:
        api_key = os.environ.get("NEBIUS_API_KEY")
        if not api_key:
            raise RuntimeError(
                "NEBIUS_API_KEY environment variable is not set. "
                "Set it in your .env file or environment."
            )
        if self._client is None:
            self._client = AsyncOpenAI(
                base_url=NEBIUS_BASE_URL,
                api_key=api_key,
            )
        return self._client

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """
        Send a chat completion request to Nebius DeepSeek-V3.2.
        Returns the parsed JSON from the model's response content.
        Strips markdown code fences automatically.
        """
        client = self._get_client()

        kwargs: dict[str, Any] = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": temperature,
        }

        if response_format:
            kwargs["response_format"] = response_format

        response = await client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content

        # Strip markdown code fences
        text = content.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        return json.loads(text)


# Module-level singleton
llm_service = LLMService()
