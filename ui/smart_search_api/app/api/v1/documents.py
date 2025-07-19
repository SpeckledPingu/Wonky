from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db

router = APIRouter()


@router.get("/projects/{project_id}/documents/{doc_id}", response_model=schemas.Document)
def get_document_by_id(project_id: int, doc_id: str, db: Session = Depends(get_db)):
    """
    Fetches a single document or report by its ID from the database, scoped to a project.
    """
    # First, check if the ID corresponds to a regular document
    db_doc = crud.get_document(db, doc_id=doc_id, project_id=project_id)
    if db_doc:
        return db_doc
    
    # If not found, check if it corresponds to a report in the same project
    db_report = crud.get_report(db, report_id=doc_id, project_id=project_id)
    if db_report:
        # --- FIX ---
        # When a report is found, we must correctly construct a `schemas.Document`
        # object using keyword arguments to satisfy the Pydantic model.
        report_tags = [
            schemas.Tag(id=-1, name='report'),
            schemas.Tag(id=-2, name=db_report.analysis_type)
        ]
        
        return schemas.Document(
            id=db_report.id,
            title=db_report.title,
            content=db_report.content,
            tags=report_tags,
            color='purple'
        )
    
    # If the ID is not found in either, raise a 404 error
    raise HTTPException(status_code=404, detail="Item not found in this project")


@router.put("/projects/{project_id}/documents/{doc_id}", response_model=schemas.Document)
def update_document(project_id: int, doc_id: str, doc_update: schemas.DocumentUpdateRequest,
                    db: Session = Depends(get_db)):
    """
    Updates a document's tags and/or color in the database.
    """
    db_doc = crud.update_document(db, doc_id=doc_id, project_id=project_id, doc_update=doc_update)
    if db_doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_doc
