from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.database import get_db

router = APIRouter()
# This would come from an authentication system
MOCK_USER_ID = 1

@router.get("/projects", response_model=List[schemas.Project])
def get_user_projects(db: Session = Depends(get_db)):
    """
    Retrieves all projects associated with the current user.
    """
    return crud.get_projects_by_user(db, user_id=MOCK_USER_ID)
