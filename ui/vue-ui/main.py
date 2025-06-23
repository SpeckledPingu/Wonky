# /Users/jameslittiebrant/DataspellProjects/PKMResearcher/working_folder/vue-ui/main.py
import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any  # Import Any for flexible db typing

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# ===============================================================================
# 1. PYDANTIC MODELS (Data Shapes)
# ===============================================================================

class Document(BaseModel):
    id: str = Field(default_factory=lambda: f"doc_{uuid.uuid4().hex[:8]}")
    name: str
    type: str
    publicationDate: date
    content: str
    subjects: List[str] = []
    keyPlayers: List[str] = []
    linkedDocIds: List[str] = []
    parentId: Optional[str] = None
    isHidden: bool = False  # NEW: Add visibility flag


class ResearchStream(BaseModel):
    id: str = Field(default_factory=lambda: f"rs_{uuid.uuid4().hex[:8]}")
    subject: str
    focus: str
    analysisType: str
    documents: List[Document] = []


class Project(BaseModel):
    id: str = Field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:8]}")
    name: str
    goal: str
    description: Optional[str] = None
    icon: Optional[str] = 'FilePlus'
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    researchStreams: List[ResearchStream] = []


# --- Input Models for POST/PUT requests ---

class ProjectCreate(BaseModel):
    name: str
    goal: str
    description: Optional[str] = None


class ResearchStreamCreate(BaseModel):
    subject: str
    focus: str
    analysisType: str


class DocumentCreate(BaseModel):
    name: str
    type: str
    content: str
    publicationDate: Optional[date] = None  # Optional for quick adds, defaults to today
    subjects: List[str] = []
    keyPlayers: List[str] = []
    isHidden: bool = False # NEW: Allow setting visibility o


# Models for interactive chat and actions
class ChatMessageInput(BaseModel):
    message: str
    selected_doc_ids: List[str] = []
    persona_id: Optional[str] = None
    tangent_id: Optional[str] = None
    custom_deep_dive: Optional[str] = None


class ActionInput(BaseModel):
    action_id: str
    selected_doc_ids: List[str] = []
    custom_prompt: Optional[str] = None


# NEW: Models for dynamic configuration data
class Persona(BaseModel):
    id: str = Field(default_factory=lambda: f"persona_{uuid.uuid4().hex[:8]}")
    name: str
    icon: str  # Stores the string name of the Lucide icon, e.g., "UserCog"
    promptStart: str


class Tangent(BaseModel):
    id: str = Field(default_factory=lambda: f"tangent_{uuid.uuid4().hex[:8]}")
    name: str
    icon: str  # Stores the string name of the Lucide icon, e.g., "Lightbulb"
    promptStart: str


class UserAction(BaseModel):
    id: str = Field(default_factory=lambda: f"action_{uuid.uuid4().hex[:8]}")
    name: str
    promptContent: str


# --- Response Models for specific views ---

class ProjectSummary(BaseModel):
    id: str
    name: str
    goal: str
    description: Optional[str] = None
    icon: Optional[str] = None
    date: str
    sources: int


# NEW: A response model for documents that includes their stream info
class DocumentWithStream(Document):
    streamId: str
    streamName: str


# A generic response model for assistant messages
class AssistantResponse(BaseModel):
    response_text: str


# ===============================================================================
# 2. IN-MEMORY DATABASE
# ===============================================================================

db: Dict[str, Dict[str, Any]] = {  # Changed to Any for flexibility
    "projects": {},
    "personas": {},  # New section for personas
    "tangents": {},  # New section for tangents
    "user_actions": {}  # New section for user-defined actions
}


