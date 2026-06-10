from app.core.config import settings
from app.services.llm.exceptions import LLMConfigurationError
from app.services.llm.providers import AnthropicProvider, OpenAICompatibleProvider
from app.services.llm.types import LLMProvider

_active_provider: LLMProvider | None = None


def _require(value: str, setting_name: str, provider: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        raise LLMConfigurationError(
            f"LLM_PROVIDER='{provider}' requires {setting_name} to be set."
        )
    return cleaned


def _build_provider() -> LLMProvider:
    provider = (settings.LLM_PROVIDER or "nebius").strip().lower()

    if provider == "nebius":
        return OpenAICompatibleProvider(
            name="nebius",
            api_key=_require(settings.NEBIUS_API_KEY, "NEBIUS_API_KEY", provider),
            base_url=_require(settings.NEBIUS_BASE_URL, "NEBIUS_BASE_URL", provider),
            model=_require(settings.NEBIUS_MODEL, "NEBIUS_MODEL", provider),
        )

    if provider == "openai":
        # Optional base_url lets this slot target any OpenAI-compatible
        # gateway (e.g. tokenlb.net). Blank → the official OpenAI endpoint.
        base_url = (settings.OPENAI_BASE_URL or "").strip() or None
        return OpenAICompatibleProvider(
            name="openai",
            api_key=_require(settings.OPENAI_API_KEY, "OPENAI_API_KEY", provider),
            model=_require(settings.OPENAI_MODEL, "OPENAI_MODEL", provider),
            base_url=base_url,
        )

    if provider == "anthropic":
        return AnthropicProvider(
            api_key=_require(settings.ANTHROPIC_API_KEY, "ANTHROPIC_API_KEY", provider),
            model=_require(settings.ANTHROPIC_MODEL, "ANTHROPIC_MODEL", provider),
        )

    raise LLMConfigurationError(
        "Invalid LLM_PROVIDER "
        f"'{settings.LLM_PROVIDER}'. Expected one of: nebius, openai, anthropic."
    )


def get_active_provider() -> LLMProvider:
    """Return the single active provider for this backend process."""
    global _active_provider
    if _active_provider is None:
        _active_provider = _build_provider()
    return _active_provider


def reset_provider_cache() -> None:
    """Reset the cached provider. Intended for tests and config reloads."""
    global _active_provider
    _active_provider = None
