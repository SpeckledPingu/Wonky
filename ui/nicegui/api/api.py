# api.py
import sqlite3
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field

# --- Database Configuration ---
DB_FILE = '../ui_data.sqlite'

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