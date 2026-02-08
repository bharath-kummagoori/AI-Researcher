"""
Local embedding functions using sentence-transformers (free, no API key needed).
Drop-in replacement for OpenAI embeddings used throughout the codebase.
"""
import os
import ssl
from typing import List

# Bypass SSL verification for corporate proxies/firewalls
# that intercept HTTPS with self-signed certificates
if os.environ.get('DISABLE_SSL_VERIFY', 'true').lower() in ('true', '1', 'yes'):
    os.environ.setdefault('CURL_CA_BUNDLE', '')
    os.environ.setdefault('REQUESTS_CA_BUNDLE', '')
    os.environ.setdefault('HF_HUB_DISABLE_TELEMETRY', '1')
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
    except AttributeError:
        pass

_EMBEDDER = None
_EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def get_local_embedder(model_name: str = None):
    """Get or create a singleton sentence-transformer embedder."""
    global _EMBEDDER, _EMBEDDING_MODEL_NAME
    if model_name:
        _EMBEDDING_MODEL_NAME = model_name
    if _EMBEDDER is None:
        from sentence_transformers import SentenceTransformer
        _EMBEDDER = SentenceTransformer(_EMBEDDING_MODEL_NAME)
    return _EMBEDDER


def local_embed(texts: List[str], model_name: str = None) -> List[List[float]]:
    """
    Embed a list of texts using sentence-transformers locally.
    Returns a list of embedding vectors, matching OpenAI's output format.
    """
    embedder = get_local_embedder(model_name)
    embeddings = embedder.encode(texts, show_progress_bar=False)
    return embeddings.tolist()


class LocalEmbeddingWrapper:
    """
    Wraps sentence-transformers to match OpenAI's embedding API interface.
    This allows it to be used as a drop-in replacement in CodeTreeMemory etc.
    """
    class EmbeddingData:
        def __init__(self, embedding):
            self.embedding = embedding

    class EmbeddingResponse:
        def __init__(self, data):
            self.data = data

    class Embeddings:
        def __init__(self, wrapper):
            self._wrapper = wrapper

        def create(self, input, model=None, **kwargs):
            """Matches OpenAI's embeddings.create() interface."""
            if isinstance(input, str):
                input = [input]
            embeddings = local_embed(input)
            data = [LocalEmbeddingWrapper.EmbeddingData(emb) for emb in embeddings]
            return LocalEmbeddingWrapper.EmbeddingResponse(data)

    def __init__(self, **kwargs):
        self.embeddings = self.Embeddings(self)
