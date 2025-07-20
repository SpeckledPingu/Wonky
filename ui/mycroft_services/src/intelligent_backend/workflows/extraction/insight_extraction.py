from burr.core import State, Application, ApplicationBuilder, action
from burr.core.action import Result
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from intelligent_backend.db import crud
from intelligent_backend.db.session import SessionLocal
from intelligent_backend.workflows.models import SearchDocument, Insight

from rag.ingestion.core_extractions import insights

# --- Data Models ---

class InsightExtractionState(State):
    """Defines the state for the insight extraction workflow."""
    
    # Input fields
    document_id: int
    user_id: str
    project_id: str
    
    # Internal processing fields
    document: SearchDocument
    
    # Output fields
    insights: list = []
    identified_insights: list = []
    error_message: str = ""

@action(reads=["document_id"], writes=["document", "error_message"])
def load_document_content(state: InsightExtractionState) -> InsightExtractionState:
    """Loads the document content from the database."""
    db: Session = SessionLocal()
    try:
        document = crud.get_document_by_id(db, document_id=state.document_id)
        document = convert_json_to_search_document(document)
        if not document:
            state.error_message=f"Document with ID {state.document_id} not found."
            return state
        
        state.document=document
        return state
    finally:
        db.close()
        return state
        
def convert_json_to_search_document(document):
    return SearchDocument()


@action(reads=["document"], writes=["identified_insights"])
def identify_insights_in_text(state: InsightExtractionState, prompts: dict, config: dict) -> InsightExtractionState:
    identified_insights = insights.identify_insights(state.document,
                                                     prompts.get('identify_prompt'),
                                                     citation_prefix=config.get('citation_prefix'),
                                                     citation_hash_length=config.get('citation_hash_length')
                                                     )
    state.identified_insights=identified_insights
    return state

@action(reads=["identified_insights","document"], writes=["insights"])
def extract_insights_from_text(state: InsightExtractionState, prompts: dict, config: dict) -> InsightExtractionState:
    print(f"LLM Call: Extracting insights for project {state.project_id}...")

    extracted_insights = insights.extract_insights(state.identified_insights,
                                search_document=state.document,
                                prompt=prompts.get('extract_prompt'),
                                batch_size=config.get('batch_size'),
                                temperature=config.get('temperature_extraction'),
                                max_tokens=config.get('max_tokens'))
    state.insights=extracted_insights
    return state


@action(reads=["insights", "document_id"], writes=[])
def save_insights_to_db(state: InsightExtractionState) -> InsightExtractionState:
    """Saves the extracted insights back to the database."""
    if not state.insights:
        return state  # Nothing to save
    
    db: Session = SessionLocal()
    try:
        crud.bulk_create_insights(db, insights=state.insights, document_id=state.document_id)
        print(f"Successfully saved {len(state.get('insights'))} insights to the database.")
        return state
    finally:
        db.close()
        return state


# --- Application Builder ---

def create_insight_extraction_application() -> Application:
    return (
        ApplicationBuilder()
        .with_state(InsightExtractionState)
        .with_actions(
            load_document=load_document_content,
            identify_insights_in_text=identify_insights_in_text,
            extract_insights_from_text=extract_insights_from_text,
            save_insights_to_db=save_insights_to_db,
        )
        .with_entrypoint("load_document")
        .with_transitions(
            ("load_document", "identify_insights_in_text", lambda s: not s["error_message"]),
            ("identify_insights_in_text", "extract_insights_from_text")
            ("extract_insights_from_text", "save_insights_to_db"),
        )
        .build()
    )
