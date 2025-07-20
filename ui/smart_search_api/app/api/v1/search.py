import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.llm.main import get_llm_service # <-- IMPORTED
from app.llm.base import LLMService # <-- IMPORTED
from app.database import get_db
from app.core.security import get_current_user
from app.search.main import get_search_index
from app.search.base import SearchIndex
from typing import List
import random
import time

router = APIRouter()

SUMMARY_JOBS = {}


@router.post("/projects/{project_id}/search/documents", response_model=schemas.SearchResponse)
def search_documents(
        project_id: int,
        query: schemas.SearchQuery,
        current_user: models.User = Depends(get_current_user),
        search_index: SearchIndex = Depends(get_search_index),
        db: Session = Depends(get_db)
):
    raw_results = search_index.search_documents(project_id=project_id, query=query)
    persisted_documents = crud.upsert_and_save_search_results(db, results=raw_results, project_id=project_id)

    search_id = f"search-doc-{uuid.uuid4()}"
    
    # Store the project_id in the job so the poller can use it
    SUMMARY_JOBS[search_id] = {
        "project_id": project_id,
        "results_to_summarize": [doc.id for doc in raw_results],
        "summarized_ids": set(),
        "prompt": query.guidingPrompt
    }
    
    return schemas.SearchResponse(searchId=search_id, results=raw_results)

@router.post("/projects/{project_id}/search/extractions", response_model=schemas.SearchResponse)
def search_extractions(
    project_id: int,
    query: schemas.ExtractionSearchQuery,
    current_user: models.User = Depends(get_current_user),
    search_index: SearchIndex = Depends(get_search_index),
    db: Session = Depends(get_db)
):
    """
    Searches for extractions and returns them in the unified RawSearchResult format.
    """
    # --- FIX: The logic is now unified ---
    raw_results = search_index.search_extractions(project_id=project_id, query=query)
    persisted_documents = crud.upsert_and_save_search_results(db, results=raw_results, project_id=project_id)

    search_id = f"search-ext-{uuid.uuid4()}"
    SUMMARY_JOBS[search_id] = { "results_to_summarize": [ext.id for ext in persisted_documents], "summarized_ids": set(), "prompt": query.guidingPrompt }

    return schemas.SearchResponse(searchId=search_id, results=raw_results)


@router.get("/search/summary/updates/{search_id}", response_model=schemas.SummaryUpdateResponse)
def get_summary_update(
        search_id: str,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
        llm_service: LLMService = Depends(get_llm_service)
):
    if search_id not in SUMMARY_JOBS:
        raise HTTPException(status_code=404, detail="Search job not found.")
    
    job = SUMMARY_JOBS[search_id]
    
    next_doc_id = next((doc_id for doc_id in job["results_to_summarize"] if doc_id not in job["summarized_ids"]), None)
    if not next_doc_id:
        return schemas.SummaryUpdateResponse(status="complete", summary=None)
    
    # Fetch the full document from the database to pass to the LLM
    document = crud.get_document(
        db,
        doc_id=next_doc_id,
        project_id=job["project_id"],
        user_id=current_user.id
    )
    
    if not document:
        job["summarized_ids"].add(next_doc_id)  # Skip if not found
        return schemas.SummaryUpdateResponse(status="pending", summary=None)
    
    # --- REFACTORED: Call the LLM service ---
    summary_text = llm_service.generate_summary_for_document(document, job["prompt"])
    
    job["summarized_ids"].add(next_doc_id)
    summary_item = schemas.GuidedSummaryItem(docId=next_doc_id, user_id=current_user.id, summary=summary_text)
    
    return schemas.SummaryUpdateResponse(status="pending", summary=summary_item)
