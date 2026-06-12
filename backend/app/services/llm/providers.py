from typing import Any

from app.services.llm.types import LLMRequest, LLMResponse


class OpenAICompatibleProvider:
    """Adapter for OpenAI chat-completions-compatible APIs."""

    def __init__(
        self,
        *,
        name: str,
        api_key: str,
        model: str,
        base_url: str | None = None,
    ) -> None:
        self._name = name
        self._api_key = api_key
        self._model = model
        self._base_url = base_url
        self._client: Any | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def model(self) -> str:
        return self._model

    @property
    def base_url(self) -> str | None:
        return self._base_url

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                from openai import AsyncOpenAI
            except ImportError as exc:
                raise RuntimeError(
                    "The 'openai' package is required for "
                    f"LLM provider '{self.name}'. Install backend requirements."
                ) from exc

            client_kwargs: dict[str, Any] = {"api_key": self._api_key}
            if self._base_url:
                client_kwargs["base_url"] = self._base_url
            self._client = AsyncOpenAI(**client_kwargs)

        return self._client

    async def generate(self, request: LLMRequest) -> LLMResponse:
        response = await self._get_client().chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        content = response.choices[0].message.content
        usage = getattr(response, "usage", None)
        usage_data = None
        if usage is not None:
            usage_data = {
                "prompt_tokens": getattr(usage, "prompt_tokens", None),
                "completion_tokens": getattr(usage, "completion_tokens", None),
                "total_tokens": getattr(usage, "total_tokens", None),
            }

        return LLMResponse(
            text=content or "",
            provider=self.name,
            model=self.model,
            usage=usage_data,
        )


class AnthropicProvider:
    """Adapter for Anthropic Messages API."""

    def __init__(self, *, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model
        self._client: Any | None = None

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def model(self) -> str:
        return self._model

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
            except ImportError as exc:
                raise RuntimeError(
                    "The 'anthropic' package is required for "
                    "LLM provider 'anthropic'. Install backend requirements."
                ) from exc

            self._client = AsyncAnthropic(api_key=self._api_key)

        return self._client

    async def generate(self, request: LLMRequest) -> LLMResponse:
        response = await self._get_client().messages.create(
            model=self.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system=request.system_prompt,
            messages=[
                {"role": "user", "content": request.user_prompt},
            ],
        )

        text_parts = []
        for block in response.content:
            if getattr(block, "type", None) == "text":
                text_parts.append(getattr(block, "text", ""))

        usage = getattr(response, "usage", None)
        usage_data = None
        if usage is not None:
            input_tokens = getattr(usage, "input_tokens", None)
            output_tokens = getattr(usage, "output_tokens", None)
            total_tokens = None
            if input_tokens is not None and output_tokens is not None:
                total_tokens = input_tokens + output_tokens
            usage_data = {
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": total_tokens,
            }

        return LLMResponse(
            text="".join(text_parts),
            provider=self.name,
            model=self.model,
            usage=usage_data,
        )
