from typing import List
from app import schemas
from app.rag.base import RAGService


class MockRAGService(RAGService):
    """
    A mock implementation of the RAGService for testing purposes.
    """
    
    def get_context_for_documents(self, documents: List[schemas.Document], query: str) -> str:
        print(f"[MockRAG] Retrieving context for {len(documents)} documents based on query: '{query}'")
        
        # Simulate context retrieval by creating a simple summary
        doc_titles = [doc.title for doc in documents]
        context = f"""
        CONTEXT RETRIEVED FOR QUERY: "{query}"
        =======================================
        The following documents were identified as relevant: {', '.join(doc_titles)}.
        - Key point from '{doc_titles[0]}': Discusses the primary subject matter.
        - Contrasting point from '{doc_titles[-1]}': Offers an alternative perspective.

        This mock context can be passed to the LLM for generation.
        """
        return context.strip()
    
    def generate_report_with_context(self, documents: List[schemas.Document], query: str) -> str:
        print(f"[MockRAG] Retrieving context for {len(documents)} documents based on query: '{query}'")
        
        # Simulate context retrieval by creating a simple summary
        doc_titles = [doc.title for doc in documents]
        context = f"""
        CONTEXT RETRIEVED FOR QUERY: "{query}"
        =======================================
        The following documents were identified as relevant: {', '.join(doc_titles)}.
        - Key point from '{doc_titles[0]}': Discusses the primary subject matter.
        - Contrasting point from '{doc_titles[-1]}': Offers an alternative perspective.

        This mock context can be passed to the LLM for generation.
        """
        return context.strip()