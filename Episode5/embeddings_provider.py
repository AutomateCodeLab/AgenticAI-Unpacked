#!/usr/bin/env python3
"""
embeddings_provider.py — pluggable text embeddings for semantic memory.

Auto-detects a real embeddings API vs. a zero-setup local fallback:

    OPENAI_API_KEY set  -> real OpenAI embeddings (text-embedding-3-small, dim 1536)
    otherwise           -> local hashing bag-of-words embedding (dim 256, no API key)

Semantic recall works either way — the real API is just more accurate at
matching different words with the same meaning. This mirrors llm_provider.py's
auto-detection style, but embeddings and the chat LLM are independent: you can
run the LLM on Anthropic while still getting real OpenAI embeddings, as long
as OPENAI_API_KEY is set.

Dimension-mismatch handling: switching providers between runs changes the
vector dimension (256 vs 1536) for any already-stored memory. Each stored
memory is tagged with the "embed_model" that produced it. When a memory's tag
doesn't match the CURRENTLY active model, retrieve_memories() re-embeds it
with the current model before scoring — so a provider switch never crashes on
a shape mismatch or silently returns nothing; it just re-computes on next use.
"""

import hashlib
import os
import re

import numpy as np
from dotenv import load_dotenv

load_dotenv()

LOCAL_DIM = 256

if os.environ.get("OPENAI_API_KEY", "").strip():
    from openai import OpenAI
    _client = OpenAI()
    EMBED_PROVIDER = "openai"
    EMBED_MODEL_NAME = "text-embedding-3-small"
    EMBED_DIM = 1536
    # Real embedding models spread short, topically-different factual
    # sentences across a much LOWER raw cosine-similarity range than the
    # local hash embedding does — even genuinely relevant memories about the
    # same user can score well under 0.1. A threshold tuned for one embedding
    # space does NOT transfer to another; always calibrate empirically per
    # model rather than reusing a "reasonable-looking" constant.
    SIMILARITY_THRESHOLD = 0.04
else:
    _client = None
    EMBED_PROVIDER = "local"
    EMBED_MODEL_NAME = "hash256"
    EMBED_DIM = LOCAL_DIM
    SIMILARITY_THRESHOLD = 0.15

EMBED_MODEL = f"{EMBED_PROVIDER}:{EMBED_MODEL_NAME}"


def _local_embed(text: str) -> np.ndarray:
    """Cheap local embedding: hashed bag-of-words. No API key needed — good
    enough to demo semantic retrieval, just less precise than a real model."""
    vec = np.zeros(LOCAL_DIM, dtype=np.float32)
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        h = int(hashlib.md5(token.encode()).hexdigest(), 16)
        vec[h % LOCAL_DIM] += 1.0
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


def embed(text: str) -> np.ndarray:
    """Turn text into a vector using whichever provider is currently active."""
    if EMBED_PROVIDER == "openai":
        try:
            resp = _client.embeddings.create(model=EMBED_MODEL_NAME, input=text)
            return np.array(resp.data[0].embedding, dtype=np.float32)
        except Exception:
            # If the real API hiccups, don't crash memory — fall back for this call.
            return _local_embed(text)
    return _local_embed(text)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom else 0.0
