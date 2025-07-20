from functools import lru_cache
from app.llm.base import LLMService
from app.llm.mock_llm import MockLLMService

@lru_cache()
def get_llm_service() -> LLMService:
    """
    Dependency injector to get the current LLM service implementation.
    To switch to a real model (e.g., OpenAI, Gemini), you would change
    this function to return a different implementation of the LLMService.
    """
    print("Initializing Mock LLM Service...")
    return MockLLMService()
