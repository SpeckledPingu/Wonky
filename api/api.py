# api.py
import sqlite3
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field
import lancedb
from uuid import uuid4
from sentence_transformers import SentenceTransformer
from pathlib import Path
from dotenv import load_dotenv

from workflows.structured_documents.structured_talking_points_burr import structured_talking_points_build

load_dotenv('env_var')

import os
print(os.environ)

from workflows.structured_documents.structured_crs_report_analysis_burr import structured_csr_report_build
from workflows.structured_documents.structured_crs_report_analysis_burr import analysis_types as CRS_analysis_types
from workflows.structured_documents.structured_wikipedia_report_analysis_wikipedia_burr import structured_wikipedia_report_build
from workflows.structured_documents.structured_wikipedia_report_analysis_wikipedia_burr import analysis_types as WIKIPEDIA_analysis_types
from workflows.structured_documents.structured_compare_actor_positions_burr import structured_compare_actor_positions_build, actor_comparison_prompt
from workflows.structured_documents.structured_executive_summary_report_burr import structured_executive_summary_report_build, two_part_summary_prompt
from workflows.structured_documents.structured_extract_policy_recs_burr import structured_extract_policy_recommendations_report_build, policy_recommendations_prompt
from workflows.structured_documents.structured_find_funding_burr import structured_compare_actor_positions_build, funding_opportunities_prompt
from workflows.structured_documents.structured_talking_points_burr import structured_talking_points_build, talking_points_prompt
from workflows.structured_documents.structured_stakeholder_report_burr import structured_stakeholder_report_build, stakeholder_analysis_prompt

# --- Database Configuration ---
DB_FILE = 'ui/ui_data.sqlite'
_ = Path(DB_FILE)
print(_.resolve())
encoder = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', device='mps', trust_remote_code=True)

RESEARCH_FILE = '../project_research/research.sqlite'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# --- Pydantic Models (Existing and New) ---

class Project(BaseModel):
    id: str
    name: str

class StreamBase(BaseModel):
    subject: str
    focus: str

class StreamCreate(StreamBase):
    pass

class Stream(StreamBase):
    id: str
    project_id: str
    created_at: datetime

class PaperBase(BaseModel):
    title: str = Field(default="Untitled Paper")
    content: str = Field(default="# New Paper")

class PaperCreate(PaperBase):
    id: Optional[str] = None

class Paper(PaperBase):
    id: str
    project_id: str
    stream_id: str
    added_at: datetime

class ChatMessageBase(BaseModel):
    text: str
    sent_by_user: bool
    avatar: str

class ChatMessageCreate(ChatMessageBase):
    id: Optional[str] = None

class ChatMessageResponse(ChatMessageBase):
    id: str
    project_id: str
    stream_id: str
    timestamp: datetime
    timestamp_display: str
    timestamp_full: str

