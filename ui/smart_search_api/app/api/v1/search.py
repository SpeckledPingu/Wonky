import uuid
from fastapi import APIRouter, Depends, HTTPException
from app import schemas
from app import models
from app import crud
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models import User
from app.search.main import get_search_index  # <-- IMPORTED
from app.search.base import SearchIndex  # <-- IMPORTED
from app.database import get_db
import time
import random

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
    """
    Searches for documents using the abstracted search service, then immediately
    imports the results into the user's project database.
    """
    # Step 1: Get raw results from the search index (e.g., LanceDB)
    raw_results = search_index.search_documents(project_id=project_id, query=query)
    
    if not raw_results:
        return schemas.SearchResponse(searchId=f"search-doc-{uuid.uuid4()}", results=[])
    
    # Step 2: Use the new CRUD function to save these results to the database
    persisted_documents = crud.upsert_and_save_search_results(db, results=raw_results, project_id=project_id)
    
    # Step 3: Kick off the summary generation job for the newly saved documents
    search_id = f"search-doc-{uuid.uuid4()}"
    SUMMARY_JOBS[search_id] = {"results_to_summarize": [doc.id for doc in persisted_documents], "summarized_ids": set(),
                               "prompt": query.guidingPrompt}
    
    # Step 4: Return the fully-formed, database-persisted documents to the frontend
    return schemas.SearchResponse(searchId=search_id, results=persisted_documents)


@router.post("/projects/{project_id}/search/extractions", response_model=schemas.ExtractionSearchResponse)
def search_extractions(
        project_id: int,
        query: schemas.ExtractionSearchQuery,
        current_user: User = Depends(get_current_user),
        search_index: SearchIndex = Depends(get_search_index)  # <-- DEPENDENCY INJECTION
):
    """
    Searches for extractions using the abstracted search service.
    """
    results = search_index.search_extractions(project_id=project_id, query=query)
    
    search_id = f"search-ext-{uuid.uuid4()}"
    SUMMARY_JOBS[search_id] = {"results_to_summarize": [ext.source_doc_id for ext in results], "summarized_ids": set(),
                               "prompt": query.guidingPrompt}
    
    return schemas.ExtractionSearchResponse(searchId=search_id, results=results)


@router.get("/search/summary/updates/{search_id}", response_model=schemas.SummaryUpdateResponse)
def get_summary_update(search_id: str):
    if search_id not in SUMMARY_JOBS:
        raise HTTPException(status_code=404, detail="Search job not found.")
    job = SUMMARY_JOBS[search_id]
    next_doc_id = next((doc_id for doc_id in job["results_to_summarize"] if doc_id not in job["summarized_ids"]), None)
    if not next_doc_id:
        return schemas.SummaryUpdateResponse(status="complete", summary=None)
    time.sleep(random.uniform(0.5, 1.5))
    job["summarized_ids"].add(next_doc_id)
    summary_text = f"Guided by '{job['prompt']}', a key insight from '{next_doc_id}' is its connection to {random.choice(['global markets', 'recent innovations', 'policy debates'])}."
    summary_item = schemas.GuidedSummaryItem(docId=next_doc_id, summary=summary_text)
    return schemas.SummaryUpdateResponse(status="pending", summary=summary_item)
