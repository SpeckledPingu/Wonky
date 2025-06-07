# pages/prompt_composer_page.py
from nicegui import ui, app
from collections import defaultdict
import httpx
import asyncio

# --- API Configuration ---
API_BASE_URL = "http://localhost:8000"  # Adjust if your API runs elsewhere
api_client = httpx.AsyncClient(base_url=API_BASE_URL)
PLACEHOLDER_USER_ID = "current_user_example"  # Replace with actual user auth logic


# --- API Interaction Functions ---

async def api_load_components_for_user(user_id: str):
    try:
        response = await api_client.get(f"/users/{user_id}/prompt-components")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        ui.notify(f"Error loading components: {e.response.status_code}", type='negative')
        return []
    except httpx.RequestError:
        ui.notify("Network error loading components.", type='negative')
        return []


async def api_load_library_for_user(user_id: str):
    try:
        response = await api_client.get(f"/users/{user_id}/prompt-library")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        ui.notify(f"Error loading library items: {e.response.status_code}", type='negative')
        return []
    except httpx.RequestError:
        ui.notify("Network error loading library items.", type='negative')
        return []


async def api_save_prompt_component(user_id: str, component_data: dict):
    try:
        # component_data should contain name, type, content
        response = await api_client.post(f"/users/{user_id}/prompt-components", json=component_data)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        ui.notify(f"Error saving component: {e.response.status_code} - {e.response.text}", type='negative',
                  multi_line=True)
        return None
    except httpx.RequestError:
        ui.notify("Network error saving component.", type='negative')
        return None


async def api_save_library_item(user_id: str, item_data: dict):
    try:
        # item_data should contain name, type, content
        response = await api_client.post(f"/users/{user_id}/prompt-library", json=item_data)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        ui.notify(f"Error saving library item: {e.response.status_code} - {e.response.text}", type='negative',
                  multi_line=True)
        return None
    except httpx.RequestError:
        ui.notify("Network error saving library item.", type='negative')
        return None


async def api_delete_prompt_component(user_id: str, component_id: str):
    try:
        response = await api_client.delete(f"/users/{user_id}/prompt-components/{component_id}")
        response.raise_for_status()
        return True
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            ui.notify(f"Component '{component_id}' not found for deletion.", type='warning')
        else:
            ui.notify(f"Error deleting component: {e.response.status_code}", type='negative')
        return False
    except httpx.RequestError:
        ui.notify("Network error deleting component.", type='negative')
        return False


async def api_delete_library_item(user_id: str, item_id: str):
    try:
        response = await api_client.delete(f"/users/{user_id}/prompt-library/{item_id}")
        response.raise_for_status()
        return True
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            ui.notify(f"Library item '{item_id}' not found for deletion.", type='warning')
        else:
            ui.notify(f"Error deleting library item: {e.response.status_code}", type='negative')
        return False
    except httpx.RequestError:
        ui.notify("Network error deleting library item.", type='negative')
        return False


