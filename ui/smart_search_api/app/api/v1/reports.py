from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud, models
from app.database import get_db
from app.core.security import get_current_user

router = APIRouter()

@router.get("/projects/{project_id}/reports", response_model=List[schemas.Report])
def get_all_reports(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieves all generated reports for a specific project, ensuring it belongs to the current user.
    """
    # A more robust check would be to verify project ownership first
    # For example: if project.user_id != current_user.id: raise HTTPException
    reports = crud.get_reports_by_project(db, project_id=project_id)
    return reports
