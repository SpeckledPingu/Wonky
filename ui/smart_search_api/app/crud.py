from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.dialects.sqlite import insert
from app import models, schemas
import uuid
import datetime


def get_projects_by_user(db: Session, user_id: int):
    """
    Retrieves all projects owned by a specific user.
    """
    print(user_id)
    return db.query(models.Project).filter(models.Project.user_id == user_id).all()


# === Document & Search CRUD ===
def get_document(db: Session, doc_id: str, project_id: int):
    return db.query(models.Document).filter(models.Document.id == doc_id,
                                            models.Document.project_id == project_id).first()


def search_documents(db: Session, project_id: int, query: str):
    search_term = f"%{query.lower()}%"
    return db.query(models.Document).filter(
        models.Document.project_id == project_id,
        or_(
            models.Document.title.ilike(search_term),
            models.Document.content.ilike(search_term)
        )
    ).all()


def search_extractions(db: Session, project_id: int, query: schemas.ExtractionSearchQuery):
    db_query = db.query(models.Extraction).filter(models.Extraction.project_id == project_id)
    if query.contentTypes:
        db_query = db_query.filter(models.Extraction.type.in_(query.contentTypes))
    if query.stances:
        db_query = db_query.filter(models.Extraction.stance.in_(query.stances))
    if query.query:
        search_term = f"%{query.query.lower()}%"
        db_query = db_query.filter(models.Extraction.content.ilike(search_term))
    return db_query.all()


def update_document(db: Session, doc_id: str, project_id: int, doc_update: schemas.DocumentUpdateRequest):
    db_doc = get_document(db, doc_id, project_id)
    if not db_doc:
        return None
    
    if doc_update.tags is not None:
        db_doc.tags = db.query(models.Tag).filter(models.Tag.name.in_(doc_update.tags)).all()
    
    if doc_update.color is not None:
        db_doc.color = doc_update.color
    
    db.commit()
    db.refresh(db_doc)
    return db_doc


# === Report CRUD ===
def get_report(db: Session, report_id: str, project_id: int):
    return db.query(models.Report).filter(models.Report.id == report_id, models.Report.project_id == project_id).first()


def get_reports_by_project(db: Session, project_id: int):
    return db.query(models.Report).filter(models.Report.project_id == project_id).order_by(
        models.Report.generated_at.desc()).all()


def create_report_from_job(db: Session, job_request: schemas.ProcessingJobRequest, project_id: int):
    source_docs = db.query(models.Document).filter(models.Document.id.in_(job_request.documentIds),
                                                   models.Document.project_id == project_id).all()
    
    db_report = models.Report(
        id=f"report-{uuid.uuid4()}",
        project_id=project_id,
        title=f"Analysis Report on {job_request.analysisType}",
        content=f"Generated report for prompt: '{job_request.prompt}'",
        analysis_type=job_request.analysisType,
        generated_at=datetime.datetime.now(),
        source_documents=source_docs
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


# === Processing Bucket CRUD ===
def get_bucket_items(db: Session, project_id: int):
    return db.query(models.ProcessingBucketItem.document_id).filter(
        models.ProcessingBucketItem.project_id == project_id).all()


def add_to_bucket(db: Session, doc_id: str, project_id: int):
    stmt = insert(models.ProcessingBucketItem).values(project_id=project_id, document_id=doc_id)
    stmt = stmt.on_conflict_do_nothing(index_elements=['project_id', 'document_id'])
    db.execute(stmt)
    db.commit()
    return {"status": "success"}


def remove_from_bucket(db: Session, doc_ids: list[str], project_id: int):
    db.query(models.ProcessingBucketItem).filter(
        models.ProcessingBucketItem.project_id == project_id,
        models.ProcessingBucketItem.document_id.in_(doc_ids)
    ).delete(synchronize_session=False)
    db.commit()
