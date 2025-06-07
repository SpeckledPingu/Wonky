# pages/research_stream_page.py

from nicegui import ui, app
import httpx  # Added for API calls
import asyncio  # For async operations

# --- API Configuration ---
API_BASE_URL = "http://localhost:8000"  # Adjust if your API runs elsewhere
api_client = httpx.AsyncClient(base_url=API_BASE_URL)


# --- API Interaction Functions ---

async def api_load_streams_for_project(project_id: str):
    """Loads all research streams for a given project from the API."""
    try:
        response = await api_client.get(f"/projects/{project_id}/streams")
        response.raise_for_status()
        return response.json()  # Returns a list of stream dicts
    except httpx.HTTPStatusError as e:
        print(f"API error in api_load_streams_for_project: {e}")
        ui.notify(f"Error loading streams: {e.response.status_code}", type='negative')
        return []
    except httpx.RequestError as e:
        print(f"Request error in api_load_streams_for_project: {e}")
        ui.notify("Network error loading streams.", type='negative')
        return []


async def api_add_stream_to_project(project_id: str, stream_data: dict):
    """Adds a new research stream to a project via the API."""
    # stream_data should contain 'subject' and 'focus'
    payload = {
        "subject": stream_data.get('subject'),
        "focus": stream_data.get('focus')
    }
    try:
        response = await api_client.post(f"/projects/{project_id}/streams", json=payload)
        response.raise_for_status()
        return response.json()  # Returns the created stream dict
    except httpx.HTTPStatusError as e:
        print(f"API error in api_add_stream_to_project: {e}")
        ui.notify(f"Error adding stream: {e.response.status_code} - {e.response.text}", type='negative',
                  multi_line=True)
        return None
    except httpx.RequestError as e:
        print(f"Request error in api_add_stream_to_project: {e}")
        ui.notify("Network error adding stream.", type='negative')
        return None


async def api_delete_stream(project_id: str, stream_id: str):
    """Deletes a research stream via the API."""
    try:
        response = await api_client.delete(f"/projects/{project_id}/streams/{stream_id}")
        response.raise_for_status()
        print(f"Stream '{stream_id}' deleted successfully via API for project '{project_id}'.")
        return True  # Or response.json() if API returns a meaningful body
    except httpx.HTTPStatusError as e:
        print(f"API error in api_delete_stream: {e}")
        if e.response.status_code == 404:
            ui.notify(f"Stream '{stream_id}' not found for deletion.", type='warning')
        else:
            ui.notify(f"Error deleting stream via API: {e.response.status_code}", type='negative')
        return False
    except httpx.RequestError as e:
        print(f"Request error in api_delete_stream: {e}")
        ui.notify("Network error deleting stream.", type='negative')
        return False


async def create_research_stream_page_content(project_identifier: str) -> None:  # Made async
    """Creates the content for the research stream management page using an API backend."""

    with ui.column().classes('w-full items-center p-8 gap-8'):
        project_name_display = project_identifier.replace("_", " ").title()
        ui.label(f'Research Streams for: {project_name_display}').classes('text-3xl font-bold mb-4 text-primary')

        with ui.card().classes('w-full max-w-lg p-6 shadow-lg rounded-lg'):
            ui.label('Add New Research Stream').classes('text-2xl font-semibold mb-4')
            subject_input = ui.input(label='Subject Matter').classes('w-full')
            focus_input = ui.input(label='Focus Area').classes('w-full')

            async def handle_add_stream():  # Made async
                subject = subject_input.value
                focus = focus_input.value
                if subject and focus:
                    new_stream_data = {"subject": subject, "focus": focus}
                    # Call API to add stream
                    stream_from_api = await api_add_stream_to_project(project_identifier, new_stream_data)

                    if stream_from_api and stream_from_api.get("id"):
                        ui.notify(f'Research stream "{subject}" added via API.', type='positive')
                        subject_input.value = ''
                        focus_input.value = ''
                        research_streams_view.refresh()
                    # else: ui.notify handled by api_add_stream_to_project
                else:
                    ui.notify('Please fill in both subject matter and focus.', type='warning')

            ui.button('Add Research Stream', on_click=handle_add_stream).props('color=primary').classes('w-full mt-4')

        ui.separator().classes('my-4')
        ui.label('Current Research Streams').classes('text-2xl font-bold mb-2 text-secondary')

        async def handle_delete_stream_ui(p_id: str, stream_to_delete: dict):  # Made async
            stream_id_to_delete = stream_to_delete.get("id")
            if not stream_id_to_delete:
                ui.notify("Cannot delete stream: ID is missing.", type='error')
                return

            # Call API to delete stream
            if await api_delete_stream(p_id, stream_id_to_delete):
                ui.notify(f'Research stream "{stream_to_delete.get("subject", "Unknown")}" deleted via API.',
                          type='info')
                research_streams_view.refresh()
            # else: ui.notify handled by api_delete_stream

        def handle_run_research(p_id: str, stream_data: dict):  # This can remain sync
            stream_subject = stream_data.get("subject", "unknown_stream")
            stream_identifier = stream_data.get("id")
            if not stream_identifier:
                ui.notify("Error: Stream ID is missing for navigation.", type='error')
                return

            ui.notify(f'Navigating to workspace for: "{stream_subject}"...', type='info')
            ui.navigate.to(f'/project-workspace/{p_id}/{stream_identifier}')

        @ui.refreshable
        async def research_streams_view():  # Made async
            streams = await api_load_streams_for_project(project_identifier)  # Load from API
            if not streams:
                ui.label('No research streams added yet for this project.').classes('text-lg text-gray-500')
            else:
                with ui.column().classes('w-full max-w-lg gap-2'):
                    for stream in streams:  # stream is already a dict from API
                        if not stream.get("id"):
                            ui.label(f"Warning: Stream '{stream.get('subject')}' missing ID.").classes(
                                'text-red-500 text-xs')
                            continue

                        with ui.card().classes('w-full p-4 shadow rounded-md'):
                            with ui.row().classes('w-full justify-between items-center'):
                                with ui.column().classes('flex-grow'):
                                    ui.label(f"Subject: {stream.get('subject', 'N/A')}").classes('font-semibold')
                                    ui.label(f"Focus: {stream.get('focus', 'N/A')}")
                                with ui.row().classes('gap-2 items-center'):
                                    ui.button('Run Research',
                                              on_click=lambda s=stream: handle_run_research(project_identifier, s)) \
                                        .props('color=positive dense') \
                                        .tooltip('Open workspace for this stream')
                                    ui.button(icon='delete',
                                              on_click=lambda s=stream: handle_delete_stream_ui(project_identifier, s)) \
                                        .props('flat color=negative dense round') \
                                        .tooltip('Delete this stream')

        await research_streams_view()  # Initial call for the async refreshable