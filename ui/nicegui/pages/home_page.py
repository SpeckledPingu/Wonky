# pages/home_page.py

from nicegui import ui, app  # Added app import
import uuid # For generating unique IDs if needed for new projects
import sqlite3
# --- Placeholder for Backend Functions (Illustrative) ---
# In a real application, these would interact with your SQL database.
#
# def db_load_projects():
#     # SQL_HOOK: Example: SELECT id, name FROM projects ORDER BY name;
#     print(f"SQL_HOOK: (Placeholder) Loading all projects from database")
#     # This would be replaced by an actual database call.
#     # For now, let's simulate if app.storage.user has 'db_projects' or return empty
#     # This is just to make it runnable without a live DB for this example.
#     # In a real scenario, you'd directly query the DB.
#     if 'db_projects' in app.storage.user:
#         return app.storage.user['db_projects']
#     return [] # Return list of project dicts, e.g., [{"id": "proj_1", "name": "Project Alpha"}, ...]
#
# def db_create_project(project_name: str):
#     # SQL_HOOK: Example: INSERT INTO projects (id, name) VALUES (?, ?) RETURNING id, name;
#     # The 'id' could be generated here or by the database.
#     project_id = project_name.lower().replace(" ", "_") + f"_{str(uuid.uuid4())[:4]}" # Simple unique ID
#     print(f"SQL_HOOK: (Placeholder) Creating project '{project_name}' with id '{project_id}' in database")
#     # Simulate DB interaction and return the created project object
#     new_project = {"id": project_id, "name": project_name}
#
#     # Simulate saving to a 'db_projects' list in app.storage for this example
#     # In a real app, this function would directly interact with the SQL DB.
#     current_db_projects = app.storage.user.get('db_projects', [])
#     current_db_projects.append(new_project)
#     app.storage.user['db_projects'] = current_db_projects
#     return new_project

# Simpler: if running from project root, and ui_data.sqlite is there:
DB_FILE = 'ui_data.sqlite'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

# --- Database Interaction Functions ---

def db_load_projects():
    """Loads all projects from the database."""
    print(f"SQL_QUERY: Loading all projects from database: {DB_FILE}")
    projects = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM projects ORDER BY name;")
        rows = cursor.fetchall()
        for row in rows:
            projects.append(dict(row))
    except sqlite3.Error as e:
        print(f"Database error in db_load_projects: {e}")
        ui.notify(f"Error loading projects: {e}", type='negative')
    finally:
        if conn:
            conn.close()
    return projects

def db_create_project(project_name: str):
    """Creates a new project in the database."""
    project_id = project_name.lower().replace(" ", "_") + f"_{str(uuid.uuid4())[:4]}"
    print(f"SQL_QUERY: Creating project '{project_name}' with id '{project_id}' in database: {DB_FILE}")
    created_project_data = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO projects (id, name) VALUES (?, ?) RETURNING id, name;",
                       (project_id, project_name))
        # For SQLite, RETURNING is supported from version 3.35.0
        # If using an older version, you might need to select after insert or just assume success
        # and return the input data.
        # For now, we'll assume RETURNING works or handle if it doesn't fetch.
        row = cursor.fetchone()
        if row:
            created_project_data = dict(row)
        else: # Fallback if RETURNING is not supported or nothing returned
            created_project_data = {"id": project_id, "name": project_name}
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error in db_create_project: {e}")
        ui.notify(f"Error creating project: {e}", type='negative')
        return None # Indicate failure
    finally:
        if conn:
            conn.close()
    return created_project_data


def create_home_page_content() -> None:
    """Creates the content for the home page, including project creation and listing from a DB."""

    # Key for storing projects in app.storage.user (if you were caching, not primary storage)
    # For this example, we'll use a placeholder 'db_projects' to simulate DB interaction via functions.
    # In a real app, db_load_projects() would directly fetch from SQL.

    # Initialize 'db_projects' in app.storage.user if it doesn't exist for placeholder functions
    # This is only for the simulation. A real app wouldn't need this for DB interaction.
    if 'db_projects' not in app.storage.user:
        # Simulate initial data that might be in the DB if it's the first run with this setup
        app.storage.user['db_projects'] = [
            # {"id": "project_alpha_db", "name": "Project Alpha (DB)"}, # Example if pre-populated
        ]


    with ui.column().classes('w-full items-center p-8 gap-8'):
        # Section 1: Create Project Form
        with ui.card().classes('w-full max-w-lg p-6 shadow-lg rounded-lg'):
            ui.label('Create New Project').classes('text-2xl font-semibold mb-4 text-primary')
            project_name_input = ui.input(label='Project Name').classes('w-full')

            def handle_create_project():
                name = project_name_input.value
                if name:
                    # SQL_HOOK: Save the new project to the database
                    created_project = db_create_project(name)
                    if created_project and created_project.get("id"):
                        ui.notify(f'Project "{name}" created. Redirecting to add research streams...',
                                  type='positive')
                        # Refresh the list of projects displayed
                        existing_projects_view.refresh()
                        # Navigate to the research stream page for the new project
                        ui.navigate.to(f'/new-research-stream/{created_project["id"]}')
                        project_name_input.value = ''  # Clear the input
                    else:
                        ui.notify('Failed to create project in the database.', type='negative')
                else:
                    ui.notify('Please enter a project name.', type='warning')

            ui.button('Create Project', on_click=handle_create_project).props('color=primary').classes('w-full mt-4')

        # Separator
        ui.separator().classes('my-4')

        # Section 2: Existing Project Cards
        with ui.column().classes('w-full items-center gap-4'):
            ui.label('Existing Projects').classes('text-3xl font-bold mb-4 text-secondary')

            @ui.refreshable
            def existing_projects_view():
                # SQL_HOOK: Load projects from the database
                projects_from_db = db_load_projects()

                if not projects_from_db:
                    ui.label('No projects yet. Create one above!').classes('text-lg text-gray-500')
                else:
                    # Using a grid for better card layout
                    with ui.grid(columns=1).classes('gap-4 md:grid-cols-2 lg:grid-cols-3 w-full max-w-4xl'):
                        for project in projects_from_db:
                            with ui.card().classes('w-full shadow-md rounded-lg'):
                                with ui.card_section():
                                    ui.label(project["name"]).classes('text-xl font-semibold')

                                ui.separator()

                                with ui.card_actions().classes('justify-end'):
                                    ui.button('Open', on_click=lambda p=project: ui.navigate.to(
                                        f'/project-workspace/{p["id"]}/{p.get("default_stream_id", "general")}')).props('flat color=primary') # Added a placeholder for stream_id
                                    ui.button('Edit Streams', on_click=lambda p=project: ui.navigate.to(
                                        f'/research-streams/{p["id"]}')).props('flat color=secondary')
            existing_projects_view() # Initial call