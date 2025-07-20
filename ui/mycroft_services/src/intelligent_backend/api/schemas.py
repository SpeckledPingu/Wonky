from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

# --- Insight Schemas ---

class InsightBase(BaseModel):
    """Schema for the core fields of an insight."""
    citation: str
    run_id: str
    result_id: str
    insight_type: Optional[str] = None
    insight_name: Optional[str] = None
    insight_synopsis: Optional[str] = None
    related_citations: Optional[str] = None
    insight_text: Optional[str] = None
    insight_data: Optional[str] = None
    text: Optional[str] = None

class InsightCreate(InsightBase):
    """Schema used for creating a new insight via the API."""
    pass

class Insight(InsightBase):
    """Schema used for returning an insight from the API."""
    model_config = ConfigDict(from_attributes=True)

# --- Policy Schemas ---

class PolicyBase(BaseModel):
    """Schema for the core fields of a policy."""
    citation: str
    run_id: str
    result_id: str
    source_document_id: Optional[str] = None
    policy_name: Optional[str] = None
    policy_type: Optional[str] = None
    primary_objective: Optional[str] = None
    mechanism_of_action: Optional[str] = None
    policy_details: Optional[str] = None
    key_stakeholders: Optional[str] = None
    authors_apparent_stance: Optional[str] = None
    specific_evidence: Optional[str] = None
    policy_text: Optional[str] = None
    arguments_in_favor: Optional[str] = None
    arguments_against: Optional[str] = None
    locations_in_source: Optional[str] = None

class PolicyCreate(PolicyBase):
    """Schema used for creating a new policy via the API."""
    pass

class Policy(PolicyBase):
    """Schema used for returning a policy from the API."""
    model_config = ConfigDict(from_attributes=True)

# --- Search Result Schemas ---

class SearchResultBase(BaseModel):
    result_id: str
    run_id: str
    query: Optional[str] = None

class SearchResultCreate(SearchResultBase):
    pass

class SearchResult(SearchResultBase):
    created_at: datetime
    insights: List[Insight] = []
    policies: List[Policy] = []
    model_config = ConfigDict(from_attributes=True)

# --- API-Specific Request/Response Models for Workflows ---

class ExtractionWorkflowRequest(BaseModel):
    """Updated request model for triggering an extraction workflow."""
    run_id: str = Field(..., description="The ID of the overarching run.")
    result_id: str = Field(..., description="The ID of the specific search result to process.")
    user_id: str = Field(..., description="The ID of the user initiating the request.")
    project_id: str = Field(..., description="The ID of the project this workflow belongs to.")
    # The document content would likely be fetched within the workflow
    # using the result_id, so it's not needed here directly.

class InsightExtractionResponse(BaseModel):
    """Updated response model for the insight extraction endpoint."""
    run_id: str
    result_id: str
    created_insights: List[Insight]

class PolicyExtractionResponse(BaseModel):
    """Updated response model for the policy extraction endpoint."""
    run_id: str
    result_id: str
    created_policies: List[Policy]
