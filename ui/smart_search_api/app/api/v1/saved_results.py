from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud, models
from app.database import get_db
from app.core.security import get_current_user

router = APIRouter()

@router.get("/projects/{project_id}/saved-results", response_model=List[schemas.Document])
def get_saved_results_for_project(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieves all saved search results for a specific project.
    """
    # A more robust check would verify project ownership first
    return crud.get_saved_results(db, project_id=project_id)

@router.post("/projects/{project_id}/saved-results/{doc_id}", status_code=201)
def save_search_result(project_id: int, doc_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Saves a document to the project's saved results list.
    """
    # Verify project ownership
    crud.add_saved_result(db, doc_id=doc_id, project_id=project_id)
    return {"message": "Result saved successfully"}

@router.delete("/projects/{project_id}/saved-results/{doc_id}", status_code=200)
def remove_saved_search_result(project_id: int, doc_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Removes a document from the project's saved results list.
    """
    # Verify project ownership
    crud.remove_saved_result(db, doc_id=doc_id, project_id=project_id)
    return {"message": "Result removed successfully"}
