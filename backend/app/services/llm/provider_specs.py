"""
Data-driven provider registry.

Adding support for a new LLM provider is a DATA change (one row in
``PROVIDER_SPECS`` below), not a code change. Every OpenAI chat-completions
compatible backend - OpenAI, Nebius, DeepSeek, OpenRouter, Groq, Together,
xAI, Mistral, Moonshot/Kimi, vLLM, LM Studio, Ollama, ... - speaks the same
wire format and differs only in a handful of fields (default base URL, whether
a key is required, etc.). So each one is described as data here and served by
the single ``OpenAICompatibleProvider`` adapter. Anthropic uses a genuinely
different SDK, so it gets its own adapter (``kind="anthropic"``).

Env-var naming convention (so a new provider needs zero new ``Settings``
fields):

    <PROVIDER>_API_KEY     e.g. DEEPSEEK_API_KEY, OPENROUTER_API_KEY
    <PROVIDER>_MODEL       e.g. DEEPSEEK_MODEL
    <PROVIDER>_BASE_URL    e.g. DEEPSEEK_BASE_URL  (override the spec default)

with a generic fallback that works for ANY selected provider:

    LLM_API_KEY  /  LLM_MODEL  /  LLM_BASE_URL

The actual precedence / resolution logic lives in ``registry._build_provider``.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderSpec:
    """How to reach one provider. Pure data - no behaviour."""

    # Which adapter serves this provider.
    #   "openai_compatible" -> OpenAICompatibleProvider (chat completions)
    #   "anthropic"         -> AnthropicProvider (Messages API)
    kind: str = "openai_compatible"

    # Default endpoint. ``None`` means "use the SDK's own default" (real OpenAI).
    base_url: str | None = None

    # A sensible default model id, used only if the user sets no model var.
    default_model: str | None = None

    # Keyless / local servers (Ollama, LM Studio, raw vLLM) don't need a real
    # key. When True and no key is supplied we send ``placeholder_key`` instead
    # of raising.
    key_optional: bool = False
    placeholder_key: str = "EMPTY"

    # Generic endpoints (the escape hatch) have no default URL, so the user
    # MUST supply one. When True we raise a clear error if none is resolved.
    require_base_url: bool = False

    # Optional explicit env-var overrides. Leave ``None`` to use the
    # ``<PROVIDER>_*`` convention derived from the provider name.
    key_env: str | None = None
    model_env: str | None = None
    base_url_env: str | None = None


# ---------------------------------------------------------------------------
# Table C - provider -> endpoint spec.
# To add a provider: add one row. To add an OpenAI-compatible provider that
# isn't listed, the caller can just use LLM_PROVIDER=openai_compatible and give
# a base URL - no edit needed at all.
# ---------------------------------------------------------------------------
PROVIDER_SPECS: dict[str, ProviderSpec] = {
    # First-party / native SDKs ------------------------------------------------
    # Real OpenAI: base_url None -> the openai SDK targets api.openai.com.
    "openai": ProviderSpec(kind="openai_compatible"),
    # Anthropic speaks a different protocol -> dedicated adapter.
    "anthropic": ProviderSpec(kind="anthropic"),

    # Hosted OpenAI-compatible gateways --------------------------------------
    "nebius": ProviderSpec(
        base_url="https://api.studio.nebius.com/v1/",
        default_model="deepseek-ai/DeepSeek-V3.2",
    ),
    "deepseek": ProviderSpec(base_url="https://api.deepseek.com"),
    "openrouter": ProviderSpec(base_url="https://openrouter.ai/api/v1"),
    "groq": ProviderSpec(base_url="https://api.groq.com/openai/v1"),
    "together": ProviderSpec(base_url="https://api.together.xyz/v1"),
    "xai": ProviderSpec(base_url="https://api.x.ai/v1"),
    "mistral": ProviderSpec(base_url="https://api.mistral.ai/v1"),
    # Moonshot / Kimi - two common names for the same service. Default to the
    # international endpoint; override with KIMI_BASE_URL / MOONSHOT_BASE_URL
    # (e.g. https://api.moonshot.cn/v1 for the China region).
    "moonshot": ProviderSpec(base_url="https://api.moonshot.ai/v1"),
    "kimi": ProviderSpec(base_url="https://api.moonshot.ai/v1"),

    # Local / self-hosted (keyless) ------------------------------------------
    "ollama": ProviderSpec(
        base_url="http://localhost:11434/v1",
        key_optional=True,
        placeholder_key="ollama",
    ),
    "lmstudio": ProviderSpec(
        base_url="http://localhost:1234/v1",
        key_optional=True,
        placeholder_key="lm-studio",
    ),
    # Raw vLLM server: you host it, so you supply the URL; key optional.
    "vllm": ProviderSpec(
        require_base_url=True,
        key_optional=True,
    ),

    # The universal escape hatch ---------------------------------------------
    # Point at ANY OpenAI-compatible endpoint by giving a base URL. Key is
    # optional (local servers) but still sent if provided (hosted relays).
    "openai_compatible": ProviderSpec(
        require_base_url=True,
        key_optional=True,
    ),
}

# Spec used for any LLM_PROVIDER value not present above: treat it as a generic
# OpenAI-compatible endpoint that requires a base URL. This means even an
# unlisted provider name works as long as the user supplies <NAME>_BASE_URL or
# LLM_BASE_URL.
GENERIC_SPEC = ProviderSpec(require_base_url=True, key_optional=True)


def get_spec(provider: str) -> ProviderSpec:
    """Return the spec for ``provider`` (falling back to the generic spec)."""
    return PROVIDER_SPECS.get(provider, GENERIC_SPEC)


def key_env_for(provider: str, spec: ProviderSpec) -> str:
    """Env var that holds this provider's API key (Table B, as data)."""
    return spec.key_env or f"{provider.upper()}_API_KEY"


def model_env_for(provider: str, spec: ProviderSpec) -> str:
    """Env var that holds this provider's model id."""
    return spec.model_env or f"{provider.upper()}_MODEL"


def base_url_env_for(provider: str, spec: ProviderSpec) -> str:
    """Env var that overrides this provider's base URL."""
    return spec.base_url_env or f"{provider.upper()}_BASE_URL"


def supported_providers() -> list[str]:
    """Names with built-in presets (for error messages / docs)."""
    return sorted(PROVIDER_SPECS.keys())
