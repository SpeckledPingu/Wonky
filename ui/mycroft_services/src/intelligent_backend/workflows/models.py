from pydantic import BaseModel, Field
from typing import List, Any, Dict

# Pydantic models offer runtime type checking, validation, and serialization,
# making them more robust for API and data processing tasks compared to standard dataclasses.

class SearchDocument(BaseModel):
    """
    Pydantic model corresponding to the SearchDocument dataclass.
    This model represents a single search result document.
    """
    run_id: str
    result_id: str
    title: str
    summary: str
    source_file: str
    start_index: int
    end_index: int
    chunk_id: str
    id: str
    type: str
    typeId: str
    active: bool
    source: str
    topics: List[Any]  # Using List[Any] as the original type was a generic list
    version_id: str
    date: str
    # Using an alias to allow the field name '_distance' in the input data,
    # while having a valid Python identifier 'distance' in the model.
    distance: float = Field(..., alias="_distance")
    grounding: str = ""

    # Pydantic v2 allows configuring models using a class inside the model.
    # 'allow_population_by_field_name' allows populating the model using either
    # the field name ('distance') or its alias ('_distance').
    class Config:
        allow_population_by_field_name = True


class Insight(BaseModel):
    run_id: str
    result_id: str
    insight_type: str
    insight_name: str
    insight_synopsis: str
    related_citations: List[Any] # Using List[Any] for generic list items
    citation: str
    insight_text: str = ''
    insight_data: List[Any] = Field(default_factory=list)

class Policy(BaseModel):
    run_id: str
    result_id: str
    source_document_id: str
    citation: str
    policy_name: str
    policy_type: str
    primary_objective: str
    mechanism_of_action: str
    policy_details: str
    key_stakeholders: Dict[str, Any] # Defines a dictionary with string keys
    authors_apparent_stance: str
    specific_evidence: str
    policy_text: str = ''
    arguments_in_favor: List[str] = Field(default_factory=list)
    arguments_against: List[str] = Field(default_factory=list)
    locations_in_source: List[Dict[str, Any]] = Field(default_factory=list)

class ResearchPath(BaseModel):
    """
    Pydantic model corresponding to the ResearchPath dataclass.
    This model defines the parameters and metadata for a research run.
    """
    run_id: str
    query: str
    run_time: str
    name: str = 'default_research'
    description: str = 'the default research description'