async def create_prompt_composer_page_content():  # Made async
    """Creates the UI for the prompt composer page, fetching data from an API."""

    composer_textarea_ref = [None]

    # --- Helper Functions ---
    def add_content_to_composer(content_to_add: str):
        if composer_textarea_ref[0]:
            current_value = composer_textarea_ref[0].value or ""
            composer_textarea_ref[0].set_value(f"{current_value}\n{content_to_add}".strip())
            ui.notify("Content added to composer.", type='positive')
        else:
            ui.notify("Composer text area not ready.", type='negative')

    def view_and_add_dialog(item: dict, item_category: str):
        with ui.dialog() as dialog, ui.card().classes('min-w-[400px] max-w-[600px]'):
            ui.label(f"Viewing: {item['name']}").classes('text-h6 font-medium text-gray-700')
            ui.badge(f"{item_category.capitalize()}: {item['type']}",
                     color='blue' if item_category == 'component' else 'green').classes('my-1')
            with ui.scroll_area().classes('h-48 border p-3 rounded-md my-3 bg-gray-50 text-sm'):
                ui.markdown(item['content'])
            with ui.row().classes('w-full justify-end pt-2 gap-x-2'):
                ui.button("Add to Composer",
                          on_click=lambda: (add_content_to_composer(item['content']), dialog.close()),
                          icon='add_circle_outline', color='primary')
                ui.button("Close", on_click=dialog.close, color='gray').props('outline')
        dialog.open()

    async def delete_item_handler(item_id: str, list_type: str):  # Renamed and made async
        current_user_id = PLACEHOLDER_USER_ID
        success = False
        if list_type == "component":
            success = await api_delete_prompt_component(current_user_id, item_id)
            if success:
                components_pane_ui.refresh()
                ui.notify("Component deleted.", type='info')
        elif list_type == "library":
            success = await api_delete_library_item(current_user_id, item_id)
            if success:
                library_pane_ui.refresh()
                ui.notify("Library prompt deleted.", type='info')
        # ui.notify for errors is handled within api_delete functions

    # --- UI Panes (Refreshable) ---
    @ui.refreshable
    async def components_pane_ui():  # Made async
        ui.label("Prompt Components").classes('text-xl font-semibold mb-3 text-blue-700')
        current_components = await api_load_components_for_user(PLACEHOLDER_USER_ID)
        if not current_components:
            ui.label("No components available for this user.").classes('text-gray-500 italic')
            return

        components_by_type = defaultdict(list)
        for comp in current_components:
            components_by_type[comp['type']].append(comp)
        sorted_types = sorted(components_by_type.keys())

        for comp_type in sorted_types:
            with ui.expansion(text=comp_type.capitalize(), icon='category').classes('w-full rounded-lg mb-2'):
                with ui.column().classes('gap-y-3 w-full p-2'):
                    if not components_by_type[comp_type]:
                        ui.label(f"No {comp_type} components available.").classes('text-gray-400 italic text-sm ml-2')
                    for comp in components_by_type[comp_type]:
                        with ui.card().classes(
                                'w-full shadow-md hover:shadow-lg transition-shadow duration-150 ease-in-out'):
                            with ui.card_section():
                                ui.label(comp["name"]).classes('text-lg font-medium text-gray-800')
                                ui.markdown(
                                    f"_{comp['content'][:80]}{'...' if len(comp['content']) > 80 else ''}_").classes(
                                    'text-sm text-gray-600 mt-1 h-12 overflow-hidden')
                            with ui.card_actions().classes('justify-start q-pt-none mt-2'):
                                ui.button("View/Add", on_click=lambda c=comp: view_and_add_dialog(c, "component"),
                                          icon='visibility', color='primary').props('dense flat')
                                ui.button(icon='delete_outline',
                                          on_click=lambda c_id=comp.get("id"): delete_item_handler(c_id, "component"),
                                          color='red-500').props('flat dense round')

    @ui.refreshable
    async def library_pane_ui():  # Made async
        ui.label("Prompt Library").classes('text-xl font-semibold mb-3 text-green-700')
        current_library_items = await api_load_library_for_user(PLACEHOLDER_USER_ID)
        if not current_library_items:
            ui.label("No library prompts available for this user.").classes('text-gray-500 italic')
            return

        library_items_by_type = defaultdict(list)
        for lib_item in current_library_items:
            library_items_by_type[lib_item['type']].append(lib_item)
        sorted_types = sorted(library_items_by_type.keys())

        for lib_type in sorted_types:
            with ui.expansion(text=lib_type.capitalize(), icon='collections_bookmark').classes(
                    'w-full rounded-lg mb-2'):
                with ui.column().classes('gap-y-3 w-full p-2'):
                    if not library_items_by_type[lib_type]:
                        ui.label(f"No {lib_type} library items available.").classes('text-gray-400 italic text-sm ml-2')
                    for lib_item in library_items_by_type[lib_type]:
                        with ui.card().classes(
                                'w-full shadow-md hover:shadow-lg transition-shadow duration-150 ease-in-out'):
                            with ui.card_section():
                                ui.label(lib_item["name"]).classes('text-lg font-medium text-gray-800')
                                ui.markdown(
                                    f"_{lib_item['content'][:80]}{'...' if len(lib_item['content']) > 80 else ''}_").classes(
                                    'text-sm text-gray-600 mt-1 h-12 overflow-hidden')
                            with ui.card_actions().classes('justify-start q-pt-none mt-2'):
                                ui.button("View/Add",
                                          on_click=lambda item=lib_item: view_and_add_dialog(item, "library"),
                                          icon='visibility', color='primary').props('dense flat')
                                ui.button(icon='delete_outline',
                                          on_click=lambda l_id=lib_item.get("id"): delete_item_handler(l_id, "library"),
                                          color='red-500').props('flat dense round')

    # --- Main Page Layout ---
    with ui.splitter(value=30).classes('w-full h-screen') as main_splitter:
        with main_splitter.before:
            with ui.column().classes('p-4 w-full h-full overflow-auto bg-blue-50 rounded-lg shadow-inner'):
                await components_pane_ui()  # Initial call

        with main_splitter.after:
            with ui.splitter(value=50, horizontal=False).classes('w-full h-full') as right_area_splitter:
                with right_area_splitter.before:
                    with ui.column().classes('p-4 w-full h-full overflow-auto bg-gray-100 rounded-lg shadow-inner'):
                        ui.label("Prompt Composer").classes('text-xl font-semibold mb-4 text-purple-700')

                        main_type_options = {"Component": "Prompt Component", "Library": "Prompt Library"}
                        main_type_select = ui.select(main_type_options, label="1. Save to which collection?",
                                                     value="Component").classes('w-full mt-1')
                        prompt_name_input = ui.input(label="2. Give it a name").classes('w-full mt-3')
                        subtype_select = ui.select([], label="3. Select specific type").classes('w-full mt-3')

                        def update_subtype_options(e=None):
                            target_value = main_type_select.value
                            new_options = ["rules", "reasoning"] if target_value == "Component" else ["actions",
                                                                                                      "personas"]
                            subtype_select.options = new_options
                            if new_options and (subtype_select.value not in new_options or not subtype_select.value):
                                subtype_select.set_value(new_options[0])
                            elif not new_options:
                                subtype_select.set_value(None)

                        main_type_select.on('update:model-value', update_subtype_options)
                        update_subtype_options()  # Initial call

                        ui.label("4. Compose or edit prompt content:").classes(
                            'mt-4 mb-1 text-sm font-medium text-gray-600')
                        composer_textarea_ref[0] = ui.textarea(value='').props('outlined filled rows=30').classes(
                            'w-full mt-1 bg-white')

                        async def save_prompt():  # Made async
                            current_user_id = PLACEHOLDER_USER_ID
                            name = prompt_name_input.value
                            content = composer_textarea_ref[0].value if composer_textarea_ref[0] else ""
                            specific_type = subtype_select.value
                            save_to_collection_key = main_type_select.value

                            if not all([name, content, specific_type, save_to_collection_key]):
                                ui.notify("All fields are required.", type='negative')
                                return

                            new_item_data = {"name": name, "type": specific_type, "content": content}
                            saved_item = None

                            if save_to_collection_key == "Component":
                                saved_item = await api_save_prompt_component(current_user_id, new_item_data)
                                if saved_item:
                                    components_pane_ui.refresh()
                                    ui.notify("Prompt component saved!", type='positive')
                            elif save_to_collection_key == "Library":
                                saved_item = await api_save_library_item(current_user_id, new_item_data)
                                if saved_item:
                                    library_pane_ui.refresh()
                                    ui.notify("Prompt library item saved!", type='positive')

                            if saved_item:  # Clear form only on successful save
                                prompt_name_input.set_value("")
                                if composer_textarea_ref[0]:
                                    composer_textarea_ref[0].set_value("")
                            # ui.notify for errors handled by api_save functions

                        ui.button("Save Prompt", on_click=save_prompt, icon='save').classes(
                            'mt-5 w-full bg-purple-600 text-white hover:bg-purple-700 py-2 text-base')

                with right_area_splitter.after:
                    with ui.column().classes('p-4 w-full h-full overflow-auto bg-green-50 rounded-lg shadow-inner'):
                        await library_pane_ui()  # Initial call