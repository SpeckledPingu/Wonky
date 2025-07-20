from functools import lru_cache
from app.search.base import SearchIndex
from app.search.lancedb_index import LanceDBIndex
from app.llm.base import LLMService
from app.llm.mock_llm import MockLLMService
from app.rag.base import RAGService
from app.rag.mock_rag import MockRAGService
from sentence_transformers import SentenceTransformer

@lru_cache()
def get_sentence_encoder():
    """Loads and provides the sentence encoder model."""
    print("Loading Sentence Encoder model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Sentence Encoder model loaded.")
    return model

@lru_cache()
def get_search_index() -> SearchIndex:
    """Provides the search index, injecting the encoder."""
    model = get_sentence_encoder()
    return LanceDBIndex(encoder=model)

@lru_cache()
def get_llm_service() -> LLMService:
    """Provides the language model service."""
    print("Initializing Mock LLM Service...")
    return MockLLMService()

@lru_cache()
def get_rag_service():
    return MockRAGService()

# @lru_cache()
# from app.rag.external_rag_service import ExternalRAGService
# def get_rag_service():
#     return ExternalRAGService()