# Pre-populate the database with more detailed mock data
def populate_mock_data():
    # Project 1 Data
    project1_streams = [
        ResearchStream(
            id='rs1',
            subject='USF History',
            focus='Legislative milestones',
            analysisType='Historical Review',
            documents=[
                Document(id='doc1a', name='Telecommunications Act of 1996 Summary.pdf', type='pdf',
                         publicationDate=date(1996, 2, 8), content='# Telecommunications Act of 1996...'),
                Document(id='doc1b', name='Early USF initiatives.docx', type='docx', publicationDate=date(1998, 5, 20),
                         content='## Early USF Initiatives...', parentId='doc1a', isHidden=True),  # Child of doc1a, now hidden
                Document(id='doc1c', name='FCC Report on USF.pdf', type='pdf', publicationDate=date(2005, 7, 1),
                         content='FCC Report...', linkedDocIds=['doc1a', 'doc1b']),  # Links to 1a and 1b
                Document(id='doc1d', name='USF High-Cost Program Analysis.docx', type='docx',
                         publicationDate=date(2002, 3, 15),
                         content='### Analysis of the High-Cost Program...', parentId='doc1b', isHidden=True), # Child of doc1b, now hidden
                Document(id='doc1e', name='E-Rate Program Overview.pdf', type='pdf', publicationDate=date(2003, 6, 1),
                         content='Summary of the E-Rate program for schools and libraries.', linkedDocIds=['doc1d'])
                # Links to 1d
            ]
        ),
        ResearchStream(
            id='rs2',
            subject='Rural Broadband Impact',
            focus='Case studies and statistics',
            analysisType='Impact Analysis',
            documents=[
                Document(id='doc2a', name='Appalachian Broadband Report.pdf', type='pdf',
                         publicationDate=date(2021, 11, 15), content='...'),
                Document(id='doc2b', name='Midwest Connectivity Status.xlsx', type='xlsx',
                         publicationDate=date(2022, 3, 1), content='...', parentId='doc2a', isHidden=True),  # Child of doc2a, now hidden
            ]
        )
    ]
    db["projects"]["1"] = Project(id="1", name="United States Universal Service Fund Overview", goal="Understand USF",
                                  description="Deep dive into USF.", icon="BarChart3", createdAt=datetime(2024, 5, 31),
                                  researchStreams=project1_streams)
    
    # Project 2 Data
    project2_streams = [
        ResearchStream(
            id='rs3',
            subject='ReConnect Program Analysis',
            focus='Funding rounds and project awards',
            analysisType='Impact Analysis',
            documents=[
                Document(id='doc3a', name='ReConnect Round 1 Awards.pdf', type='pdf',
                         publicationDate=date(2020, 1, 1), content='...'),
                Document(id='doc3b', name='ReConnect Round 2 Fact Sheet.docx', type='docx',
                         publicationDate=date(2021, 1, 1), content='...'),
                Document(id='doc3c', name='ReConnect Program Economic Impact.pdf', type='pdf',
                         publicationDate=date(2022, 1, 1), content='...'),
                Document(id='doc3d', name='ReConnect Program FAQ.html', type='html',
                         publicationDate=date(2023, 1, 1), content='...'),
            ]
        )
    ]
    db["projects"]["2"] = Project(id="2", name="USDA's ReConnect Program", goal="Analyze ReConnect",
                                  description="Expanding broadband access.", icon="Network",
                                  createdAt=datetime(2024, 5, 25), researchStreams=project2_streams)
    
    # Project 3 Data (no streams/sources)
    db["projects"]["3"] = Project(id="3", name="Untitled notebook", goal="General notes", description="",
                                  icon="FileText", createdAt=datetime(2024, 5, 25))
    
    # Project 4 Data
    project4_streams = [
        ResearchStream(
            id='rs4',
            subject='Indiana Health Law',
            focus='Statutes and forms for advance directives',
            analysisType='Legal Review',
            documents=[
                Document(id='doc4a', name='Indiana Living Will Declaration.pdf', type='pdf',
                         publicationDate=date(2019, 1, 1), content='...'),
                Document(id='doc4b', name='Power of Attorney for Health Care.docx', type='docx',
                         publicationDate=date(2019, 1, 1), content='...'),
            ]
        )
    ]
    db["projects"]["4"] = Project(id="4", name="Indiana Advance Health Directives Guide", goal="Health directives",
                                  description="Guide for Indiana.", icon="FileHeart", createdAt=datetime(2024, 5, 22),
                                  researchStreams=project4_streams)
    
    # NEW: Populate Personas
    db["personas"]["analyst"] = Persona(id='analyst', name='Policy Analyst', icon='UserCog',
                                        promptStart="As a seasoned policy analyst, let's examine this. ")
    db["personas"]["legal"] = Persona(id='legal', name='Legal Expert', icon='Scale',
                                      promptStart="From a legal perspective, considering relevant case law and statutes, ")
    db["personas"]["economist"] = Persona(id='economist', name='Economist', icon='Brain',
                                          promptStart="Analyzing the economic implications, including costs and benefits, ")
    
    # NEW: Populate Tangents
    db["tangents"]["explore"] = Tangent(id='explore', name='Explore Ideas', icon='Lightbulb',
                                        promptStart="Let's brainstorm some innovative ideas related to this topic: ")
    db["tangents"]["counterfactuals"] = Tangent(id='counterfactuals', name='Identify Counterfactuals', icon='Shuffle',
                                                promptStart="What if the key assumptions were different? Let's explore counterfactual scenarios: ")
    db["tangents"]["devilsAdvocate"] = Tangent(id='devilsAdvocate', name="Devil's Advocate", icon='EyeOff',
                                               promptStart="Playing devil's advocate, what are the strongest arguments against this? ")
    
    # NEW: Populate User Actions
    db["user_actions"]["userAction1"] = UserAction(id='userAction1', name='Analyze Fiscal Impact (Custom)',
                                                   promptContent='System: You are an economist... Analysis: Analyze the fiscal impact of the selected documents focusing on budget neutrality.')
    db["user_actions"]["userAction2"] = UserAction(id='userAction2', name='Identify Public Sentiment Trends',
                                                   promptContent='System: You are a social media analyst... Analysis: Identify public sentiment trends related to the core topics in the selected documents.')


