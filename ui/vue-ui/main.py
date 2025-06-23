# /Users/jameslittiebrant/DataspellProjects/PKMResearcher/working_folder/vue-ui/main.py
import uuid
import sqlite3
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# --- Configuration ---
DATABASE_FILE = "research_workspace.db"


# ===============================================================================
# 1. PYDANTIC MODELS (Data Shapes) - These remain the same
# ===============================================================================

class Document(BaseModel):
    id: str
    name: str
    type: str
    publicationDate: Optional[date]
    content: str
    subjects: List[str] = []
    keyPlayers: List[str] = []
    linkedDocIds: List[str] = []
    parentId: Optional[str] = None
    isHidden: bool = False


class ResearchStream(BaseModel):
    id: str
    subject: str
    focus: str
    analysisType: str
    documents: List[Document] = []


class Project(BaseModel):
    id: str
    name: str
    goal: str
    description: Optional[str] = None
    icon: Optional[str] = 'FilePlus'
    createdAt: datetime
    researchStreams: List[ResearchStream] = []


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
    publicationDate: Optional[date] = None
    subjects: List[str] = []
    keyPlayers: List[str] = []
    isHidden: bool = False


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


class Persona(BaseModel):
    id: str
    name: str
    icon: str
    promptStart: str


class Tangent(BaseModel):
    id: str
    name: str
    icon: str
    promptStart: str


class UserAction(BaseModel):
    id: str
    name: str
    promptContent: str


class ProjectSummary(BaseModel):
    id: str
    name: str
    goal: str
    description: Optional[str] = None
    icon: Optional[str] = None
    date: str
    sources: int


class DocumentWithStream(Document):
    streamId: str
    streamName: str


class AssistantResponse(BaseModel):
    response_text: str


# ===============================================================================
# 2. DATABASE CONNECTION
# ===============================================================================

def get_db():
    """FastAPI dependency to get a DB connection for each request."""
    # The `check_same_thread=False` is the key to allowing SQLite to work
    # with FastAPI's threading model. It's safe because each request
    # gets its own connection from this dependency.
    db = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON;")  # Enforce foreign key constraints
    try:
        yield db
    finally:
        db.close()


# ===============================================================================
# 3. FASTAPI APPLICATION
# ===============================================================================

