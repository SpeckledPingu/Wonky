from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.database import get_db
from app.core.security import get_current_user

router = APIRouter()


@router.get("/projects/{project_id}/documents/{doc_id}", response_model=schemas.Document)
def get_document_by_id(project_id: int, doc_id: str, db: Session = Depends(get_db),
                       current_user: models.User = Depends(get_current_user)):
    db_doc = crud.get_document(db, doc_id=doc_id, project_id=project_id, user_id=current_user.id)
    if db_doc:
        return db_doc
    
    db_report = crud.get_report(db, report_id=doc_id, project_id=project_id, user_id=current_user.id)
    if db_report:
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
    
    raise HTTPException(status_code=404, detail="Item not found in this project for the current user")


@router.put("/projects/{project_id}/documents/{doc_id}", response_model=schemas.Document)
def update_document(project_id: int, doc_id: str, doc_update: schemas.DocumentUpdateRequest, db: Session = Depends(get_db),
                    current_user: models.User = Depends(get_current_user)):
    db_doc = crud.update_document(db, doc_id=doc_id, project_id=project_id, doc_update=doc_update,
                                  user_id=current_user.id)
    if db_doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_doc
