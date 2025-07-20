from sqlalchemy.orm import Session
from . import models
from ..api import schemas


# --- SearchResult CRUD ---

def get_search_result(db: Session, result_id: str) -> models.SearchResult | None:
    """Retrieves a SearchResult by its ID."""
    return db.query(models.SearchResult).filter(models.SearchResult.result_id == result_id).first()


def create_search_result(db: Session, search_result: schemas.SearchResultCreate) -> models.SearchResult:
    """Creates a new SearchResult record."""
    db_obj = models.SearchResult(**search_result.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# --- Insight CRUD ---

def get_insight(db: Session, citation: str) -> models.Insight | None:
    """Retrieves an Insight by its citation (primary key)."""
    return db.query(models.Insight).filter(models.Insight.citation == citation).first()


def create_insight(db: Session, insight: schemas.InsightCreate) -> models.Insight:
    """Creates a new Insight record."""
    # Ensure the parent SearchResult exists
    parent_search_result = get_search_result(db, result_id=insight.result_id)
    if not parent_search_result:
        # In a real system, you might raise an error or create it.
        # For now, we'll create a placeholder.
        print(f"Warning: SearchResult {insight.result_id} not found. Creating a placeholder.")
        create_search_result(db, schemas.SearchResultCreate(result_id=insight.result_id, run_id=insight.run_id))
    
    db_obj = models.Insight(**insight.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# --- Policy CRUD ---

def get_policy(db: Session, citation: str) -> models.Policy | None:
    """Retrieves a Policy by its citation (primary key)."""
    return db.query(models.Policy).filter(models.Policy.citation == citation).first()


def create_policy(db: Session, policy: schemas.PolicyCreate) -> models.Policy:
    """Creates a new Policy record."""
    # Ensure the parent SearchResult exists
    parent_search_result = get_search_result(db, result_id=policy.result_id)
    if not parent_search_result:
        print(f"Warning: SearchResult {policy.result_id} not found. Creating a placeholder.")
        create_search_result(db, schemas.SearchResultCreate(result_id=policy.result_id, run_id=policy.run_id))
    
    db_obj = models.Policy(**policy.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
