import time
import uuid
import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.database import get_db
from app.core.security import get_current_user
from typing import List

router = APIRouter()


@router.get("/projects/{project_id}/processing/bucket", response_model=List[str])
def get_processing_bucket(project_id: int, db: Session = Depends(get_db),
                          current_user: models.User = Depends(get_current_user)):
    # Add verification that the project belongs to the user
    items = crud.get_bucket_items(db, project_id=project_id)
    return [item[0] for item in items]


@router.post("/projects/{project_id}/processing/bucket", status_code=201)
def add_to_processing_bucket(project_id: int, request: schemas.AddToBucketRequest, db: Session = Depends(get_db),
                             current_user: models.User = Depends(get_current_user)):
    # Add verification
    crud.add_to_bucket(db, doc_id=request.documentId, project_id=project_id)
    return {"message": "Document added to processing bucket"}


@router.delete("/projects/{project_id}/processing/bucket", status_code=200)
def remove_from_processing_bucket(project_id: int, request: schemas.RemoveFromBucketRequest,
                                  db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Add verification
    crud.remove_from_bucket(db, doc_ids=request.documentIds, project_id=project_id)
    return {"message": f"Successfully removed items."}


@router.post("/projects/{project_id}/processing/jobs", response_model=schemas.ProcessingJobResponse)
def submit_processing_job(project_id: int, job_request: schemas.ProcessingJobRequest, db: Session = Depends(get_db),
                          current_user: models.User = Depends(get_current_user)):
    # Add verification
    time.sleep(1)
    try:
        report = crud.create_report_from_job(db, job_request=job_request, project_id=project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create report: {e}")
    
    return schemas.ProcessingJobResponse(
        jobId=report.id,
        message="Processing job completed successfully."
    )
