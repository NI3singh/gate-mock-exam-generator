from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMRequest:
    """Provider-neutral request shape used by the exam generator."""

    system_prompt: str
    user_prompt: str
    temperature: float
    max_tokens: int


@dataclass(frozen=True)
class LLMResponse:
    """Provider-neutral response metadata."""

    text: str
    provider: str
    model: str
    usage: dict[str, int | None] | None = None


class LLMProvider(Protocol):
    """Minimal interface each provider adapter must implement."""

    @property
    def name(self) -> str:
        ...

    @property
    def model(self) -> str:
        ...

    async def generate(self, request: LLMRequest) -> LLMResponse:
        ...
