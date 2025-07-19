from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# --- Association Tables ---
document_tags_table = Table('document_tags', Base.metadata,
                            Column('document_id', String, ForeignKey('documents.id'), primary_key=True),
                            Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
                            )

report_sources_table = Table('report_sources', Base.metadata,
                             Column('report_id', String, ForeignKey('reports.id'), primary_key=True),
                             Column('document_id', String, ForeignKey('documents.id'), primary_key=True)
                             )


# --- NEW: Project Model ---
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", back_populates="projects")
    documents = relationship("Document", back_populates="project")
    reports = relationship("Report", back_populates="project")
    extractions = relationship("Extraction", back_populates="project")
    processing_bucket = relationship("ProcessingBucketItem", back_populates="project")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    projects = relationship("Project", back_populates="owner")


class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)  # <-- ADDED
    title = Column(String, nullable=False)
    content = Column(Text)
    color = Column(String, default='default')
    
    project = relationship("Project", back_populates="documents")
    tags = relationship("Tag", secondary=document_tags_table, back_populates="documents")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    documents = relationship("Document", secondary=document_tags_table, back_populates="tags")


class Extraction(Base):
    __tablename__ = "extractions"
    id = Column(String, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)  # <-- ADDED
    source_doc_id = Column(String, ForeignKey("documents.id"), nullable=False)
    type = Column(String, nullable=False)
    stance = Column(String, nullable=False)
    content = Column(Text)
    
    project = relationship("Project", back_populates="extractions")
    source_document = relationship("Document")


class Report(Base):
    __tablename__ = "reports"
    id = Column(String, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)  # <-- ADDED
    title = Column(String, nullable=False)
    content = Column(Text)
    analysis_type = Column(String)
    generated_at = Column(DateTime(timezone=True), nullable=False)
    
    project = relationship("Project", back_populates="reports")
    source_documents = relationship("Document", secondary=report_sources_table)


class ProcessingBucketItem(Base):
    __tablename__ = "processing_bucket_items"
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)  # <-- CHANGED
    document_id = Column(String, ForeignKey("documents.id"), primary_key=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    project = relationship("Project", back_populates="processing_bucket")
    document = relationship("Document")