populate_mock_data()

# ===============================================================================
# 3. FASTAPI APPLICATION
# ===============================================================================

app = FastAPI(
    title="Research Workspace API",
    description="API for the Vue-based research workspace application.",
    version="1.0.0"
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Helper Functions ---
def get_all_documents_for_project(project_id: str) -> List[Dict[str, Any]]:
    """Flattens all documents from all streams in a project and adds stream info."""
    project = db["projects"].get(project_id)
    if not project:
        return []
    
    all_docs = []
    for stream in project.researchStreams:
        for doc in stream.documents:
            doc_dict = doc.model_dump()
            # Convert date to string for JSON compatibility if needed, Pydantic handles it
            doc_dict["streamId"] = stream.id
            doc_dict["streamName"] = stream.subject
            all_docs.append(doc_dict)
    return all_docs


# ===============================================================================
# 4. API ENDPOINTS
# ===============================================================================

@app.get("/")
def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"message": "Welcome to the Research Workspace API!"}


# --- Project Endpoints ---

@app.get("/api/projects", response_model=List[ProjectSummary])
def get_all_projects():
    """
    Gets a list of all projects, summarized for the ProjectsView.
    """
    summaries = []
    sorted_projects = sorted(db["projects"].values(), key=lambda p: p.createdAt, reverse=True)
    for project in sorted_projects:
        sources_count = sum(len(s.documents) for s in project.researchStreams)
        summary = ProjectSummary(
            id=project.id,
            name=project.name,
            goal=project.goal,
            description=project.description,
            icon=project.icon,
            date=project.createdAt.strftime('%B %d, %Y'),
            sources=sources_count
        )
        summaries.append(summary)
    return summaries


