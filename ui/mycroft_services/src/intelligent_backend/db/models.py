from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func


# Define a Base class for declarative models
class Base(DeclarativeBase):
    pass


class SearchResult(Base):
    """
    SQLAlchemy model for search results, referenced by insights and policies.
    This is a placeholder based on the foreign key references in your DDL.
    """
    __tablename__ = "search_results"
    
    # Assuming result_id is the primary key for this table.
    result_id = Column(String, primary_key=True, index=True)
    run_id = Column(String, nullable=False, index=True)
    query = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    insights = relationship("Insight", back_populates="search_result")
    policies = relationship("Policy", back_populates="search_result")


class Insight(Base):
    """
    SQLAlchemy model representing the 'insights' table.
    """
    __tablename__ = "insights"
    
    citation = Column(Text, primary_key=True)
    run_id = Column(Text, nullable=False)
    result_id = Column(Text, ForeignKey("search_results.result_id"), nullable=False)
    insight_type = Column(Text)
    insight_name = Column(Text)
    insight_synopsis = Column(Text)
    related_citations = Column(Text)
    insight_text = Column(Text)
    insight_data = Column(Text)
    text = Column(Text)
    
    # Relationship
    search_result = relationship("SearchResult", back_populates="insights")


class Policy(Base):
    """
    SQLAlchemy model representing the 'policies' table.
    """
    __tablename__ = "policies"
    
    citation = Column(Text, primary_key=True)
    run_id = Column(Text, nullable=False)
    result_id = Column(Text, ForeignKey("search_results.result_id"), nullable=False)
    source_document_id = Column(Text)
    policy_name = Column(Text)
    policy_type = Column(Text)
    primary_objective = Column(Text)
    mechanism_of_action = Column(Text)
    policy_details = Column(Text)
    key_stakeholders = Column(Text)
    authors_apparent_stance = Column(Text)
    specific_evidence = Column(Text)
    policy_text = Column(Text)
    arguments_in_favor = Column(Text)
    arguments_against = Column(Text)
    locations_in_source = Column(Text)
    
    # Relationship
    search_result = relationship("SearchResult", back_populates="policies")
