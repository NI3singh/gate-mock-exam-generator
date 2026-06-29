"""
Local text embeddings for PYQ retrieval.

Uses a sentence-transformers model (default all-MiniLM-L6-v2, 384-dim — matching
the `vector(384)` columns). The model is lazy-loaded once and cached. If the
library or model is unavailable, callers degrade gracefully (no embeddings) so
exam generation never crashes just because embeddings are missing.
"""

import logging
import threading

from app.core.config import settings

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 384

_model = None
_model_lock = threading.Lock()
_load_failed = False


def _get_model():
    global _model, _load_failed
    if _model is not None or _load_failed:
        return _model
    with _model_lock:
        if _model is None and not _load_failed:
            try:
                from sentence_transformers import SentenceTransformer

                logger.info("Loading embedding model %s ...", settings.EMBEDDING_MODEL)
                _model = SentenceTransformer(settings.EMBEDDING_MODEL)
                logger.info("Embedding model ready.")
            except Exception as exc:  # noqa: BLE001
                _load_failed = True
                logger.warning(
                    "Embedding model unavailable (%s). PYQ grounding/loading will "
                    "be skipped. Install with: pip install sentence-transformers",
                    exc,
                )
    return _model


def embeddings_available() -> bool:
    """True if the embedding model loaded successfully."""
    return _get_model() is not None


def embed_texts(texts: list[str]) -> list[list[float]] | None:
    """Embed a batch of texts (L2-normalized). Returns None if unavailable."""
    model = _get_model()
    if model is None:
        return None
    vectors = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    return [v.tolist() for v in vectors]


def embed_text(text: str) -> list[float] | None:
    """Embed a single text. Returns None if unavailable."""
    result = embed_texts([text])
    return result[0] if result else None
