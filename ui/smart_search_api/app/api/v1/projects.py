from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud, models
from app.database import get_db
from app.core.security import get_current_user

router = APIRouter()

@router.get("/projects", response_model=List[schemas.Project])
def get_user_projects(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieves all projects associated with the current user.
    """
    return crud.get_projects_by_user(db, user_id=current_user.id)

# --- NEW ENDPOINT ---
@router.post("/projects", response_model=schemas.Project, status_code=201)
def create_new_project(project: schemas.ProjectCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Creates a new project for the currently authenticated user.
    """
    return crud.create_project(db=db, project=project, user_id=current_user.id)