class DynamicAction(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    ui_group: str
    action_type: str
    output_destination: str
    prompt_template: Optional[str] = None
    is_user_defined: bool

# New Pydantic Models for Prompt Composer
class PromptComponentBase(BaseModel):
    name: str
    type: str # e.g., 'rules', 'reasoning'
    content: str

class PromptComponentCreate(PromptComponentBase):
    pass

class PromptComponent(PromptComponentBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

class PromptLibraryItemBase(BaseModel):
    name: str
    type: str # e.g., 'personas', 'actions'
    content: str

class PromptLibraryItemCreate(PromptLibraryItemBase):
    pass

class PromptLibraryItem(PromptLibraryItemBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

class ResearchStreamTopic(BaseModel):
    subject_matter: str
    focus: str


app = FastAPI()

# --- Helper Functions ---
def _dict_from_row(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    return dict(row) if row else None

def _format_chat_message_timestamps(msg_dict: Dict[str, Any]) -> Dict[str, Any]:
    if 'timestamp' in msg_dict:
        ts_value = msg_dict['timestamp']
        dt_obj = None
        if isinstance(ts_value, str):
            try:
                dt_obj = datetime.fromisoformat(ts_value.replace(' ', 'T'))
            except ValueError:
                dt_obj = datetime.now()
        elif isinstance(ts_value, datetime):
            dt_obj = ts_value
        else:
            dt_obj = datetime.now()
        msg_dict['timestamp'] = dt_obj
        msg_dict['timestamp_display'] = dt_obj.strftime('%H:%M')
        msg_dict['timestamp_full'] = dt_obj.isoformat()
    return msg_dict


def insert_new_research_paper(document_id, title, content, document_type, project_id, stream_id, cursor, conn):
    added_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
                    INSERT OR REPLACE INTO papers (id, project_id, stream_id, title, content, added_at, is_new)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    RETURNING id, project_id, title, added_at;
                    """, (document_id, project_id, stream_id, title, content, added_at, 1))
    row = cursor.fetchone()
    conn.commit()
    return row

## Alter the table to add document_type

def insert_into_research_stream(id, project_id, subject, focus, project_created_at, cursor, conn):
    row = cursor.execute("""SELECT * from research_streams
                     WHERE project_id = ? AND id = ? AND subject = ? AND focus = ?""",
                  (project_id, id, subject, focus)).fetchone()
    if len(row) == 0:
        cursor.execute("""
                      INSERT OR REPLACE INTO research_streams (id, project_id, subject, focus, created_at)
                      VALUES (?, ?, ?, ?, ?)
                      RETURNING id, project_id, subject, focus, created_at;
                      """,
                      (id, project_id, subject, focus, project_created_at)
                      )
        row = cursor.fetchone()
        conn.commit()
    return row





# --- Generation Endpoints ---
def generate_stakeholder_analysis_report(subject_matter: str, focus: str, project_id: str, stream_id: str, document_ids: list):
    run_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    run_id = str(uuid4())

    project_folder = Path('project_research')
    project_folder.mkdir(parents=True, exist_ok=True)
    research_json_folder = project_folder.joinpath('json_data')
    research_json_folder.mkdir(parents=True, exist_ok=True)
    database_location = project_folder.joinpath('research.sqlite')

    conn = sqlite3.connect(database_location)
    cursor = conn.cursor()
    temperature = 0.2
    fields = ['overview', 'run_id', 'run_timestamp', 'project_id', 'subject_matter', 'focus', 'source_document']

    summary_app = structured_stakeholder_report_build()
    summary_action, summary_result, summary_state = summary_app.run(
        halt_after=["generate_stakeholder_summary"],
        inputs={
            "subject_matter": subject_matter,
            "focus": focus,
            "fields": fields,
            "document_ids": document_ids,
            "summary_prompt_template": stakeholder_analysis_prompt,
            "temperature": 0.2,
            "conn": conn,
            "cursor": cursor,
        }
    )

    ui_conn = sqlite3.connect(DB_FILE)
    ui_cursor = ui_conn.cursor()
    extraction_data = summary_state.get_all()
    for _document_id, _extractions in extraction_data['extractions'].items():
        title = 'Stake_' + _extractions['title']
        content = _extractions['overview']
        added_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_new_research_paper(_document_id, title, content, 'stakeholder_report', project_id, stream_id, ui_cursor, ui_conn)
    ui_conn.close()


def generate_talking_points_report(subject_matter: str, focus: str, project_id: str, stream_id: str, document_ids: list,
                                   audience: str, viewpoint: str):
    run_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    run_id = str(uuid4())

    project_folder = Path('project_research')
    project_folder.mkdir(parents=True, exist_ok=True)
    research_json_folder = project_folder.joinpath('json_data')
    research_json_folder.mkdir(parents=True, exist_ok=True)
    database_location = project_folder.joinpath('research.sqlite')

    conn = sqlite3.connect(database_location)
    cursor = conn.cursor()
    temperature = 0.2
    fields = ['overview', 'run_id', 'run_timestamp', 'project_id', 'subject_matter', 'focus', 'source_document']

    summary_app = structured_talking_points_build()
    summary_action, summary_result, summary_state = summary_app.run(
        halt_after=["generate_talking_points_summary"],
        inputs={
            "subject_matter": subject_matter,
            "focus": focus,
            "fields":fields,
            "audience": audience,
            "viewpoint": viewpoint,
            "document_ids": document_ids,
            "talkingpoints_prompt":talking_points_prompt,
            "temperature":temperature,
            "conn": conn,
            "cursor": cursor,
        }
    )

    ui_conn = sqlite3.connect(DB_FILE)
    ui_cursor = ui_conn.cursor()
    extraction_data = summary_state.get_all()
    for _document_id, _extractions in extraction_data['extractions'].items():
        title = 'TPoints_' + _extractions['title']
        content = _extractions['overview']
        added_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_new_research_paper(_document_id, title, content, 'talking_points', project_id, stream_id, ui_cursor, ui_conn)
    ui_conn.close()


def generate_find_funding_report(subject_matter: str, focus: str, project_id: str, stream_id: str, document_ids: list):
    run_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    run_id = str(uuid4())

    project_folder = Path('project_research')
    project_folder.mkdir(parents=True, exist_ok=True)
    research_json_folder = project_folder.joinpath('json_data')
    research_json_folder.mkdir(parents=True, exist_ok=True)
    database_location = project_folder.joinpath('research.sqlite')

    conn = sqlite3.connect(database_location)
    cursor = conn.cursor()
    temperature = 0.2
    fields = ['overview', 'run_id', 'run_timestamp', 'project_id', 'subject_matter', 'focus', 'source_document']

    summary_app = structured_compare_actor_positions_build()
    summary_action, summary_result, summary_state = summary_app.run(
        halt_after=["generate_funding_opportunities_summary"],
        inputs={
            "subject_matter": subject_matter,
            "focus": focus,
            "fields": fields,
            "document_ids": document_ids,
            "funding_opportunities_prompt": funding_opportunities_prompt,
            "temperature": temperature,
            "conn": conn,
            "cursor": cursor,
        }
    )

    ui_conn = sqlite3.connect(DB_FILE)
    ui_cursor = ui_conn.cursor()
    extraction_data = summary_state.get_all()
    for _document_id, _extractions in extraction_data['extractions'].items():
        title = 'Funding_' + _extractions['title']
        content = _extractions['overview']
        added_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_new_research_paper(_document_id, title, content, 'funding_opportunities', project_id, stream_id, ui_cursor, ui_conn)
    ui_conn.close()


def generate_policy_recommendation_report(subject_matter: str, focus: str, project_id: str, stream_id: str, document_ids: list):
    run_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    run_id = str(uuid4())

    project_folder = Path('project_research')
    project_folder.mkdir(parents=True, exist_ok=True)
    research_json_folder = project_folder.joinpath('json_data')
    research_json_folder.mkdir(parents=True, exist_ok=True)
    database_location = project_folder.joinpath('research.sqlite')

    conn = sqlite3.connect(database_location)
    cursor = conn.cursor()
    temperature = 0.2
    fields = ['overview', 'run_id', 'run_timestamp', 'project_id', 'subject_matter', 'focus', 'source_document']

    summary_app = structured_compare_actor_positions_build()
    summary_action, summary_result, summary_state = summary_app.run(
        halt_after=["generate_policy_recommendations_summary"],
        inputs={
            "subject_matter": subject_matter,
            "focus": focus,
            "fields": fields,
            "document_ids": document_ids,
            "policy_recommendations_prompt": policy_recommendations_prompt,
            "temperature": temperature,
            "conn": conn,
            "cursor": cursor,
        }
    )
    ui_conn = sqlite3.connect(DB_FILE)
    ui_cursor = ui_conn.cursor()
    extraction_data = summary_state.get_all()
    for _document_id, _extractions in extraction_data['extractions'].items():
        title = 'PolicyR_' + _extractions['title']
        content = _extractions['overview']
        added_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_new_research_paper(_document_id, title, content, 'policy_recommendations', project_id, stream_id, ui_cursor, ui_conn)
    ui_conn.close()


def generate_executive_summary_report(subject_matter: str, focus: str, project_id: str, stream_id: str, document_ids: list):
    run_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    run_id = str(uuid4())

    project_folder = Path('project_research')
    project_folder.mkdir(parents=True, exist_ok=True)
    research_json_folder = project_folder.joinpath('json_data')
    research_json_folder.mkdir(parents=True, exist_ok=True)
    database_location = project_folder.joinpath('research.sqlite')

    conn = sqlite3.connect(database_location)
    cursor = conn.cursor()
    temperature = 0.2
    fields = ['overview', 'run_id', 'run_timestamp', 'project_id', 'subject_matter', 'focus', 'source_document']

    summary_app = structured_executive_summary_report_build()
    summary_action, summary_result, summary_state = summary_app.run(
    halt_after=["generate_executive_summary"],
    inputs={
        "subject_matter": subject_matter,
        "focus": focus,
        "fields":fields,
        "document_ids": document_ids,
        "summary_prompt_template":two_part_summary_prompt,
        "temperature":temperature,
        "conn": conn,
        "cursor": cursor,
    }
)

    ui_conn = sqlite3.connect(DB_FILE)
    ui_cursor = ui_conn.cursor()
    extraction_data = summary_state.get_all()
    print(extraction_data['summary'])
    # for _document_id, _extractions in extraction_data['summary'].items():
    title = 'Exec_' + ' '.join(document_ids) #_extractions['title']
    content = extraction_data['summary']
    added_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    insert_new_research_paper(title, title, content, 'executive_summary', project_id, stream_id, ui_cursor, ui_conn)
    ui_conn.close()


def generate_compare_actor_positions_report(subject_matter: str, focus: str, project_id: str, stream_id: str, document_ids: list,
                                            actors_to_compare: list):
    run_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    run_id = str(uuid4())

    project_folder = Path('project_research')
    project_folder.mkdir(parents=True, exist_ok=True)
    research_json_folder = project_folder.joinpath('json_data')
    research_json_folder.mkdir(parents=True, exist_ok=True)
    database_location = project_folder.joinpath('research.sqlite')

    conn = sqlite3.connect(database_location)
    cursor = conn.cursor()
    temperature = 0.2
    fields = ['overview', 'run_id', 'run_timestamp', 'project_id', 'subject_matter', 'focus', 'source_document']
    actors_to_compare = ', '.join(actors_to_compare)

    summary_app = structured_compare_actor_positions_build()
    summary_action, summary_result, summary_state = summary_app.run(
        halt_after=["generate_actor_comparison_summary"],
        inputs={
            "subject_matter": subject_matter,
            "focus": focus,
            "fields":fields,
            "document_ids": document_ids,
            "actor_comparison_prompt":actor_comparison_prompt,
            "actors_to_compare": actors_to_compare,
            "temperature":temperature,
            "conn": conn,
            "cursor": cursor,
        }
    )

    ui_conn = sqlite3.connect(DB_FILE)
    ui_cursor = ui_conn.cursor()
    extraction_data = summary_state.get_all()
    for _document_id, _extractions in extraction_data['extractions'].items():
        title = 'Compare_' + _extractions['title']
        content = _extractions['overview']
        added_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_new_research_paper(_document_id, title, content, 'compare_actors', project_id, stream_id, ui_cursor, ui_conn)
    ui_conn.close()


def generate_crs_report(subject_matter: str, focus: str, project_id: str, stream_id: str):
    run_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    run_id = str(uuid4())
    # project_id = str(uuid4())
    # project_id = 'proj_alpha_01'
    # stream_id = 'general'
    crs_source_dataset = 'CRSReports'
    wikipedia_source_dataset = 'Wikipedia'
    # subject_matter = "Rural Broadband in America."
    # focus = "Historical, current, and future challenges for rural broadband and connectivity in America."

    analysis_type = 'domestic_policy'
    analysis_prompts = CRS_analysis_types[analysis_type]

    project_folder = Path('project_research')
    project_folder.mkdir(parents=True, exist_ok=True)
    research_json_folder = project_folder.joinpath('json_data')
    research_json_folder.mkdir(parents=True, exist_ok=True)
    database_location = project_folder.joinpath('research.sqlite')

    conn = sqlite3.connect(database_location)
    cursor = conn.cursor()
    index = lancedb.connect('../../wonky_data/indexes/')
    table = index.open_table('sections_hybrid')
    # encoder = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', device='mps', trust_remote_code=True)

    temperature = 0.2
    crs_num_results = 3
    wikipedia_num_results = 2

    extraction_app = structured_csr_report_build()
    extraction_action, extraction_result, extraction_state = extraction_app.run(
        halt_after=["save_research_to_json"],
        inputs={
            "subject_matter": subject_matter,
            "focus": focus,
            "analysis_type": analysis_type,
            "analysis_prompts": analysis_prompts,
            "table": table,
            "temperature": temperature,
            "run_id": run_id,
            "project_id": project_id,
            "run_timestamp": run_timestamp,
            "conn": conn,
            "cursor": cursor,
            "research_json_folder": research_json_folder,
            "num_results": crs_num_results,
            "source_dataset": crs_source_dataset,
            "encoder":encoder
        }
    )

    ui_conn = sqlite3.connect(DB_FILE)
    ui_cursor = ui_conn.cursor()
    extraction_data = extraction_state.get_all()
    for _document_id, _extractions in extraction_data['extractions'].items():
        title = 'EXT_' + _extractions['title']
        content = _extractions['overview']
        added_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_new_research_paper(_document_id, title, content, 'extraction', project_id, stream_id, ui_cursor, ui_conn)
    ui_conn.close()


def generate_wikipedia_report(subject_matter: str, focus: str, project_id: str, stream_id: str):
    run_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    run_id = str(uuid4())
    # project_id = str(uuid4())
    # project_id = 'proj_alpha_01'
    # stream_id = 'general'
    crs_source_dataset = 'CRSReports'
    wikipedia_source_dataset = 'Wikipedia'
    # subject_matter = "Rural Broadband in America."
    # focus = "Historical, current, and future challenges for rural broadband and connectivity in America."

    analysis_type = 'domestic_policy'
    analysis_prompts = WIKIPEDIA_analysis_types[analysis_type]

    project_folder = Path('project_research')
    project_folder.mkdir(parents=True, exist_ok=True)
    research_json_folder = project_folder.joinpath('json_data')
    research_json_folder.mkdir(parents=True, exist_ok=True)
    database_location = project_folder.joinpath('research.sqlite')

    conn = sqlite3.connect(database_location)
    cursor = conn.cursor()
    index = lancedb.connect('../../wonky_data/indexes/')
    table = index.open_table('sections_hybrid')
    # encoder = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', device='mps', trust_remote_code=True)

    temperature = 0.2
    crs_num_results = 3
    wikipedia_num_results = 2

    extraction_app = structured_wikipedia_report_build()
    extraction_action, extraction_result, extraction_state = extraction_app.run(
        halt_after=["save_research_to_json"],
        inputs={
            "subject_matter": subject_matter,
            "focus": focus,
            "analysis_type": analysis_type,
            "analysis_prompts": analysis_prompts,
            "table": table,
            "temperature": temperature,
            "run_id": run_id,
            "project_id": project_id,
            "run_timestamp": run_timestamp,
            "conn": conn,
            "cursor": cursor,
            "research_json_folder": research_json_folder,
            "num_results": wikipedia_num_results,
            "source_dataset": wikipedia_source_dataset,
        }
    )

    ui_conn = sqlite3.connect(DB_FILE)
    ui_cursor = ui_conn.cursor()
    extraction_data = extraction_state.get_all()
    for _document_id, _extractions in extraction_data['extractions'].items():
        title = 'EXT_' + _extractions['title']
        content = _extractions['overview']
        added_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_new_research_paper(_document_id, title, content, 'extraction', project_id, stream_id, ui_cursor, ui_conn)
    ui_conn.close()

class SelectedDocumentsAction(BaseModel):
    subject_matter: str
    focus: str
    project_id: str
    stream_id: str
    selected_documents: List[str]


# api.py

# ... (existing imports like FastAPI, HTTPException, Depends, BackgroundTasks, BaseModel, Field, List, Optional, etc.)
# ... (ensure your generation functions like generate_executive_summary_report, etc., are imported or defined)

# --- Pydantic Model for the new endpoint's payload ---
class ExecuteActionPayload(BaseModel):
    project_id: str
    stream_id: str
    selected_documents: List[str] = Field(default_factory=list)
    action_id: str

    # Optional fields based on what 'required_inputs' might define for various actions
    # These should correspond to the 'name' attributes in your required_inputs JSON
    subject_matter: Optional[str] = None
    focus: Optional[str] = None
    max_length: Optional[int] = None # Example, if used by a workflow
    audience: Optional[str] = None   # For actions like 'generate_talking_points'
    viewpoint: Optional[str] = None  # For actions like 'generate_talking_points'
    actors_to_compare: Optional[List[str]] = None # For 'compare_actor_positions'
    # Add any other dynamic input fields that your actions might require


# --- Mapping Action IDs to Backend Functions ---
# Keys: 'id' from the dynamic_actions table
# Values: The corresponding Python function in api.py that runs the Burr workflow
ACTION_TO_FUNCTION_MAP = {
    # Example mapping - replace with your actual action IDs and functions
    "generate_custom_summary": generate_executive_summary_report,
    # Add mappings for other actions defined in your dynamic_actions table, e.g.:
    # "generate_policy_recs_v1": generate_policy_recommendation_report,
    # "find_funding_v1": generate_find_funding_report,
    # "generate_talking_points_v1": generate_talking_points_report,
    # "analyze_stakeholders_v1": generate_stakeholder_analysis_report,
    # "compare_actors_v1": generate_compare_actor_positions_report,
}

# --- New API Endpoint ---

@app.post("/actions/execute_dynamic_action", status_code=202) # 202 Accepted for background tasks
async def execute_dynamic_action_endpoint(
    payload: ExecuteActionPayload,
    background_tasks: BackgroundTasks,
    conn: sqlite3.Connection = Depends(get_db_connection) # To fetch action details if needed
):
    """
    Generic endpoint to execute a dynamic action based on its ID and provided inputs.
    """
    action_function = ACTION_TO_FUNCTION_MAP.get(payload.action_id)

    if not action_function:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Action ID '{payload.action_id}' is not mapped to a backend function. Please check ACTION_TO_FUNCTION_MAP."
        )

    # Fetch action details from DB to get the prompt_template if needed by the workflow
    # This assumes your Burr workflow functions are designed to accept a custom prompt.
    cursor = conn.cursor()
    cursor.execute("SELECT prompt_template FROM dynamic_actions WHERE id = ?", (payload.action_id,))
    action_db_row = cursor.fetchone()
    conn.close()

    if not action_db_row:
        # This should ideally not happen if the frontend got the action_id from the same DB
        raise HTTPException(status_code=404, detail=f"Configuration for action ID '{payload.action_id}' not found in database.")

    db_prompt_template = _dict_from_row(action_db_row).get("prompt_template")

    # Prepare arguments for the target action_function
    common_args = {
        "project_id": payload.project_id,
        "stream_id": payload.stream_id,
        "document_ids": payload.selected_documents,
    }

    # Add action-specific arguments from the payload
    # This section needs to align with the signatures of your mapped functions
    specific_args = {}
    if payload.subject_matter is not None:
        specific_args["subject_matter"] = payload.subject_matter
    if payload.focus is not None:
        specific_args["focus"] = payload.focus

    # For functions requiring more specific inputs like audience, viewpoint, actors_to_compare
    if action_function == generate_talking_points_report:
        if payload.audience is None or payload.viewpoint is None:
            raise HTTPException(status_code=400, detail="Audience and viewpoint are required for generating talking points.")
        specific_args["audience"] = payload.audience
        specific_args["viewpoint"] = payload.viewpoint
    elif action_function == generate_compare_actor_positions_report:
        if payload.actors_to_compare is None:
            raise HTTPException(status_code=400, detail="Actors to compare are required for this action.")
        specific_args["actors_to_compare"] = payload.actors_to_compare
    # Add other elif blocks for functions with unique required dynamic inputs

    # IMPORTANT: Adapt your generation functions (e.g., generate_executive_summary_report)
    # to accept a parameter for the prompt template (e.g., `prompt_override: Optional[str] = None`)
    # and use it in the Burr app's inputs if provided.
    # Example modification in generate_executive_summary_report:
    #   def generate_executive_summary_report(..., prompt_override: Optional[str] = None):
    #       ...
    #       current_prompt = prompt_override if prompt_override else two_part_summary_prompt # (default prompt)
    #       burr_inputs = {..., "summary_prompt_template": current_prompt, ...}
    #       summary_app.run(..., inputs=burr_inputs)
    #
    # If your generation functions are adapted, you can pass the db_prompt_template:
    if db_prompt_template:
        # The key here ('prompt_override', 'custom_prompt', etc.) must match
        # the parameter name in your adapted generation functions.
        specific_args["prompt_override"] = db_prompt_template # Example key

    final_args = {**common_args, **specific_args}

    # Validate that all required args for the specific function are present
    # (Python will raise TypeError if arguments are missing when calling the function)
    # You can add more specific checks here based on function signatures if desired.

    background_tasks.add_task(action_function, **final_args)

    return {
        "message": f"Action '{payload.action_id}' (mapped to: {action_function.__name__}) initiated successfully.",
        "details": f"Processing with arguments: { {k:v for k,v in final_args.items() if k not in ['document_ids']} } and {len(final_args.get('document_ids',[]))} documents."
    }

# Make sure this new endpoint is below your app = FastAPI() line and
# other necessary imports and definitions.


@app.post("/generation/executive_summary", response_model=None, status_code=200)
async def generate_executive_summary_report_endpoint(selected_documents: SelectedDocumentsAction, background_tasks: BackgroundTasks):
    print('project id')
    print(selected_documents.project_id)
    print(selected_documents.stream_id)
    print(selected_documents)
    background_tasks.add_task(generate_executive_summary_report,
                              subject_matter=selected_documents.subject_matter,
                              focus=selected_documents.focus,
                              project_id=selected_documents.project_id,
                              stream_id=selected_documents.stream_id,
                              document_ids=selected_documents.selected_documents)

@app.post("/generation/crs_report", response_model=None, status_code=200)
async def generate_crs_report_extraction(subject_matter: str, focus: str, project_id: str, stream_id: str, background_tasks: BackgroundTasks):
    print('project id')
    print(project_id)
    print(stream_id)
    background_tasks.add_task(generate_crs_report, subject_matter=subject_matter, focus=focus,
                              project_id=project_id, stream_id=stream_id)

@app.post("/generation/wikipedia_report", response_model=None, status_code=200)
async def generate_wikipedia_report_extraction(subject_matter: str, focus: str, project_id: str, stream_id:str, background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_wikipedia_report, subject_matter=subject_matter, focus=focus,
                              project_id=project_id, stream_id=stream_id)

@app.post("/generation/crs_wiki_reports", response_model=None, status_code=200)
async def generate_crs_wikipedia_report_extraction(subject_matter: str, focus: str, project_id: str, stream_id:str, background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_crs_report, subject_matter=subject_matter, focus=focus,
                              project_id=project_id, stream_id=stream_id)
    background_tasks.add_task(generate_wikipedia_report, subject_matter=subject_matter, focus=focus,
                              project_id=project_id, stream_id=stream_id)


# --- API Endpoints (Existing and New) ---

@app.get("/projects/{project_id}", response_model=Optional[Project])
async def get_project_details(project_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM projects WHERE id = ?", (project_id,))
        project = cursor.fetchone()
        return _dict_from_row(project)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if conn:
            conn.close()

# --- New Endpoints for Research Streams ---

@app.get("/projects/{project_id}/streams", response_model=List[Stream])
async def get_streams_for_project(project_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, project_id, subject, focus, created_at
            FROM research_streams
            WHERE project_id = ?
            ORDER BY subject;
        """, (project_id,))
        rows = cursor.fetchall()
        print(rows)
        return [_dict_from_row(row) for row in rows]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error loading streams: {e}")
    finally:
        if conn:
            conn.close()

@app.post("/projects/{project_id}/streams", response_model=Stream, status_code=201)
async def create_stream_for_project(project_id: str, stream_data: StreamCreate, conn: sqlite3.Connection = Depends(get_db_connection)):
    stream_id = f"rs_{uuid.uuid4().hex[:10]}"
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO research_streams (id, project_id, subject, focus)
            VALUES (?, ?, ?, ?)
            RETURNING id, project_id, subject, focus, created_at;
        """, (stream_id, project_id, stream_data.subject, stream_data.focus))
        row = cursor.fetchone()
        conn.commit()
        if row:
            return _dict_from_row(row)
        raise HTTPException(status_code=500, detail="Failed to retrieve stream after creation.")
    except sqlite3.Error as e:
        conn.rollback() # Rollback on error
        raise HTTPException(status_code=500, detail=f"Database error creating stream: {e}")
    finally:
        if conn:
            conn.close()

@app.delete("/projects/{project_id}/streams/{stream_id}", status_code=200) # Changed to 200 for response body
async def delete_stream_from_project(project_id: str, stream_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM research_streams
            WHERE id = ? AND project_id = ?;
        """, (stream_id, project_id))
        conn.commit()
        if cursor.rowcount > 0:
            return {"message": f"Stream '{stream_id}' deleted successfully."}
        else:
            raise HTTPException(status_code=404, detail=f"Stream '{stream_id}' not found for project '{project_id}'.")
    except sqlite3.Error as e:
        conn.rollback() # Rollback on error
        raise HTTPException(status_code=500, detail=f"Database error deleting stream: {e}")
    finally:
        if conn:
            conn.close()

# --- End of New Stream Endpoints ---


@app.get("/streams/{stream_id}", response_model=Optional[Stream])
async def get_stream_details(stream_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    # This endpoint is used by project_workspace_page.py
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, project_id, subject, focus, created_at FROM research_streams WHERE id = ?", (stream_id,))
        stream = cursor.fetchone()
        return _dict_from_row(stream)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if conn:
            conn.close()


@app.get("/projects/{project_id}/streams/{stream_id}/papers", response_model=List[Paper])
async def load_papers_for_stream(project_id: str, stream_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    print('getting papers!')
    try:
        print(project_id)
        print(stream_id)
        cursor = conn.cursor()
        if stream_id == 'general':
            print('general stream')
            cursor.execute("""
                           SELECT id, project_id, stream_id, title, content, added_at
                           FROM papers
                           WHERE project_id = ?
                           ORDER BY added_at DESC;
                               """, (project_id, ))
        else:
            print('specific stream')
            cursor.execute("""
                           SELECT id, project_id, stream_id, title, content, added_at
                           FROM papers
                           WHERE project_id = ?
                             AND stream_id = ?
                           ORDER BY added_at DESC;
                           """, (project_id, stream_id))

        rows = cursor.fetchall()
        return [_dict_from_row(row) for row in rows]
    except sqlite3.Error as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if conn:
            conn.close()

@app.post("/projects/{project_id}/streams/{stream_id}/papers", response_model=Paper, status_code=201)
async def add_paper_to_stream(project_id: str, stream_id: str, paper_data: PaperCreate, conn: sqlite3.Connection = Depends(get_db_connection)):
    paper_id = paper_data.id if paper_data.id else f"paper_{uuid.uuid4().hex[:10]}"
    try:
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO papers (id, project_id, stream_id, title, content)
                       VALUES (?, ?, ?, ?, ?)
                       RETURNING id, project_id, stream_id, title, content, added_at;
                       """, (paper_id, project_id, stream_id, paper_data.title, paper_data.content))
        row = cursor.fetchone()
        conn.commit()
        if row:
            return _dict_from_row(row)
        raise HTTPException(status_code=500, detail="Failed to retrieve paper after adding.")
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error adding paper: {e}")
    finally:
        if conn:
            conn.close()

@app.get("/projects/{project_id}/streams/{stream_id}/papers/check_new_papers", response_model=List[Paper])
async def load_new_papers_for_stream(project_id: str, stream_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = conn.cursor()
        if stream_id == 'general':
            print('general')
            cursor.execute("""
                           SELECT id, project_id, stream_id, title, content, added_at, is_new
                           FROM papers
                           WHERE project_id = ?
                             AND is_new = 1
                           ORDER BY added_at DESC;
                           """, (project_id, ))
        else:
            print(stream_id)
            cursor.execute("""
                           SELECT id, project_id, stream_id, title, content, added_at, is_new
                           FROM papers
                           WHERE project_id = ? AND stream_id = ? AND is_new = 1
                           ORDER BY added_at DESC;
                           """, (project_id, stream_id)) # Corrected to filter by stream_id as well
        rows = cursor.fetchall()
        print(len([_dict_from_row(row) for row in rows]))
        return [_dict_from_row(row) for row in rows]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if conn:
            conn.close()

@app.post("/projects/{project_id}/streams/{stream_id}/papers/clear_new_papers", response_model=List[Paper])
async def clear_new_papers_for_stream(project_id: str, stream_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = conn.cursor()
        print(project_id, stream_id)
        print()
        cursor.execute("""
                       UPDATE papers
                       SET is_new = 0
                       WHERE project_id = ? AND stream_id = ?;
                       """, (project_id, stream_id)) # Corrected to filter by stream_id as well
        rows = cursor.fetchall()
        conn.commit()
        print('rows updated:')
        print(len([_dict_from_row(row) for row in rows]))
        return [_dict_from_row(row) for row in rows]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if conn:
            conn.close()

@app.delete("/projects/{project_id}/streams/{stream_id}/papers/{paper_id}", status_code=200)
async def delete_paper_from_stream(project_id: str, stream_id: str, paper_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = conn.cursor()
        cursor.execute("""
                       DELETE FROM papers
                       WHERE id = ? AND project_id = ? AND stream_id = ?;
                       """, (paper_id, project_id, stream_id)) # Added stream_id for consistency
        conn.commit()
        if cursor.rowcount > 0:
            return {"message": f"Paper '{paper_id}' deleted successfully."}
        else:
            raise HTTPException(status_code=404, detail=f"Paper '{paper_id}' not found for project '{project_id}' and stream '{stream_id}'.")
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error deleting paper: {e}")
    finally:
        if conn:
            conn.close()

@app.get("/projects/{project_id}/streams/{stream_id}/chat/messages", response_model=List[ChatMessageResponse])
async def load_chat_messages(project_id: str, stream_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    messages = []
    try:
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT id, project_id, stream_id, text, sent_by_user, avatar, timestamp
                       FROM chat_messages
                       WHERE project_id = ? AND stream_id = ?
                       ORDER BY timestamp ASC;
                       """, (project_id, stream_id))
        rows = cursor.fetchall()
        for row_data in rows:
            msg_dict = _dict_from_row(row_data)
            if msg_dict:
                messages.append(_format_chat_message_timestamps(msg_dict))

        if not messages:
            initial_ai_message_data = ChatMessageCreate(
                id=f'chat_init_{uuid.uuid4().hex[:6]}',
                text='Hello! How can I help you with your research today?',
                sent_by_user=False,
                avatar='https://robohash.org/ai.png?size=40x40',
            )
            try:
                init_cursor = conn.cursor()
                init_cursor.execute("""
                               INSERT INTO chat_messages (id, project_id, stream_id, text, sent_by_user, avatar)
                               VALUES (?, ?, ?, ?, ?, ?)
                               RETURNING id, project_id, stream_id, text, sent_by_user, avatar, timestamp;
                               """, (initial_ai_message_data.id, project_id, stream_id,
                                     initial_ai_message_data.text, initial_ai_message_data.sent_by_user,
                                     initial_ai_message_data.avatar))
                saved_initial_msg_row = init_cursor.fetchone()
                conn.commit()
                if saved_initial_msg_row:
                    msg_dict = _dict_from_row(saved_initial_msg_row)
                    if msg_dict:
                        messages.append(_format_chat_message_timestamps(msg_dict))
            except sqlite3.Error as e_init:
                conn.rollback()
                print(f"Database error saving initial chat message: {e_init}")

        return messages
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error loading chat messages: {e}")
    finally:
        if conn:
            conn.close()

@app.post("/projects/{project_id}/streams/{stream_id}/chat/messages", response_model=ChatMessageResponse, status_code=201)
async def save_chat_message(
    project_id: str,
    stream_id: str,
    message_data: ChatMessageCreate,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    message_id = message_data.id if message_data.id else f"msg_{uuid.uuid4().hex[:10]}"
    try:
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO chat_messages (id, project_id, stream_id, text, sent_by_user, avatar)
                       VALUES (?, ?, ?, ?, ?, ?)
                       RETURNING id, project_id, stream_id, text, sent_by_user, avatar, timestamp;
                       """, (message_id, project_id, stream_id, message_data.text,
                             message_data.sent_by_user, message_data.avatar))
        row = cursor.fetchone()
        conn.commit()
        if row:
            msg_dict = _dict_from_row(row)
            if msg_dict:
                return _format_chat_message_timestamps(msg_dict)
        raise HTTPException(status_code=500, detail="Failed to retrieve message after saving.")
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error saving message: {e}")
    finally:
        if conn:
            conn.close()

@app.delete("/projects/{project_id}/streams/{stream_id}/chat/messages", status_code=200)
async def clear_chat_messages(project_id: str, stream_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_messages WHERE project_id = ? AND stream_id = ?;", (project_id, stream_id))
        conn.commit()
        return {"message": "Chat messages cleared.", "rows_affected": cursor.rowcount}
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error clearing chat: {e}")
    finally:
        if conn:
            conn.close()

@app.get("/dynamic-actions", response_model=List[DynamicAction])
async def get_dynamic_actions_by_group(ui_group: str = Query(...), conn: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, description, ui_group, action_type, output_destination, prompt_template, is_user_defined
            FROM dynamic_actions
            WHERE ui_group = ?
            ORDER BY name ASC;
        """, (ui_group,))
        rows = cursor.fetchall()

        return [_dict_from_row(row) for row in rows]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if conn:
            conn.close()

@app.get("/dynamic-actions/{action_id}", response_model=Optional[DynamicAction])
async def get_dynamic_action_by_id(action_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, description, ui_group, action_type, output_destination, prompt_template, is_user_defined
            FROM dynamic_actions
            WHERE id = ?;
        """, (action_id,))
        row = cursor.fetchone()
        print(_dict_from_row(row))
        return _dict_from_row(row)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if conn:
            conn.close()

# Prompt Components
@app.get("/users/{user_id}/prompt-components", response_model=List[PromptComponent])
async def get_prompt_components_for_user(user_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, name, type, content, created_at, updated_at FROM prompt_components WHERE user_id = ? ORDER BY name", (user_id,))
        rows = cursor.fetchall()
        return [_dict_from_row(row) for row in rows]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error loading prompt components: {e}")
    finally:
        if conn: conn.close()

@app.post("/users/{user_id}/prompt-components", response_model=PromptComponent, status_code=201)
async def create_prompt_component_for_user(user_id: str, component_data: PromptComponentCreate, conn: sqlite3.Connection = Depends(get_db_connection)):
    component_id = f"comp_{uuid.uuid4().hex[:10]}"
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO prompt_components (id, user_id, name, type, content)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id, user_id, name, type, content, created_at, updated_at;
        """, (component_id, user_id, component_data.name, component_data.type, component_data.content))
        row = cursor.fetchone()
        conn.commit()
        if row:
            return _dict_from_row(row)
        raise HTTPException(status_code=500, detail="Failed to retrieve component after creation.")
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error creating prompt component: {e}")
    finally:
        if conn: conn.close()

@app.delete("/users/{user_id}/prompt-components/{component_id}", status_code=200)
async def delete_prompt_component_for_user(user_id: str, component_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM prompt_components WHERE id = ? AND user_id = ?", (component_id, user_id))
        conn.commit()
        if cursor.rowcount > 0:
            return {"message": f"Prompt component '{component_id}' deleted successfully."}
        raise HTTPException(status_code=404, detail=f"Prompt component '{component_id}' not found for user '{user_id}'.")
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error deleting prompt component: {e}")
    finally:
        if conn: conn.close()

# Prompt Library Items
@app.get("/users/{user_id}/prompt-library", response_model=List[PromptLibraryItem])
async def get_prompt_library_items_for_user(user_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, name, type, content, created_at, updated_at FROM prompt_library WHERE user_id = ? ORDER BY name", (user_id,))
        rows = cursor.fetchall()
        return [_dict_from_row(row) for row in rows]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error loading prompt library items: {e}")
    finally:
        if conn: conn.close()

@app.post("/users/{user_id}/prompt-library", response_model=PromptLibraryItem, status_code=201)
async def create_prompt_library_item_for_user(user_id: str, item_data: PromptLibraryItemCreate, conn: sqlite3.Connection = Depends(get_db_connection)):
    item_id = f"lib_{uuid.uuid4().hex[:10]}"
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO prompt_library (id, user_id, name, type, content)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id, user_id, name, type, content, created_at, updated_at;
        """, (item_id, user_id, item_data.name, item_data.type, item_data.content))
        row = cursor.fetchone()
        conn.commit()
        if row:
            return _dict_from_row(row)
        raise HTTPException(status_code=500, detail="Failed to retrieve library item after creation.")
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error creating prompt library item: {e}")
    finally:
        if conn: conn.close()

@app.delete("/users/{user_id}/prompt-library/{item_id}", status_code=200)
async def delete_prompt_library_item_for_user(user_id: str, item_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM prompt_library WHERE id = ? AND user_id = ?", (item_id, user_id))
        conn.commit()
        if cursor.rowcount > 0:
            return {"message": f"Prompt library item '{item_id}' deleted successfully."}
        raise HTTPException(status_code=404, detail=f"Prompt library item '{item_id}' not found for user '{user_id}'.")
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error deleting prompt library item: {e}")
    finally:
        if conn: conn.close()

# --- (Keep other existing endpoints) ---
# Example:
@app.get("/projects/{project_id}", response_model=Optional[Project])
async def get_project_details(project_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM projects WHERE id = ?", (project_id,))
        project = cursor.fetchone()
        return _dict_from_row(project)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if conn: conn.close()


# To run this FastAPI app (save as api.py):
# uvicorn api:app --reload