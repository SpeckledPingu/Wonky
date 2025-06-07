# pages/home_page.py

from nicegui import ui

# Placeholder for projects data. In a real app, this would come from a database or app.storage.
mock_projects = [
    {"id": "project_alpha", "name": "Project Alpha"},
    {"id": "project_beta", "name": "Project Beta"},
    {"id": "project_gamma", "name": "Project Gamma"},
]


def create_home_page_content() -> None:
    """Creates the content for the home page, including project creation and listing."""
    with ui.column().classes('w-full items-center p-8 gap-8'):
        # Section 1: Create Project Form
        with ui.card().classes('w-full max-w-lg p-6 shadow-lg rounded-lg'):
            ui.label('Create New Project').classes('text-2xl font-semibold mb-4 text-primary')
            project_name_input = ui.input(label='Project Name').classes('w-full')

            def handle_create_project():
                name = project_name_input.value
                if name:
                    ui.notify(f'Project "{name}" would be created. Redirecting to add research streams...',
                              type='positive')
                    # In a real app, you'd save the project and then redirect.
                    # For now, we'll simulate the redirect.
                    # The project name or ID would typically be part of the URL.
                    ui.navigate.to(f'/new-research-stream/{name.lower().replace(" ", "_")}')
                    project_name_input.value = ''  # Clear the input
                else:
                    ui.notify('Please enter a project name.', type='warning')

            ui.button('Create Project', on_click=handle_create_project).props('color=primary').classes('w-full mt-4')

        # Separator
        ui.separator().classes('my-4')

        # Section 2: Existing Project Cards
        with ui.column().classes('w-full items-center gap-4'):
            ui.label('Existing Projects').classes('text-3xl font-bold mb-4 text-secondary')
            if not mock_projects:
                ui.label('No projects yet. Create one above!').classes('text-lg text-gray-500')
            else:
                # Using a grid for better card layout
                with ui.grid(columns=1).classes('gap-4 md:grid-cols-2 lg:grid-cols-3 w-full max-w-4xl'):
                    for project in mock_projects:
                        with ui.card().classes('w-full shadow-md rounded-lg'):
                            with ui.card_section():
                                ui.label(project["name"]).classes('text-xl font-semibold')

                            ui.separator()

                            with ui.card_actions().classes('justify-end'):
                                # Placeholder actions - these would navigate to different pages
                                ui.button('Open', on_click=lambda p=project: ui.navigate.to(
                                    f'/project-workspace/{p["id"]}')).props('flat color=primary')
                                ui.button('Edit Streams', on_click=lambda p=project: ui.navigate.to(
                                    f'/research-streams/{p["id"]}')).props('flat color=secondary')
