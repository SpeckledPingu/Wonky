from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.database import get_db

router = APIRouter()

@router.get("/projects/{project_id}/reports", response_model=List[schemas.Report])
def get_all_reports(project_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all generated reports for a specific project.
    """
    reports = crud.get_reports_by_project(db, project_id=project_id)
    return reports
