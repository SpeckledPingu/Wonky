from functools import lru_cache
from app.search.base import SearchIndex
from app.search.lancedb_index import LanceDBIndex
from sentence_transformers import SentenceTransformer

# In a real app, you might use a config setting to determine which index to use.
# SEARCH_ENGINE = settings.SEARCH_ENGINE

@lru_cache() # Caches the model so it's only loaded into memory once
def get_sentence_encoder():
    """
    Dependency to load and provide the sentence encoder model.
    Using a popular, lightweight model suitable for general purpose tasks.
    """
    print("Loading Sentence Encoder model...")
    model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', device='mps', trust_remote_code=True)
    print("Sentence Encoder model loaded.")
    return model

@lru_cache() # Caches the index instance
def get_search_index() -> SearchIndex:
    """
    Dependency to get the current search index implementation.
    It now also handles injecting the sentence encoder model into the index.
    """
    model = get_sentence_encoder()
    return LanceDBIndex(encoder=model)
