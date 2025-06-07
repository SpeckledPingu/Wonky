# main.py

from nicegui import ui

# Import page creation functions and shared components
from pages import home_page
from pages import research_stream_page
from pages import project_workspace_page
from pages import prompt_composer_page # Ensure this is the correct module name
from shared import header

# Define the routes for each page
@ui.page('/')
def show_home_page():
    header.create_header()
    home_page.create_home_page_content()

@ui.page('/new-research-stream/{project_identifier}')
async def show_research_stream_page(project_identifier: str):
    header.create_header()
    await research_stream_page.create_research_stream_page_content(project_identifier)

@ui.page('/project-workspace/{project_id}/{stream_id}')
async def show_project_workspace_page(project_id: str, stream_id: str):
    header.create_header()
    await project_workspace_page.create_project_workspace_content(project_id, stream_id)

@ui.page('/research-streams/{project_id}')
async def show_edit_research_streams_page(project_id: str):
    header.create_header()
    await research_stream_page.create_research_stream_page_content(project_id)

# Route for the Prompt Composer page
@ui.page('/prompt-composer')
async def show_prompt_composer_page(): # Made async
    header.create_header()
    await prompt_composer_page.create_prompt_composer_page_content() # Added await


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(storage_secret='app_secret_key_change_me_please')