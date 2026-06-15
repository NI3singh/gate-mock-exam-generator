"""
Resolves the single active LLM provider for this backend process.

The selection is fully data-driven (see ``provider_specs.py``): which client
class to build, the endpoint, and the API key are all derived from the
``ProviderSpec`` table plus environment variables. Adding/using a new provider
needs no edit here.

Value resolution (most specific wins):

    base_url : <PROVIDER>_BASE_URL  >  LLM_BASE_URL  >  spec.base_url  >  SDK default
    api_key  : <PROVIDER>_API_KEY   >  LLM_API_KEY   >  spec.placeholder_key (keyless)
    model    : <PROVIDER>_MODEL      >  LLM_MODEL     >  spec.default_model

Every value is read with ``settings`` taking precedence over ``os.environ`` so
that (a) the existing typed ``Settings`` fields keep working and (b) brand-new
providers resolve straight from the loaded ``.env`` with no new ``Settings``
fields. A missing required key raises ``LLMConfigurationError`` naming the exact
env var to set.
"""

import os

from app.core.config import settings
from app.services.llm.exceptions import LLMConfigurationError
from app.services.llm.provider_specs import (
    base_url_env_for,
    get_spec,
    key_env_for,
    model_env_for,
    supported_providers,
)
from app.services.llm.providers import AnthropicProvider, OpenAICompatibleProvider
from app.services.llm.types import LLMProvider

_active_provider: LLMProvider | None = None


def _read(name: str) -> str:
    """
    Read a config value by name. ``Settings`` attributes (typed, loaded from
    .env at import) take precedence; otherwise fall back to the raw environment
    so providers without a dedicated Settings field still resolve from .env.
    """
    value = getattr(settings, name, None)
    if value is None:
        value = os.environ.get(name)
    return (value or "").strip()


def _build_provider() -> LLMProvider:
    provider = (settings.LLM_PROVIDER or "nebius").strip().lower()
    spec = get_spec(provider)

    key_env = key_env_for(provider, spec)
    model_env = model_env_for(provider, spec)
    base_url_env = base_url_env_for(provider, spec)

    # --- resolve each field by precedence -----------------------------------
    api_key = _read(key_env) or _read("LLM_API_KEY")
    model = _read(model_env) or _read("LLM_MODEL") or (spec.default_model or "")
    base_url = (
        _read(base_url_env)
        or _read("LLM_BASE_URL")
        or (spec.base_url or "")
    ) or None

    # --- Anthropic (native Messages API) ------------------------------------
    if spec.kind == "anthropic":
        if not api_key:
            raise LLMConfigurationError(
                f"LLM_PROVIDER='{provider}' requires {key_env} to be set."
            )
        if not model:
            raise LLMConfigurationError(
                f"LLM_PROVIDER='{provider}' requires {model_env} to be set."
            )
        return AnthropicProvider(api_key=api_key, model=model)

    # --- OpenAI-compatible (every other provider) ---------------------------
    if spec.require_base_url and not base_url:
        raise LLMConfigurationError(
            f"LLM_PROVIDER='{provider}' requires a base URL - set "
            f"{base_url_env} (or LLM_BASE_URL) to your endpoint."
        )

    if not api_key:
        if spec.key_optional:
            api_key = spec.placeholder_key
        else:
            raise LLMConfigurationError(
                f"LLM_PROVIDER='{provider}' requires {key_env} to be set."
            )

    if not model:
        raise LLMConfigurationError(
            f"LLM_PROVIDER='{provider}' requires {model_env} (or LLM_MODEL) "
            "to be set."
        )

    return OpenAICompatibleProvider(
        name=provider,
        api_key=api_key,
        model=model,
        base_url=base_url,
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


# Re-exported for callers/tests that want the list of built-in presets.
__all__ = [
    "get_active_provider",
    "reset_provider_cache",
    "supported_providers",
]
