# shared/header.py

from nicegui import ui

def create_header() -> None:
    """Creates a shared header for the website."""
    with ui.header().classes('bg-primary text-white p-4 shadow-md'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('My NiceGUI Website').classes('text-2xl font-semibold')
            with ui.row().classes('items-center'):
                ui.link('Home', '/').classes('text-white hover:text-accent-focus mx-2 text-lg')
                ui.link('Workspace', '/project-workspace').classes('text-white hover:text-accent-focus mx-2 text-lg')
                ui.link('Prompt Composer', '/prompt-composer').classes('text-white hover:text-accent-focus mx-2 text-lg')
                # Add more links here as we create more pages
                # For example:
                # ui.link('About', '/about').classes('text-white hover:text-accent-focus mx-2 text-lg')
