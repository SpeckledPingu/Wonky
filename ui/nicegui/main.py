# main.py

from nicegui import ui

# Import page creation functions and shared components
from pages import home_page
from pages import research_stream_page
from pages import project_workspace_page
from pages import prompt_composer_page # Import the new prompt composer page module
from shared import header

# Define the routes for each page
@ui.page('/')
def show_home_page():
    """Displays the home page with the shared header."""
    header.create_header()
    home_page.create_home_page_content()

@ui.page('/new-research-stream/{project_identifier}')
def show_research_stream_page(project_identifier: str):
    """Displays the page for adding research streams to a project."""
    header.create_header()
    research_stream_page.create_research_stream_page_content(project_identifier)

@ui.page('/project-workspace/{project_id}/{stream_id}')
def show_project_workspace_page(project_id: str, stream_id: str):
    """Displays the Project Workspace page."""
    # header.create_header() # Often omitted for complex full-page UIs
    project_workspace_page.create_project_workspace_content(project_id, stream_id)

@ui.page('/research-streams/{project_id}')
def show_edit_research_streams_page(project_id: str):
    """Displays page for managing research streams (can be same as creation)."""
    header.create_header()
    research_stream_page.create_research_stream_page_content(project_id)

# Route for the new Prompt Composer page
@ui.page('/prompt-composer')
def show_prompt_composer_page():
    """Displays the Prompt Composer page."""
    # This page might also have its own header or none if it's a tool-like interface
    header.create_header()
    prompt_composer_page.create_prompt_composer_page_content()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(storage_secret='app')
