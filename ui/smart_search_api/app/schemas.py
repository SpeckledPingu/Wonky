from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
import datetime

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
# --- NEW SCHEMA for raw, untyped search results ---
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class RawSearchResult(BaseModel):
    id: str
    title: str
    content: str
    tags: List[str] = []

class Tag(BaseSchema):
    id: int
    name: str

class Document(BaseSchema):
    id: str
    title: str
    content: str
    summary: Optional[str] = None
    tags: List[Tag] = []
    color: Optional[str] = 'default'

class DocumentUpdateRequest(BaseModel):
    tags: Optional[List[str]] = Field(None)
    color: Optional[str] = Field(None)

class Extraction(BaseSchema):
    id: str
    source_doc_id: str
    type: Literal['insight', 'policy', 'case_study']
    stance: Literal['pro', 'con', 'neutral']
    content: str

class SearchQuery(BaseModel):
    query: str
    mode: Literal['semantic', 'keyword', 'hybrid']
    guidingPrompt: Optional[str] = None

class SearchResponse(BaseModel):
    searchId: str
    results: List[RawSearchResult]

class ExtractionSearchQuery(BaseModel):
    query: str
    contentTypes: Optional[List[str]] = []
    stances: Optional[List[str]] = []
    guidingPrompt: Optional[str] = None

# The ExtractionSearchResponse is no longer needed as we use the unified SearchResponse

class GuidedSummaryItem(BaseModel):
    docId: str
    summary: str

# --- NEW Auth Schemas ---
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class Project(BaseSchema):
    id: int
    name: str
    description: Optional[str] = None # <-- ADDED
    
class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class User(BaseSchema, UserBase):
    id: int

class Token(BaseModel):
    access_token: str
    token_type: str

# --- NEW SCHEMA ---

class Tag(BaseSchema):
    id: int
    name: str

class Document(BaseSchema):
    id: str
    title: str
    content: str
    tags: List[Tag] = []
    color: Optional[str] = 'default'

class DocumentUpdateRequest(BaseModel):
    tags: Optional[List[str]] = Field(None)
    color: Optional[str] = Field(None)

class Extraction(BaseSchema):
    id: str
    source_doc_id: str
    type: Literal['insight', 'policy', 'case_study']
    stance: Literal['pro', 'con', 'neutral']
    content: str

class SearchQuery(BaseModel):
    query: str
    mode: Literal['semantic', 'keyword', 'hybrid']
    guidingPrompt: Optional[str] = None

class SearchResponse(BaseModel):
    searchId: str
    results: List[Document]

class ExtractionSearchQuery(BaseModel):
    query: str
    contentTypes: Optional[List[str]] = []
    stances: Optional[List[str]] = []
    guidingPrompt: Optional[str] = None

class ExtractionSearchResponse(BaseModel):
    searchId: str
    results: List[Extraction]

class GuidedSummaryItem(BaseModel):
    docId: str
    summary: str

class SummaryUpdateResponse(BaseModel):
    status: Literal['pending', 'complete']
    summary: Optional[GuidedSummaryItem] = None

class AddToBucketRequest(BaseModel):
    documentId: str

class RemoveFromBucketRequest(BaseModel):
    documentIds: List[str]

class ProcessingJobRequest(BaseModel):
    documentIds: List[str]
    analysisType: str
    prompt: Optional[str] = None

class ProcessingJobResponse(BaseModel):
    jobId: str
    message: str

class Report(BaseSchema):
    id: str
    title: str
    content: str
    source_documents: List[Document] = []
    analysis_type: str
    generated_at: datetime.datetime
