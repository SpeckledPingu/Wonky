from burr.core import State, Application, ApplicationBuilder, action
from burr.core.action import Result
from sqlalchemy.orm import Session
from typing import List

from intelligent_backend.db import crud
from intelligent_backend.db.session import SessionLocal
from intelligent_backend.workflows.models import SearchDocument, Policy
from rag.ingestion.core_extractions import policies


# --- State Definition ---

class PolicyExtractionState(State):
    """Defines the state for the policy extraction workflow."""
    
    # Input fields
    document_id: int
    user_id: str
    project_id: str
    
    # Internal processing fields
    document: Policy
    
    # Output fields
    policies: list = []
    error_message: str = ""


# --- Action Definitions ---

@action(reads=["document_id"], writes=["document", "error_message"])
def load_document_content(state: PolicyExtractionState) -> PolicyExtractionState:
    """Loads the document content from the database."""
    db: Session = SessionLocal()
    try:
        document = crud.get_document_by_id(db, document_id=state.document_id)
        document = convert_json_to_search_document(document)
        if not document:
            state.error_message = f"Document with ID {state.document_id} not found."
            return state
        
        state.document = document
        return state
    finally:
        db.close()
        return state


def convert_json_to_search_document(document):
    return SearchDocument()


@action(reads=["document"], writes=["policies"])
def extract_policies_from_text(state: PolicyExtractionState, prompts: dict, config: dict) -> PolicyExtractionState:
    extracted_policies = policies.extract_policies(search_document=state.document,
                                extraction_prompt=prompts.get('extract_prompt'),
                                # conn=conn,
                                temperature=config.get('temperature'),
                                max_tokens=config.get('max_tokens'),
                                citation_prefix=config.get('citation_prefix'),
                                citation_hash_length=config.get('citation_hash_length')
                                )
    state.policies = extracted_policies
    return state


@action(reads=["policies", "document_id"], writes=[])
def save_policies_to_db(state: PolicyExtractionState) -> PolicyExtractionState:
    """Saves the extracted policies back to the database."""
    if not state.policies:
        return state  # Nothing to save
    
    db: Session = SessionLocal()
    try:
        crud.bulk_create_policies(db, policies=state.policies, document_id=state.document_id)
        print(f"Successfully saved {len(state.policies)} policies to the database.")
        return state
    finally:
        db.close()
        return state


# --- Application Builder ---

def create_policy_extraction_application() -> Application:
    """Builds and returns the Burr application for policy extraction."""
    return (
        ApplicationBuilder()
        .with_state(PolicyExtractionState)
        .with_actions(
            load_document=load_document_content,
            extract_policies_from_text=extract_policies_from_text,
            save_policies_to_db=save_policies_to_db,
        )
        .with_entrypoint("load_document")
        .with_transitions(
            ("load_document", "extract_policies_from_text", lambda s: not s["error_message"]),
            ("extract_policies_from_text", "save_policies_to_db"),
        )
        .build()
    )
