from abc import ABC, abstractmethod
from typing import List
from app import schemas, models

class LLMService(ABC):
    """
    Abstract base class for a Language Model service.
    Defines the contract that all LLM implementations must follow.
    """

    @abstractmethod
    def generate_summary_for_document(self, document: models.Document, guiding_prompt: str) -> str:
        """Generates a short, guided summary for a single document."""
        pass

    @abstractmethod
    def generate_report_from_documents(self, documents: List[models.Document], job_request: schemas.ProcessingJobRequest) -> str:
        """Generates a full report from a list of documents based on a job request."""
        pass
