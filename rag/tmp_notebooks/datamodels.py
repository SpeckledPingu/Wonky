from lancedb.pydantic import Vector, LanceModel
from lancedb import pydantic as ldb_pydantic
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union

from sqlmodel import Field, Session, SQLModel, create_engine, select

class ChunkLanceModel(BaseModel):
    content: str
    type: str
    document_citation: str
    chunk_position: int
    element_ids: ldb_pydantic.List[str]
    chunk_start: int
    chunk_end: int
    vector: Vector(768)
    id: str
    document_id: str
    number: str
    active: int
    source: str
    topics: ldb_pydantic.List[str]
    version_id: str
    date: str
    retrieved_date: str
    title: str
    summary: str
    source_file: str
    type_id: str
    class Config:
        orm_mode = True
        from_attributes=True
    
class ChunkDBModel(SQLModel, table=True):
    __tablename__ = "chunks"
    p_key: Optional[int] = Field(default=None, primary_key=True)
    id: str #| None = Field(default=None, primary_key=True)
    content: str
    document_citation: str
    chunk_position: int
    element_ids: str
    chunk_start: int
    chunk_end: int
    document_id: str
    
class SectionDBModel(SQLModel, table=True):
    __tablename__ = "sections"
    p_key: Optional[int] = Field(default=None, primary_key=True)
    type: str
    content: str
    id: str #| None = Field(default=None, primary_key=True)
    document_citation: str
    chunk_position: int
    intra_chunk_position: int
    document_position: int
    document_id: str
    
    
class DocumentDBModel(SQLModel, table=True):
    __tablename__ = "documents"
    p_key: Optional[int] = Field(default=None, primary_key=True)
    id: str #| None = Field(default=None, primary_key=True)
    type: str
    number: str
    active: bool
    source: str
    topics: int
    version_id: int
    date: str
    retrieved_date: str
    title: str
    
class ExtractionDocument(BaseModel):
    id: str
    citation: str
    title: str
    text: str
    type: str
    elements: List[str]
    chunks: List[str]
    document_ids: List[str]
    run_id: str | None = ''
    additional_fields: Any | None = None
    
class ExtractionDBDocument(SQLModel, table=True):
    __tablename__ = "extractions"
    p_key: Optional[int] = Field(default=None, primary_key=True)
    id: str
    citation: str
    title: str
    text: str
    type: str
    elements: str
    chunks: str
    document_ids: str
    run_id: str | None = ''
    additional_fields: str | None = None