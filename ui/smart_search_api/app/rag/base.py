from abc import ABC, abstractmethod
from typing import List
from app import schemas

class RAGService(ABC):
    """
    Abstract base class for a Retrieval-Augmented Generation (RAG) service.
    Defines the contract for retrieving relevant context to be used by an LLM.
    """

    @abstractmethod
    def get_context_for_documents(self, documents: List[schemas.Document], query: str) -> str:
        """
        Retrieves and synthesizes relevant context from a list of documents based on a query.
        """
        pass