app = FastAPI(
    title="Research Workspace API",
    description="API for the Vue-based research workspace application.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===============================================================================
# 4. HELPER FUNCTIONS FOR DATA MAPPING
# ===============================================================================

def _map_document_row_to_document_and_stream_id(row: sqlite3.Row) -> tuple[Document, str]:
    """
    Maps a raw SQLite row for a document to a Pydantic Document model
    and returns its stream_id for efficient assignment.
    """
    doc = Document(
        id=row['id'],
        name=row['name'],
        type=row['type'],
        publicationDate=date.fromisoformat(row['publication_date']) if row['publication_date'] else None,
        content=row['content'],
        isHidden=bool(row['is_hidden']),
        parentId=row['parent_id'],
        subjects=[],  # These will be populated in bulk later
        keyPlayers=[],  # These will be populated in bulk later
        linkedDocIds=[]  # These will be populated in bulk later
    )
    return doc, row['stream_id']


# ===============================================================================
# 5. API ENDPOINTS
# ===============================================================================

@app.get("/")
def read_root():
    return {"message": "Welcome to the Research Workspace API!"}

# --- Project Endpoints ---

@app.get("/api/projects", response_model=List[ProjectSummary])
def get_all_projects(db: sqlite3.Connection = Depends(get_db)):
    """Gets a list of all projects, summarized for the ProjectsView."""
    cursor = db.cursor()
    query = """
        SELECT p.id, p.name, p.goal, p.description, p.icon, p.created_at, COUNT(d.id) as sources
        FROM projects p
        LEFT JOIN research_streams rs ON p.id = rs.project_id
        LEFT JOIN documents d ON rs.id = d.stream_id
        GROUP BY p.id
        ORDER BY p.created_at DESC
    """
    projects_rows = cursor.execute(query).fetchall()

    summaries = []
    for row in projects_rows:
        # Handle 'Z' suffix for UTC timestamps
        created_at_dt = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
        summary = ProjectSummary(
            id=row['id'],
            name=row['name'],
            goal=row['goal'],
            description=row['description'],
            icon=row['icon'],
            date=created_at_dt.strftime('%B %d, %Y'),
            sources=row['sources']
        )
        summaries.append(summary)
    return summaries


@app.post("/api/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(project_data: ProjectCreate, db: sqlite3.Connection = Depends(get_db)):
    """Creates a new project."""
    new_project_id = f"proj_{uuid.uuid4().hex[:8]}"
    created_at = datetime.utcnow()

    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO projects (id, name, goal, description, icon, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (new_project_id, project_data.name, project_data.goal, project_data.description, 'FilePlus',
         created_at.isoformat())
    )
    db.commit()

    return Project(
        id=new_project_id,
        name=project_data.name,
        goal=project_data.goal,
        description=project_data.description,
        icon='FilePlus',
        createdAt=created_at,
        researchStreams=[]  # Newly created project has no streams yet
    )


@app.get("/api/projects/{project_id}", response_model=Project)
def get_project_by_id(project_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Retrieves a single project by its ID, including all nested data."""
    cursor = db.cursor()

    # 1. Get Project
    project_row = cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not project_row:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Get Streams
    streams_rows = cursor.execute("SELECT * FROM research_streams WHERE project_id = ?", (project_id,)).fetchall()
    stream_ids = [row['id'] for row in streams_rows]
    streams_map = {row['id']: ResearchStream(id=row['id'], subject=row['subject'], focus=row['focus'],
                                             analysisType=row['analysis_type'], documents=[]) for row in streams_rows}

    # 3. Get all documents and their related data for the project in bulk to avoid N+1 queries
    docs = {}  # This will store Document objects by their ID for later enrichment
    if stream_ids:
        placeholders = ','.join('?' for _ in stream_ids)

        # Documents - fetch all documents for the project's streams
        all_project_doc_rows = cursor.execute(f"SELECT * FROM documents WHERE stream_id IN ({placeholders})",
                                              stream_ids).fetchall()
        for row in all_project_doc_rows:
            doc_obj, doc_stream_id = _map_document_row_to_document_and_stream_id(row)
            docs[row['id']] = doc_obj  # Store the document object for later enrichment
            if doc_stream_id in streams_map:
                streams_map[doc_stream_id].documents.append(doc_obj)  # Assign to stream immediately

        doc_ids = list(docs.keys())
        if doc_ids:
            placeholders = ','.join('?' for _ in doc_ids)
            # Subjects
            subject_rows = cursor.execute(
                f"SELECT ds.document_id, s.name FROM document_subjects ds JOIN subjects s ON ds.subject_id = s.id WHERE ds.document_id IN ({placeholders})",
                doc_ids).fetchall()
            for row in subject_rows:
                if row['document_id'] in docs:
                    docs[row['document_id']].subjects.append(row['name'])
            # Key Players
            player_rows = cursor.execute(
                f"SELECT dkp.document_id, kp.name FROM document_key_players dkp JOIN key_players kp ON dkp.key_player_id = kp.id WHERE dkp.document_id IN ({placeholders})",
                doc_ids).fetchall()
            for row in player_rows:
                if row['document_id'] in docs:
                    docs[row['document_id']].keyPlayers.append(row['name'])
            # Linked Docs
            link_rows = cursor.execute(
                f"SELECT source_document_id, target_document_id FROM document_links WHERE source_document_id IN ({placeholders})",
                doc_ids).fetchall()
            for row in link_rows:
                if row['source_document_id'] in docs:
                    docs[row['source_document_id']].linkedDocIds.append(row['target_document_id'])

    return Project(
        id=project_row['id'],
        name=project_row['name'],
        goal=project_row['goal'],
        description=project_row['description'],
        icon=project_row['icon'],
        createdAt=datetime.fromisoformat(project_row['created_at'].replace('Z', '+00:00')),
        researchStreams=list(streams_map.values())
    )


# --- Research Stream Endpoints (NEW) ---

@app.get("/api/projects/{project_id}/streams", response_model=List[ResearchStream])
def get_research_streams_for_project(project_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Retrieves all research streams for a given project, including their documents."""
    cursor = db.cursor()

    # 1. Get Streams
    streams_rows = cursor.execute("SELECT * FROM research_streams WHERE project_id = ?", (project_id,)).fetchall()
    if not streams_rows:
        return []  # No streams found for this project

    stream_ids = [row['id'] for row in streams_rows]
    streams_map = {row['id']: ResearchStream(id=row['id'], subject=row['subject'], focus=row['focus'],
                                             analysisType=row['analysis_type'], documents=[]) for row in streams_rows}

    # 2. Get all documents for these streams and assign them
    docs = {}  # To hold Document objects for later enrichment (subjects, key players, links)
    if stream_ids:
        placeholders = ','.join('?' for _ in stream_ids)
        all_stream_doc_rows = cursor.execute(f"SELECT * FROM documents WHERE stream_id IN ({placeholders})",
                                              stream_ids).fetchall()
        for row in all_stream_doc_rows:
            doc_obj, doc_stream_id = _map_document_row_to_document_and_stream_id(row)
            docs[row['id']] = doc_obj  # Store the document object for later enrichment
            if doc_stream_id in streams_map:
                streams_map[doc_stream_id].documents.append(doc_obj)  # Assign to stream immediately

        doc_ids = list(docs.keys())
        if doc_ids:
            placeholders = ','.join('?' for _ in doc_ids)
            # Subjects
            subject_rows = cursor.execute(
                f"SELECT ds.document_id, s.name FROM document_subjects ds JOIN subjects s ON ds.subject_id = s.id WHERE ds.document_id IN ({placeholders})",
                doc_ids).fetchall()
            for row in subject_rows:
                if row['document_id'] in docs:
                    docs[row['document_id']].subjects.append(row['name'])
            # Key Players
            player_rows = cursor.execute(
                f"SELECT dkp.document_id, kp.name FROM document_key_players dkp JOIN key_players kp ON dkp.key_player_id = kp.id WHERE dkp.document_id IN ({placeholders})",
                doc_ids).fetchall()
            for row in player_rows:
                if row['document_id'] in docs:
                    docs[row['document_id']].keyPlayers.append(row['name'])
            # Linked Docs
            link_rows = cursor.execute(
                f"SELECT source_document_id, target_document_id FROM document_links WHERE source_document_id IN ({placeholders})",
                doc_ids).fetchall()
            for row in link_rows:
                if row['source_document_id'] in docs:
                    docs[row['source_document_id']].linkedDocIds.append(row['target_document_id'])

    return list(streams_map.values())


@app.post("/api/projects/{project_id}/streams", response_model=ResearchStream, status_code=status.HTTP_201_CREATED)
def create_research_stream(project_id: str, stream_data: ResearchStreamCreate,
                           db: sqlite3.Connection = Depends(get_db)):
    """Creates a new research stream for a given project."""
    cursor = db.cursor()

    # Check if project exists
    project_row = cursor.execute("SELECT id FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not project_row:
        raise HTTPException(status_code=404, detail="Project not found")

    new_stream_id = f"rs_{uuid.uuid4().hex[:8]}"
    cursor.execute(
        "INSERT INTO research_streams (id, subject, focus, analysis_type, project_id) VALUES (?, ?, ?, ?, ?)",
        (new_stream_id, stream_data.subject, stream_data.focus, stream_data.analysisType, project_id)
    )
    db.commit()

    return ResearchStream(
        id=new_stream_id,
        subject=stream_data.subject,
        focus=stream_data.focus,
        analysisType=stream_data.analysisType,
        documents=[]  # Newly created stream has no documents yet
    )


@app.delete("/api/projects/{project_id}/streams/{stream_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_research_stream(project_id: str, stream_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Deletes a research stream from a project."""
    cursor = db.cursor()

    # Check if stream exists and belongs to the project before deleting
    result = cursor.execute("DELETE FROM research_streams WHERE id = ? AND project_id = ?", (stream_id, project_id))
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Research stream not found or does not belong to this project")

    return  # 204 No Content


# --- Static Data Endpoints ---

@app.get("/api/personas", response_model=List[Persona])
def get_all_personas(db: sqlite3.Connection = Depends(get_db)):
    """Retrieves all available personas from the database."""
    rows = db.cursor().execute("SELECT id, name, icon, prompt_start FROM personas").fetchall()
    return [Persona(id=r['id'], name=r['name'], icon=r['icon'], promptStart=r['prompt_start']) for r in rows]


@app.get("/api/tangents", response_model=List[Tangent])
def get_all_tangents(db: sqlite3.Connection = Depends(get_db)):
    """Retrieves all available tangents from the database."""
    rows = db.cursor().execute("SELECT id, name, icon, prompt_start FROM tangents").fetchall()
    return [Tangent(id=r['id'], name=r['name'], icon=r['icon'], promptStart=r['prompt_start']) for r in rows]


@app.get("/api/user-actions", response_model=List[UserAction])
def get_all_user_actions(db: sqlite3.Connection = Depends(get_db)):
    """Retrieves all available user actions from the database."""
    rows = db.cursor().execute("SELECT id, name, prompt_content FROM user_actions").fetchall()
    return [UserAction(id=r['id'], name=r['name'], promptContent=r['prompt_content']) for r in rows]


# --- Interaction Endpoints (Mocked for now, but can be expanded) ---

@app.post("/api/projects/{project_id}/actions/run", response_model=AssistantResponse)
def run_action(project_id: str, action_data: ActionInput, db: sqlite3.Connection = Depends(get_db)):
    """Simulates running a custom action within a project."""
    # In a real application, this would involve complex logic,
    # potentially using the selected_doc_ids and custom_prompt
    response_text = f"Simulating action '{action_data.action_id}' for project {project_id} on {len(action_data.selected_doc_ids)} documents."
    return AssistantResponse(response_text=response_text)


@app.post("/api/projects/{project_id}/chat", response_model=AssistantResponse)
def handle_chat_message(project_id: str, chat_data: ChatMessageInput, db: sqlite3.Connection = Depends(get_db)):
    """Simulates handling a chat message within a project."""
    # In a real application, this would involve an LLM integration,
    # using the message, selected_doc_ids, persona, tangent, etc.
    response_text = f"Simulating chat response for project {project_id}."
    return AssistantResponse(response_text=response_text)