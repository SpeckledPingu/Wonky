from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, declarative_base
from sqlalchemy.sql import func
# from sqlalchemy.orm import declarative_base


# class Base(DeclarativeBase):
#     pass
Base = declarative_base()

class SectionDBModel(Base):
    __tablename__ = "sections"
    pkey = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    content = Column(String)
    id = Column(String)
    document_citation = Column(String)
    chunk_position = Column(String)
    intra_chunk_position = Column(Integer)
    document_position = Column(Integer)
    document_id = Column(String)

class ChunkDBSchema(Base):
    __tablename__ = "chunks"
    pkey = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String)
    content = Column(String)
    document_citation = Column(String)
    chunk_position = Column(Integer)
    element_ids = Column(String)
    chunk_start = Column(Integer)
    chunk_end = Column(Integer)
    document_id = Column(String)
    
class DocumentDBModel(Base):
    __tablename__ = "documents"
    pkey = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String)
    type = Column(String)
    number = Column(String)
    active = Column(Boolean)
    source = Column(String)
    topics = Column(String)
    version_id = Column(String)
    date = Column(String)
    retrieved_date = Column(String)
    title = Column(String)
