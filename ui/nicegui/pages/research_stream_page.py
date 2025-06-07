# pages/research_stream_page.py

from nicegui import ui, app
import urllib.parse  # For encoding stream subject for URL

# In-memory storage for research streams.
# In a real application, this would be stored in a database or app.storage.user.
# Structure: { "project_id_1": [{"subject": "Subj1", "focus": "Focus1"}, ...], ... }
# if not hasattr(app, 'storage'):  # Initialize if not present (for simplicity in this example)
#     app.storage.user = {}
# if 'project_research_streams' not in app.storage.user:
#     app.storage.user['project_research_streams'] = {}


def create_research_stream_page_content(project_identifier: str) -> None:
    """Creates the content for the research stream management page."""

    # Ensure the project has an entry in our streams storage
    if 'project_research_streams' not in app.storage.user:
        app.storage.user['project_research_streams'] = {}
    if project_identifier not in app.storage.user['project_research_streams']:
        app.storage.user['project_research_streams'][project_identifier] = []

    with ui.column().classes('w-full items-center p-8 gap-8'):
        project_name_display = project_identifier.replace("_", " ").title()
        ui.label(f'Research Streams for: {project_name_display}').classes('text-3xl font-bold mb-4 text-primary')

        # Section 1: Form to Create New Research Stream
        with ui.card().classes('w-full max-w-lg p-6 shadow-lg rounded-lg'):
            ui.label('Add New Research Stream').classes('text-2xl font-semibold mb-4')
            subject_input = ui.input(label='Subject Matter').classes('w-full')
            focus_input = ui.input(label='Focus Area').classes('w-full')

            def handle_add_stream():
                subject = subject_input.value
                focus = focus_input.value
                if subject and focus:
                    # Simple way to give a unique ID to a stream for this session
                    stream_id = f"stream_{len(app.storage.user['project_research_streams'][project_identifier]) + 1}"
                    new_stream = {"id": stream_id, "subject": subject, "focus": focus}
                    app.storage.user['project_research_streams'][project_identifier].append(new_stream)
                    ui.notify(f'Research stream "{subject}" added.', type='positive')
                    subject_input.value = ''
                    focus_input.value = ''
                    research_streams_view.refresh()  # Refresh the list display
                else:
                    ui.notify('Please fill in both subject matter and focus.', type='warning')

            ui.button('Add Research Stream', on_click=handle_add_stream).props('color=primary').classes('w-full mt-4')

        # Separator
        ui.separator().classes('my-4')

        # Section 2: List of Existing Research Streams for this project
        ui.label('Current Research Streams').classes('text-2xl font-bold mb-2 text-secondary')

        def handle_delete_stream(project_id: str, stream_to_delete: dict):
            """Deletes a specific research stream for a given project."""
            try:
                # Find and remove the stream by its unique ID if available, or by object match
                original_list = app.storage.user['project_research_streams'][project_id]
                item_to_remove = next((s for s in original_list if s.get("id") == stream_to_delete.get("id")), None)
                if item_to_remove:
                    original_list.remove(item_to_remove)
                else:  # Fallback for older items without ID or if ID match fails
                    original_list.remove(stream_to_delete)

                ui.notify(f'Research stream "{stream_to_delete.get("subject", "Unknown")}" deleted.', type='info')
                research_streams_view.refresh()
            except (ValueError, KeyError) as e:
                ui.notify(f'Error deleting stream: {e}', type='negative')

        def handle_run_research(project_id: str, stream_data: dict):
            """Simulates running research and navigates to the workspace."""
            stream_subject = stream_data.get("subject", "unknown_stream")
            # For a more robust URL, use a stream ID if available, otherwise slugify the subject
            stream_identifier = stream_data.get("id", urllib.parse.quote_plus(stream_subject.lower().replace(" ", "_")))

            ui.notify(f'Simulating research API call for: "{stream_subject}"...', type='info')
            # Here you would typically make an async http call
            # await some_async_http_client.post(f"/api/research/{project_id}/{stream_identifier}")
            ui.navigate.to(f'/project-workspace/{project_id}/{stream_identifier}')

        @ui.refreshable
        def research_streams_view():
            streams = app.storage.user['project_research_streams'].get(project_identifier, [])
            if not streams:
                ui.label('No research streams added yet for this project.').classes('text-lg text-gray-500')
            else:
                with ui.column().classes('w-full max-w-lg gap-2'):
                    for stream_index, stream in enumerate(streams):
                        # Ensure each stream has an ID for robust deletion/identification
                        if "id" not in stream:  # Retroactively add ID if missing
                            stream["id"] = f"stream_retro_{stream_index}"

                        with ui.card().classes('w-full p-4 shadow rounded-md'):
                            with ui.row().classes('w-full justify-between items-center'):
                                with ui.column().classes('flex-grow'):  # Allow text to take space
                                    ui.label(f"Subject: {stream['subject']}").classes('font-semibold')
                                    ui.label(f"Focus: {stream['focus']}")

                                with ui.row().classes('gap-2 items-center'):  # Group buttons
                                    ui.button('Run Research',
                                              on_click=lambda s=dict(stream): handle_run_research(project_identifier,
                                                                                                  s)) \
                                        .props('color=positive dense') \
                                        .tooltip('Run research for this stream')

                                    ui.button(icon='delete',
                                              on_click=lambda s=dict(stream): handle_delete_stream(project_identifier,
                                                                                                   s)) \
                                        .props('flat color=negative dense round') \
                                        .tooltip('Delete this stream')

        research_streams_view()  # Initial call to display the list
