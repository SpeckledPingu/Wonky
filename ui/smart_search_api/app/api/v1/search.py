import time
import uuid
import random
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db

router = APIRouter()
SUMMARY_JOBS = {}
MOCK_USER_ID = 1

# --- FIX: All endpoints are now project-specific ---
@router.post("/projects/{project_id}/search/documents", response_model=schemas.SearchResponse)
def search_documents(project_id: int, query: schemas.SearchQuery, db: Session = Depends(get_db)):
    results = crud.search_documents(db, project_id=project_id, query=query.query)
    search_id = f"search-doc-{uuid.uuid4()}"
    SUMMARY_JOBS[search_id] = { "results_to_summarize": [doc.id for doc in results], "summarized_ids": set(), "prompt": query.guidingPrompt }
    return schemas.SearchResponse(searchId=search_id, results=results)

@router.post("/projects/{project_id}/search/extractions", response_model=schemas.ExtractionSearchResponse)
def search_extractions(project_id: int, query: schemas.ExtractionSearchQuery, db: Session = Depends(get_db)):
    results = crud.search_extractions(db, project_id=project_id, query=query)
    search_id = f"search-ext-{uuid.uuid4()}"
    SUMMARY_JOBS[search_id] = { "results_to_summarize": [ext.source_doc_id for ext in results], "summarized_ids": set(), "prompt": query.guidingPrompt }
    return schemas.ExtractionSearchResponse(searchId=search_id, results=results)

# This endpoint remains global as it's job-ID specific
@router.get("/search/summary/updates/{search_id}", response_model=schemas.SummaryUpdateResponse)
def get_summary_update(search_id: str):
    # ... (logic remains the same)
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
