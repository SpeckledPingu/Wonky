from abc import ABC, abstractmethod
from typing import List
from app import schemas

class SearchIndex(ABC):
    """
    Abstract base class for a search index.
    Defines the contract that all search implementations must follow.
    """

    @abstractmethod
    def search_documents(self, project_id: int, query: schemas.SearchQuery) -> List[schemas.Document]:
        """Searches for documents in the index."""
        pass

    @abstractmethod
    def search_extractions(self, project_id: int, query: schemas.ExtractionSearchQuery) -> List[schemas.Extraction]:
        """Searches for extractions in the index."""
        pass