@app.post("/api/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(project_data: ProjectCreate):
    """
    Creates a new project.
    """
    new_project = Project(**project_data.model_dump())
    db["projects"][new_project.id] = new_project
    return new_project


@app.get("/api/projects/{project_id}", response_model=Project)
def get_project_by_id(project_id: str):
    """
    Retrieves a single project by its ID.
    """
    project = db["projects"].get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# --- Research Stream Endpoints ---

@app.get("/api/projects/{project_id}/streams", response_model=List[ResearchStream])
def get_project_streams(project_id: str):
    """
    Gets all research streams for a specific project.
    """
    project = db["projects"].get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.researchStreams


@app.post("/api/projects/{project_id}/streams", response_model=ResearchStream, status_code=status.HTTP_201_CREATED)
def add_stream_to_project(project_id: str, stream_data: ResearchStreamCreate):
    """
    Adds a new research stream to a project.
    """
    project = db["projects"].get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    new_stream = ResearchStream(**stream_data.model_dump())
    project.researchStreams.append(new_stream)
    return new_stream


@app.delete("/api/projects/{project_id}/streams/{stream_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stream_from_project(project_id: str, stream_id: str):
    """
    Deletes a research stream from a project.
    """
    project = db["projects"].get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    initial_length = len(project.researchStreams)
    project.researchStreams = [s for s in project.researchStreams if s.id != stream_id]
    
    if len(project.researchStreams) == initial_length:
        raise HTTPException(status_code=404, detail="Research stream not found in this project")
    
    return


# --- Document Endpoints ---

@app.post("/api/projects/{project_id}/streams/{stream_id}/documents", response_model=Document,
          status_code=status.HTTP_201_CREATED)
def add_document_to_stream(project_id: str, stream_id: str, doc_data: DocumentCreate):
    """
    Adds a new document to a specific research stream within a project.
    """
    project = db["projects"].get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    stream = next((s for s in project.researchStreams if s.id == stream_id), None)
    if not stream:
        raise HTTPException(status_code=404, detail="Research stream not found in this project")
    
    if doc_data.publicationDate is None:
        doc_data.publicationDate = date.today()
    
    new_document = Document(**doc_data.model_dump())
    stream.documents.append(new_document)
    
    return new_document


# NEW: Endpoint for document hierarchy
@app.get("/api/projects/{project_id}/documents/{document_id}/hierarchy", response_model=List[DocumentWithStream])
def get_document_hierarchy(project_id: str, document_id: str):
    """
    Gets a document and all its related documents (parents, children, linked).
    """
    all_docs_with_stream_info = get_all_documents_for_project(project_id)
    if not all_docs_with_stream_info:
        raise HTTPException(status_code=404, detail="Project not found or has no documents")
    
    all_docs_map = {doc['id']: doc for doc in all_docs_with_stream_info}
    
    root_doc = all_docs_map.get(document_id)
    if not root_doc:
        raise HTTPException(status_code=404, detail="Root document not found in this project")
    
    related_docs_map = {document_id: root_doc}
    
    # 1. Traverse up to find all parents
    current = root_doc
    while current and current.get('parentId'):
        parent_id = current.get('parentId')
        if parent_id in all_docs_map and parent_id not in related_docs_map:
            parent_doc = all_docs_map[parent_id]
            related_docs_map[parent_id] = parent_doc
            current = parent_doc
        else:
            break  # Stop if parent not found or already added (cycle)
    
    # 2. Find all direct children of the root document
    for doc in all_docs_with_stream_info:
        if doc.get('parentId') == document_id:
            related_docs_map[doc['id']] = doc
    
    # 3. Find all documents linked from the root document
    if root_doc.get('linkedDocIds'):
        for linked_id in root_doc.get('linkedDocIds'):
            if linked_id in all_docs_map:
                related_docs_map[linked_id] = all_docs_map[linked_id]
    
    # 4. Find all documents that link TO the root document
    for doc in all_docs_with_stream_info:
        if document_id in doc.get('linkedDocIds', []):
            related_docs_map[doc['id']] = doc
    
    return list(related_docs_map.values())


# ===============================================================================
# 5. INTERACTION ENDPOINTS (Chat, Actions)
# ===============================================================================

# --- Mock Data for Action Responses ---
mock_action_responses = {
    "executiveSummary": "Generating a comprehensive executive summary based on the {count} selected document(s)...",
    "whatsMissing": "Analyzing the selected documents to identify gaps and unanswered questions...",
    "keyStakeholders": "Identifying key stakeholders, their positions, and their influence based on the provided texts...",
    "policyMemo": "Drafting a policy memo structure. Please review and provide further details.",
    "comparePolicies": "Setting up a comparison framework for the policies outlined in the selected documents...",
    "legislativeHistory": "Summarizing the legislative history. This may take a moment...",
    "extractStatistics": "Extracting key statistics and data points from the documents...",
    "generateAudio": "Audio summary generation has been queued. This feature is a mock-up.",
    # User actions will now be fetched dynamically, but their IDs might still be used here
    "userAction1": "Running custom action 'Analyze Fiscal Impact' on {count} document(s).",
    "userAction2": "Running custom action 'Identify Public Sentiment Trends' on {count} document(s)."
}


@app.post("/api/projects/{project_id}/actions/run", response_model=AssistantResponse)
def run_action(project_id: str, action_data: ActionInput):
    """
    Simulates running a pre-defined or user-defined research action.
    """
    project = db["projects"].get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    doc_count = len(action_data.selected_doc_ids)
    response_template = mock_action_responses.get(action_data.action_id, "Unknown action requested.")
    
    response_text = response_template.format(count=doc_count)
    if doc_count == 0 and action_data.action_id not in ['generateAudio']:
        response_text += " (Warning: No documents were selected for this action)."
    
    return AssistantResponse(response_text=response_text)


@app.post("/api/projects/{project_id}/chat", response_model=AssistantResponse)
def handle_chat_message(project_id: str, chat_data: ChatMessageInput):
    """
    Simulates a chat response from the assistant.
    """
    project = db["projects"].get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    doc_count = len(chat_data.selected_doc_ids)
    message = chat_data.message.lower()
    response_text = ""
    
    # Handle guided chat context
    if chat_data.persona_id:
        persona = db["personas"].get(chat_data.persona_id)
        if persona:
            response_text += f"[Persona: {persona.name}] "
    if chat_data.tangent_id:
        tangent = db["tangents"].get(chat_data.tangent_id)
        if tangent:
            response_text += f"[Tangent: {tangent.name}] "
    if chat_data.custom_deep_dive:
        response_text += f"Initiating a deep dive on '{chat_data.custom_deep_dive}'. "
    
    # Simple keyword-based logic for chat
    if "summary" in message or "summarize" in message:
        if doc_count > 0:
            response_text += f"Based on the {doc_count} selected documents, here is a brief summary..."
        else:
            response_text += "Please select some documents first if you'd like a summary of them."
    elif "hello" in message or "hi" in message:
        response_text += "Hello! How can I assist you with your research today?"
    else:
        response_text += f"I've received your message. "
        if doc_count > 0:
            response_text += f"I will take the {doc_count} selected document(s) into consideration."
        else:
            response_text += "I am ready for your next instruction."
    
    return AssistantResponse(response_text=response_text)


# NEW: Endpoints for dynamic configuration data
@app.get("/api/personas", response_model=List[Persona])
def get_all_personas():
    """Retrieves all available personas."""
    return list(db["personas"].values())


@app.get("/api/tangents", response_model=List[Tangent])
def get_all_tangents():
    """Retrieves all available tangents."""
    return list(db["tangents"].values())


@app.get("/api/user-actions", response_model=List[UserAction])
def get_all_user_actions():
    """Retrieves all available user-defined actions."""
    return list(db["user_actions"].values())