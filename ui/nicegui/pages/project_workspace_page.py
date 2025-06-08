# pages/project_workspace_page.py

from nicegui import ui, app
import uuid
import asyncio
# import sqlite3 # No longer needed for direct DB access
from datetime import datetime
import httpx  # Added for API calls

# --- API Configuration ---
API_BASE_URL = "http://localhost:8000"  # Adjust if your API runs elsewhere
api_client = httpx.AsyncClient(base_url=API_BASE_URL)


# --- API Interaction Functions ---
# ... (existing API functions remain unchanged) ...
async def api_get_project_details(project_id: str):
    """Fetches project details (name) from the API."""
    try:
        response = await api_client.get(f"/projects/{project_id}")
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"API error in api_get_project_details: {e}")
        ui.notify(f"Error fetching project details: {e.response.status_code}", type='negative')
        return None
    except httpx.RequestError as e:
        print(f"Request error in api_get_project_details: {e}")
        ui.notify("Network error fetching project details.", type='negative')
        return None


async def api_get_stream_details(stream_id: str):
    """Fetches research stream details (subject, focus) from the API."""
    try:
        response = await api_client.get(f"/streams/{stream_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"API error in api_get_stream_details: {e}")
        ui.notify(f"Error fetching stream details: {e.response.status_code}", type='negative')
        return None
    except httpx.RequestError as e:
        print(f"Request error in api_get_stream_details: {e}")
        ui.notify("Network error fetching stream details.", type='negative')
        return None


async def api_load_papers_for_stream(project_id: str, stream_id: str):
    """Loads all papers for a given project and stream from the API."""
    try:
        response = await api_client.get(f"/projects/{project_id}/streams/{stream_id}/papers")
        response.raise_for_status()
        return response.json()  # Returns a list of paper dicts
    except httpx.HTTPStatusError as e:
        print(f"API error in api_load_papers_for_stream: {e}")
        ui.notify(f"Error loading papers: {e.response.status_code}", type='negative')
        return []
    except httpx.RequestError as e:
        print(f"Request error in api_load_papers_for_stream: {e}")
        ui.notify("Network error loading papers.", type='negative')
        return []


async def api_delete_paper_from_stream(project_id: str, stream_id: str, paper_id: str) -> bool:
    """Deletes a specific paper from a stream via the API."""
    try:
        response = await api_client.delete(f"/projects/{project_id}/streams/{stream_id}/papers/{paper_id}")
        response.raise_for_status()
        print(f"Paper '{paper_id}' deleted successfully via API from project '{project_id}', stream '{stream_id}'.")
        return True
    except httpx.HTTPStatusError as e:
        print(f"API error in api_delete_paper_from_stream: {e}")
        if e.response.status_code == 404:
            ui.notify(f"Paper '{paper_id}' not found for deletion.", type='warning')
        else:
            ui.notify(f"Error deleting paper via API: {e.response.status_code}", type='negative')
        return False
    except httpx.RequestError as e:
        print(f"Request error in api_delete_paper_from_stream: {e}")
        ui.notify("Network error deleting paper.", type='negative')
        return False


async def api_add_paper_to_stream(project_id: str, stream_id: str, paper_data: dict):
    """Adds a new paper to the stream via the API."""
    payload = {
        "id": paper_data.get("id"),
        "title": paper_data.get("title", "Untitled Paper"),
        "content": paper_data.get("content", "# New Paper")
    }
    try:
        response = await api_client.post(f"/projects/{project_id}/streams/{stream_id}/papers", json=payload)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"API error in api_add_paper_to_stream: {e}")
        ui.notify(f"Error adding paper via API: {e.response.status_code} - {e.response.text}", type='negative',
                  multi_line=True)
        return None
    except httpx.RequestError as e:
        print(f"Request error in api_add_paper_to_stream: {e}")
        ui.notify("Network error adding paper.", type='negative')
        return None


async def api_load_chat_messages(project_id: str, stream_id: str):
    """Loads all chat messages for a given project and stream from the API."""
    try:
        response = await api_client.get(f"/projects/{project_id}/streams/{stream_id}/chat/messages")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"API error in api_load_chat_messages: {e}")
        ui.notify(f"Error loading chat messages: {e.response.status_code}", type='negative')
        return []
    except httpx.RequestError as e:
        print(f"Request error in api_load_chat_messages: {e}")
        ui.notify("Network error loading chat messages.", type='negative')
        return []


async def api_save_chat_message(project_id: str, stream_id: str, message_data: dict):
    """Adds a new chat message to the stream via the API."""
    payload = {
        "id": message_data.get("id"),
        "text": message_data.get("text"),
        "sent_by_user": message_data.get("sent_by_user"),
        "avatar": message_data.get("avatar")
    }
    try:
        response = await api_client.post(f"/projects/{project_id}/streams/{stream_id}/chat/messages", json=payload)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"API error in api_save_chat_message: {e}")
        ui.notify(f"Error sending message via API: {e.response.status_code} - {e.response.text}", type='negative',
                  multi_line=True)
        return None
    except httpx.RequestError as e:
        print(f"Request error in api_save_chat_message: {e}")
        ui.notify("Network error sending message.", type='negative')
        return None


async def api_clear_chat_messages(project_id: str, stream_id: str) -> bool:
    """Deletes all chat messages for a given project and stream via the API."""
    try:
        response = await api_client.delete(f"/projects/{project_id}/streams/{stream_id}/chat/messages")
        response.raise_for_status()
        print(f"Chat messages cleared via API. Rows affected: {response.json().get('rows_affected')}")
        return True
    except httpx.HTTPStatusError as e:
        print(f"API error in api_clear_chat_messages: {e}")
        ui.notify(f"Error clearing chat via API: {e.response.status_code}", type='negative')
        return False
    except httpx.RequestError as e:
        print(f"Request error in api_clear_chat_messages: {e}")
        ui.notify("Network error clearing chat.", type='negative')
        return False


async def api_get_dynamic_actions_by_group(ui_group: str) -> list[dict]:
    """Fetches dynamic actions/prompts for a specific UI group from the API."""
    try:
        response = await api_client.get(f"/dynamic-actions", params={"ui_group": ui_group})
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"API error in api_get_dynamic_actions_by_group: {e}")
        ui.notify(f"Error fetching dynamic actions: {e.response.status_code}", type='negative')
        return []
    except httpx.RequestError as e:
        print(f"Request error in api_get_dynamic_actions_by_group: {e}")
        ui.notify("Network error fetching dynamic actions.", type='negative')
        return []


async def api_get_dynamic_action_by_id(action_id: str) -> dict | None:
    """Fetches a specific dynamic action/prompt by its ID from the API."""
    try:
        response = await api_client.get(f"/dynamic-actions/{action_id}")
        response.raise_for_status()
        print('response')
        print(response.json())
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"API error in api_get_dynamic_action_by_id: {e}")
        if e.response.status_code == 404:
            ui.notify(f"Dynamic action '{action_id}' not found.", type='warning')
        else:
            ui.notify(f"Error fetching dynamic action details: {e.response.status_code}", type='negative')
        return None
    except httpx.RequestError as e:
        print(f"Request error in api_get_dynamic_action_by_id: {e}")
        ui.notify("Network error fetching dynamic action details.", type='negative')
        return None

# --- Helper Function ---
def get_paper_title_by_id_from_list(paper_id: str, papers_list: list) -> str:
    """Helper function to get paper title by its ID from a list of paper dicts."""
    for p in papers_list:
        if p.get('id') == paper_id:
            return p.get('title', "Untitled Paper")
    return "Unknown Paper"

# --- UI Helper Function for Scrolling ---
async def scroll_chat_to_bottom(container_id: str):
    """Runs JavaScript to scroll the specified container to its bottom."""
    print(container_id)
    await ui.run_javascript(
        f"setTimeout(() => {{ const el = document.getElementById('{container_id}'); if(el) el.scrollTop = el.scrollHeight; }}, 0);"
    )

# --- Action Processing Function (Simulates Backend Interaction) ---
async def process_dynamic_action(
        project_id: str,
        stream_id: str,
        action_id: str,
        selected_paper_ids: list[str],
        page_ui_state: dict,
        _context
):
    action_details = await api_get_dynamic_action_by_id(action_id)
    if not action_details:
        print('no action details')
        return

    action_name = action_details.get('name', 'Unknown Action')
    action_type = action_details.get('action_type')
    output_destination = action_details.get('output_destination')
    prompt_template = action_details.get('prompt_template', "")

    with _context:
        ui.notify(f"Initiating '{action_name}'...", type='info')

    context_info = ""
    doc_titles_for_prompt = []

    if action_type == 'process_documents':
        if not selected_paper_ids:
            with _context:
                ui.notify(f"Please select paper(s) from the 'Papers' tab to perform '{action_name}'.", type='warning')
            page_ui_state['last_action_completed_details'] = {
                'action_name': action_name, 'status': 'warning',
                'message': f"Action '{action_name}' not performed: No papers selected.",
                'timestamp': datetime.now().isoformat()
            }
            return
        current_papers = await api_load_papers_for_stream(project_id, stream_id)
        selected_titles = [get_paper_title_by_id_from_list(pid, current_papers) for pid in selected_paper_ids]
        doc_titles_for_prompt = selected_titles
        context_info = f" on: {', '.join(selected_titles)}"
        if not selected_titles or all(title == "Unknown Paper" for title in selected_titles):
            ui.notify(f"Could not find titles for selected papers for '{action_name}'.", type='warning')

    final_prompt_text = prompt_template
    if '{selected_doc_titles_list}' in final_prompt_text:
        titles_list_str = "\n - " + "\n - ".join(doc_titles_for_prompt) if doc_titles_for_prompt else "N/A"
        final_prompt_text = final_prompt_text.replace('{selected_doc_titles_list}', titles_list_str)

    chat_input_ref = page_ui_state.get('chat_input_ref')
    send_message_func = page_ui_state.get('send_message_func')
    chat_messages_display_ref = page_ui_state.get('chat_messages_display_ref')
    chat_container_id = page_ui_state.get('chat_container_id')

    action_successful = True

    if output_destination == 'chat_message':
        if action_type in ['set_chat_persona', 'inject_chat_prompt']:
            if chat_input_ref and send_message_func:
                chat_input_ref.value = final_prompt_text
                await send_message_func(chat_input_ref) # This will handle its own scrolling
                ui.notify(f"'{action_name}' prompt added to chat.", type='positive')
            else:
                ui.notify("Chat interface not available to inject prompt.", type='error')
                action_successful = False
        elif action_type == 'process_documents':
            ai_response_text = f"AI response for '{action_name}'{context_info}:\n{final_prompt_text}\n(This is a mock response based on the action.)"
            ai_msg_data = {
                'id': f'chat_ai_action_{uuid.uuid4().hex[:6]}',
                'text': ai_response_text,
                'sent_by_user': False,
                'avatar': 'https://robohash.org/ai_action.png?size=40x40',
            }
            saved_ai_msg = await api_save_chat_message(project_id, stream_id, ai_msg_data)
            if saved_ai_msg:
                print(chat_container_id)
                if chat_messages_display_ref:
                    chat_messages_display_ref.refresh()
                if chat_container_id:
                    await scroll_chat_to_bottom(chat_container_id) # Use helper
                ui.notify(f"'{action_name}' processed. See chat for mock AI response.", type='positive')
            else:
                ui.notify("Failed to save AI action response via API.", type='error')
                action_successful = False
        else:
            ui.notify(f"Unsupported action type '{action_type}' for chat message output.", type='warning')
            action_successful = False

    elif output_destination == 'new_document':
        payload_for_backend = {
            "project_id": project_id, "stream_id": stream_id, "action_id": action_id,
            "action_name": action_name, "selected_paper_ids": selected_paper_ids, "prompt": final_prompt_text
        }
        print(f"PAYLOAD FOR NEW DOCUMENT (mock backend call): {payload_for_backend}")
        with _context:
            ui.notify(
            f"'{action_name}'{context_info} would trigger generation of a new document (see console for mock payload).",
            type='info', multi_line=True, close_button='OK')
        await asyncio.sleep(1.5)

    else:
        with _context:
            ui.notify(f"Unknown output destination '{output_destination}' for action '{action_name}'.", type='warning')
        action_successful = False

    async def final_notification_task():
        await asyncio.sleep(0.1)
        page_ui_state['last_action_completed_details'] = {
            'action_name': action_name,
            'status': 'success' if action_successful else 'error',
            'timestamp': datetime.now().isoformat()
        }
    asyncio.create_task(final_notification_task())


async def create_project_workspace_content(project_id: str, stream_id: str) -> None:
    """Creates the content for the Project Workspace page using an API backend."""

    project_details = await api_get_project_details(project_id)
    stream_details_from_db = await api_get_stream_details(stream_id)

    project_name_for_display = project_details.get('name', project_id.replace("_",
                                                                              " ").title()) if project_details else project_id.replace(
        "_", " ").title()
    stream_name_for_display = stream_details_from_db.get('subject', stream_id.replace("_",
                                                                                      " ").title()) if stream_details_from_db else stream_id.replace(
        "_", " ").title()

    page_ui_state = {
        'current_doc_content': '### Select a paper from the "Papers" tab to view its content here.',
        'selected_papers_for_chat_or_action': set(),
        'search_results': [],
        'papers_list_display_left_panel_ref': None,
        'selected_papers_display_actions_ref': None,
        'chat_messages_display_ref': None,
        'ai_response_pending': False,
        'chat_input_ref': None,
        'send_message_func': None,
        'chat_container_id': f"chat-container-{project_id}-{stream_id}",
        'last_action_completed_details': None,
    }

    async def notify_on_action_completion():
        action_details = page_ui_state.get('last_action_completed_details')
        if action_details:
            action_name_completed = action_details.get('action_name', 'The action')
            status = action_details.get('status', 'success')
            message_type = 'positive'
            if status == 'error': message_type = 'negative'
            elif status == 'warning': message_type = 'warning'
            custom_message = action_details.get('message')
            if custom_message:
                ui.notify(custom_message, type=message_type, multi_line=True, close_button='OK')
            else:
                ui.notify(
                    f"'{action_name_completed}' has finished its background processing. "
                    f"You can now manually refresh relevant sections if needed (e.g., Papers list).",
                    type=message_type, multi_line=True, close_button='OK')
            page_ui_state['last_action_completed_details'] = None
    ui.timer(interval=5, callback=notify_on_action_completion, active=True)

    async def handle_clear_chat():
        with ui.dialog() as dialog, ui.card():
            ui.label('Are you sure you want to clear the entire chat history for this stream?')
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Clear Chat', on_click=lambda: dialog.submit('clear'), color='negative')
        result = await dialog
        if result == 'clear':
            if await api_clear_chat_messages(project_id, stream_id):
                ui.notify("Chat history cleared.", type='positive')
                if page_ui_state['chat_messages_display_ref']:
                    page_ui_state['chat_messages_display_ref'].refresh()
                    # Optionally, scroll to bottom even after clear, though it might be empty
                    await scroll_chat_to_bottom(page_ui_state['chat_container_id'])


    async def send_message(text_input_element):
        user_message_text = text_input_element.value.strip()
        if not user_message_text:
            ui.notify("Please enter a message.", type='warning')
            return

        user_msg_data = {
            'id': f'chat_user_{uuid.uuid4().hex[:6]}',
            'text': user_message_text,
            'sent_by_user': True,
            'avatar': 'https://robohash.org/user.png?size=40x40',
        }
        saved_user_msg = await api_save_chat_message(project_id, stream_id, user_msg_data)

        if saved_user_msg:
            text_input_element.value = ''
            if page_ui_state['chat_messages_display_ref']:
                page_ui_state['chat_messages_display_ref'].refresh()
            await scroll_chat_to_bottom(page_ui_state['chat_container_id']) # Use helper
        else:
            return # Don't proceed to AI response if user message failed to save

        ai_response_text = f"You said: '{user_message_text}'. That's interesting!"
        if page_ui_state['selected_papers_for_chat_or_action']:
            current_papers_for_context = await api_load_papers_for_stream(project_id, stream_id)
            if current_papers_for_context:
                first_selected_paper_id = list(page_ui_state['selected_papers_for_chat_or_action'])[0]
                paper_title_to_discuss = get_paper_title_by_id_from_list(first_selected_paper_id,
                                                                         current_papers_for_context)
                if paper_title_to_discuss != "Unknown Paper":
                    ai_response_text += f" Let's discuss '{paper_title_to_discuss}'."
                    ui.notify(
                        f"Context from '{paper_title_to_discuss}' was included in the AI's thought process (mock).",
                        type='info')

        if page_ui_state['selected_papers_display_actions_ref'] and hasattr(
                page_ui_state['selected_papers_display_actions_ref'], 'refresh'):
            page_ui_state['selected_papers_display_actions_ref'].refresh()

        async def trigger_ai_response_task():
            await asyncio.sleep(1.0) # Simulate AI thinking time
            ai_msg_data = {
                'id': f'chat_ai_{uuid.uuid4().hex[:6]}',
                'text': ai_response_text,
                'sent_by_user': False,
                'avatar': 'https://robohash.org/ai.png?size=40x40',
            }
            saved_ai_msg = await api_save_chat_message(project_id, stream_id, ai_msg_data)
            if saved_ai_msg:
                page_ui_state['ai_response_pending'] = True # Signal that an AI response is ready

        asyncio.create_task(trigger_ai_response_task())

    page_ui_state['send_message_func'] = send_message

    with ui.column().classes('w-full h-[calc(100vh-100px)] p-0 m-0 gap-0'):
        ui.label(f'Workspace: {project_name_for_display} - Stream: {stream_name_for_display}') \
            .classes('text-xl font-semibold p-4 bg-gray-100 w-full text-center')

        with ui.splitter(value=33).classes('w-full flex-grow') as main_splitter:
            with main_splitter.before:
                # ... (Left panel code remains unchanged) ...
                with ui.column().classes('w-full h-full p-2'):
                    ui.label('Research & Documents').classes('text-lg font-medium mb-2')
                    with ui.tabs().classes('w-full') as left_tabs:
                        papers_tab = ui.tab('Papers', icon='article')
                        document_tab = ui.tab('Document', icon='description')

                    with ui.tab_panels(left_tabs, value=papers_tab).classes(
                            'w-full flex-grow border-t border-gray-300'):
                        with ui.tab_panel(papers_tab).classes('p-2 overflow-auto'):

                            @ui.refreshable
                            async def papers_list_display_left_panel():
                                with ui.row().classes('w-full items-center justify-between mb-1'):
                                    ui.label('Research Papers').classes('text-md font-semibold')
                                    ui.button(icon='refresh', on_click=lambda: papers_list_display_left_panel.refresh()) \
                                        .props('flat dense round').tooltip('Refresh paper list')

                                def _handle_toggle_paper_for_context(paper_id: str, is_selected: bool,
                                                                     paper_title: str):
                                    if is_selected:
                                        page_ui_state['selected_papers_for_chat_or_action'].add(paper_id)
                                        ui.notify(f"'{paper_title}' added to context for actions.", type='positive')
                                    else:
                                        page_ui_state['selected_papers_for_chat_or_action'].discard(paper_id)
                                        ui.notify(f"'{paper_title}' removed from context for actions.", type='info')
                                    if page_ui_state.get('selected_papers_display_actions_ref'):
                                        page_ui_state['selected_papers_display_actions_ref'].refresh()

                                current_stream_papers = await api_load_papers_for_stream(project_id, stream_id)
                                if not current_stream_papers:
                                    ui.label("No papers found. Try searching and adding some!")
                                else:
                                    for paper_item in current_stream_papers:
                                        p_id = paper_item.get('id')
                                        p_title = paper_item.get('title', 'Untitled Paper')
                                        p_content = paper_item.get('content', 'No content.')

                                        with ui.row().classes('items-center w-full no-wrap'):
                                            ui.checkbox(
                                                value=p_id in page_ui_state['selected_papers_for_chat_or_action'],
                                                on_change=lambda e, paper_id=p_id, paper_title=p_title:
                                                _handle_toggle_paper_for_context(paper_id, e.value, paper_title)) \
                                                .tooltip(f'Add/Remove "{p_title}" for chat/actions') \


                                            def show_paper_content_closure(p_content_for_closure, paper_id_for_closure):
                                                async def actual_handler():
                                                    page_ui_state['current_doc_content'] = p_content_for_closure
                                                    page_ui_state['current_viewed_paper_id'] = paper_id_for_closure
                                                    document_markdown_display.refresh()
                                                    left_tabs.set_value(document_tab)
                                                return actual_handler

                                            ui.button(p_title, on_click=show_paper_content_closure(p_content, p_id)) \
                                                .props('flat dense no-caps padding="none"') \
                                                .classes('text-primary hover:underline cursor-pointer flex-grow text-left ml-2 mr-1 truncatel')

                                            async def request_paper_deletion(paper_id_to_delete, paper_title_to_delete):
                                                with ui.dialog() as confirm_dialog, ui.card():
                                                    ui.label(f"Are you sure you want to delete '{paper_title_to_delete}'?")
                                                    with ui.row().classes('w-full justify-end'):
                                                        ui.button('Cancel', on_click=confirm_dialog.close).props('flat')
                                                        ui.button('Delete', color='negative', on_click=lambda: confirm_dialog.submit('delete'))
                                                result = await confirm_dialog
                                                if result == 'delete':
                                                    if await api_delete_paper_from_stream(project_id, stream_id, paper_id_to_delete):
                                                        ui.notify(f"Paper '{paper_title_to_delete}' deleted.", type='positive')
                                                        if paper_id_to_delete in page_ui_state['selected_papers_for_chat_or_action']:
                                                            page_ui_state['selected_papers_for_chat_or_action'].discard(paper_id_to_delete)
                                                            if page_ui_state['selected_papers_display_actions_ref']:
                                                                page_ui_state['selected_papers_display_actions_ref'].refresh()
                                                        if page_ui_state.get('current_viewed_paper_id') == paper_id_to_delete:
                                                            page_ui_state['current_doc_content'] = '### Select a paper from the "Papers" tab to view its content here.'
                                                            page_ui_state['current_viewed_paper_id'] = None
                                                            document_markdown_display.refresh()
                                                        papers_list_display_left_panel.refresh()

                                            ui.button(icon='delete_outline',
                                                      on_click=lambda paper_id=p_id, paper_title=p_title: request_paper_deletion(paper_id, paper_title)) \
                                                .props('flat dense round color=negative icon-size=small padding="xs"') \
                                                .tooltip('Delete this paper')

                            async def check_new_papers():
                                try:
                                    response = await api_client.get(f"/projects/{project_id}/streams/{stream_id}/papers/check_new_papers")
                                    response.raise_for_status()
                                    if len(response.json()) > 0:
                                        ui.notify('New papers found!')
                                        await api_client.post(f"/projects/{project_id}/streams/{stream_id}/papers/clear_new_papers")
                                        papers_list_display_left_panel.refresh()
                                except httpx.HTTPStatusError as e:
                                    print(f"API error checking new papers: {e}")
                                    # Potentially notify user, but could be noisy for a polling check
                                except httpx.RequestError as e:
                                    print(f"Request error checking new papers: {e}")
                                    # Potentially notify user

                            ui.timer(interval=10, callback=check_new_papers, active=True)
                            await papers_list_display_left_panel()
                            page_ui_state['papers_list_display_left_panel_ref'] = papers_list_display_left_panel

                        with ui.tab_panel(document_tab).classes('p-2 overflow-auto'):
                            ui.label('Selected Document View').classes('text-md font-semibold mb-1')
                            @ui.refreshable
                            def document_markdown_display():
                                ui.markdown(page_ui_state['current_doc_content'])
                            document_markdown_display()


            with main_splitter.after:
                with ui.splitter(value=50).classes('w-full h-full') as middle_right_splitter:
                    with middle_right_splitter.before:
                        with ui.column().classes('w-full h-full p-2'):
                            ui.label('Interaction Hub').classes('text-lg font-medium mb-2')
                            with ui.tabs().classes('w-full') as middle_tabs:
                                chat_tab_middle = ui.tab('Chat', icon='chat')
                                search_tab_middle = ui.tab('Search', icon='search')

                            with ui.tab_panels(middle_tabs, value=chat_tab_middle).classes(
                                    'w-full flex-grow border-t border-gray-300'):
                                with ui.tab_panel(chat_tab_middle).classes('p-1 flex flex-col h-full'):
                                    with ui.row().classes('w-full items-center justify-between mb-1'):
                                        ui.label('AI Chat').classes('text-md font-semibold')
                                        ui.button('Clear Chat', on_click=handle_clear_chat, icon='delete_sweep') \
                                            .props('flat dense color=negative').tooltip(
                                            'Clear all messages in this chat')

                                    with ui.column().classes('w-full h-0 flex-grow overflow-y-auto gap-2 p-2').props(
                                            f'id="{page_ui_state["chat_container_id"]}"') as chat_messages_container_element:
                                        @ui.refreshable
                                        async def chat_messages_display():
                                            messages_to_display = await api_load_chat_messages(project_id, stream_id)
                                            if not messages_to_display:
                                                ui.label("No messages yet. Start the conversation!").classes(
                                                    "text-xs text-gray-500 p-2")
                                            for msg in messages_to_display:
                                                ui.chat_message(text=msg.get('text'),
                                                                sent=msg.get('sent_by_user'),
                                                                avatar=msg.get('avatar'),
                                                                stamp=msg.get('timestamp_display')) \
                                                    .classes('w-full')

                                        page_ui_state['chat_messages_display_ref'] = chat_messages_display
                                        await page_ui_state['chat_messages_display_ref']()

                                        async def check_for_ai_response_and_update_ui():
                                            if page_ui_state.get('ai_response_pending'):
                                                if page_ui_state['chat_messages_display_ref']:
                                                    page_ui_state['chat_messages_display_ref'].refresh()
                                                await scroll_chat_to_bottom(page_ui_state['chat_container_id']) # Use helper
                                                page_ui_state['ai_response_pending'] = False

                                        ui.timer(interval=0.2, callback=check_for_ai_response_and_update_ui,
                                                 active=True)

                                    with ui.row().classes('w-full p-2 items-center border-t mt-auto'):
                                        chat_input = ui.input(placeholder='Type your message...').props(
                                            'outlined dense clearable') \
                                            .classes('flex-grow').on('keydown.enter',
                                                                     lambda e: send_message(chat_input))
                                        page_ui_state['chat_input_ref'] = chat_input
                                        ui.button(icon='send', on_click=lambda: send_message(chat_input)).props(
                                            'round flat color=primary')

                                with ui.tab_panel(search_tab_middle).classes('p-1 flex flex-col h-full'):
                                    # ... (Search tab code remains unchanged) ...
                                    async def handle_search():
                                        query = search_input_middle.value.strip()
                                        if not query:
                                            ui.notify("Please enter a search query.", type='warning')
                                            return
                                        ui.notify(f"Searching for: '{query}' (mock backend call)...", type='info')
                                        await asyncio.sleep(0.5)
                                        results = []
                                        for i in range(3):
                                            new_id = f"search_res_{uuid.uuid4().hex[:8]}"
                                            results.append({
                                                "id": new_id,
                                                "title": f"Search Result {i + 1} for '{query}'",
                                                "content": f"# Search Result: {query}\n\nThis is mock content for search result {i + 1} about '{query}'.\n\nUUID: {new_id}"
                                            })
                                        page_ui_state['search_results'] = results
                                        search_results_display_middle.refresh()

                                    @ui.refreshable
                                    def search_results_display_middle():
                                        if not page_ui_state['search_results']:
                                            ui.label("No results to display. Run a search.").classes('text-xs text-gray-500')
                                        else:
                                            with ui.column().classes('w-full gap-1 overflow-y-auto flex-grow h-0'):
                                                for result in page_ui_state['search_results']:
                                                    with ui.card().classes('w-full p-2 shadow-sm'):
                                                        async def add_search_result_to_papers_handler(res_to_add):
                                                            paper_data_for_api = {
                                                                "id": res_to_add.get("id"),
                                                                "title": res_to_add.get("title"),
                                                                "content": res_to_add.get("content")
                                                            }
                                                            saved_paper = await api_add_paper_to_stream(project_id, stream_id, paper_data_for_api)
                                                            if saved_paper:
                                                                ui.notify(f"'{saved_paper.get('title')}' added to papers.", type='positive')
                                                                if page_ui_state['papers_list_display_left_panel_ref']:
                                                                    page_ui_state['papers_list_display_left_panel_ref'].refresh()

                                                        with ui.row().classes('w-full items-center justify-between'):
                                                            ui.label(result.get('title')).classes('text-sm flex-grow')
                                                            ui.button(icon='add_circle_outline',
                                                                      on_click=lambda r=dict(result): add_search_result_to_papers_handler(r)) \
                                                                .props('flat dense round color=positive').tooltip('Add to Papers (Left Panel)')

                                    ui.label('Ad-hoc Research').classes('text-md font-semibold mb-1')
                                    search_input_middle = ui.input(label='Search Query', placeholder='Enter search terms...').classes('w-full')
                                    ui.button('Search', on_click=handle_search).props('color=secondary').classes('mt-2 w-full')
                                    ui.separator().classes('my-2')
                                    ui.label("Search Results:").classes('text-sm font-medium')
                                    search_results_display_middle()


                    with middle_right_splitter.after:
                        # ... (Right panel code remains unchanged) ...
                        with ui.column().classes('w-full h-full p-2'):
                            ui.label('Actions & Guidance').classes('text-lg font-medium mb-2')
                            with ui.tabs().classes('w-full') as right_tabs:
                                actions_tab = ui.tab('Actions', icon='build')
                                guided_chat_tab = ui.tab('Guided Chat', icon='question_answer')

                            with ui.tab_panels(right_tabs, value=actions_tab).classes('w-full flex-grow border-t border-gray-300 p-2 gap-2') as main_actions_tab:
                                with ui.tab_panel(actions_tab).classes('p-1 w-full'):
                                    ui.label('Document Actions').classes('text-md font-semibold mb-2')
                                    @ui.refreshable
                                    async def selected_papers_display_actions():
                                        if not page_ui_state['selected_papers_for_chat_or_action']:
                                            ui.label("No papers selected...").classes('text-sm text-gray-500 mb-2')
                                        else:
                                            ui.label("Selected Papers for Action:").classes('text-sm font-medium mb-1')
                                            current_papers_for_actions = await api_load_papers_for_stream(project_id, stream_id)
                                            with ui.list().props('dense bordered separator').classes('mb-2 w-full rounded-md'):
                                                for paper_id_sel in sorted(list(page_ui_state['selected_papers_for_chat_or_action'])):
                                                    title = get_paper_title_by_id_from_list(paper_id_sel, current_papers_for_actions)
                                                    ui.item(title).classes('text-xs')
                                    page_ui_state['selected_papers_display_actions_ref'] = selected_papers_display_actions
                                    await selected_papers_display_actions()

                                    document_actions = await api_get_dynamic_actions_by_group('document_actions')
                                    if not document_actions:
                                        ui.label("No document actions configured.").classes('text-xs text-gray-500')
                                    else:
                                        with ui.column().classes('gap-2 w-full mt-2'):
                                            for action_item in document_actions:
                                                ui.button(
                                                    action_item['name'],
                                                    on_click=lambda bound_action_id=action_item['id']: asyncio.create_task(
                                                        process_dynamic_action(
                                                            project_id, stream_id, bound_action_id,
                                                            list(page_ui_state['selected_papers_for_chat_or_action']),
                                                            page_ui_state, middle_right_splitter # Pass context for notifications
                                                        ))
                                                ).props('color=primary outline').classes('w-full').tooltip(action_item.get('description', ''))

                                with ui.tab_panel(guided_chat_tab).classes('p-1 w-full') as guided_tab_container:
                                    ui.label('Guided Chat Prompts').classes('text-md font-semibold mb-2')
                                    ui.label("Set Persona:").classes("text-sm font-medium mt-2")
                                    guided_personas = await api_get_dynamic_actions_by_group('guided_personas')
                                    if not guided_personas:
                                        ui.label("No personas configured.").classes('text-xs text-gray-500')
                                    else:
                                        with ui.row().classes('gap-2 flex-wrap'):
                                            for persona_action in guided_personas:
                                                ui.button(
                                                    persona_action['name'],
                                                    on_click=lambda bound_action_id=persona_action['id']: asyncio.create_task(
                                                        process_dynamic_action(
                                                            project_id, stream_id, bound_action_id, [], page_ui_state, guided_tab_container # Pass context
                                                        ))
                                                ).props('color=info outline dense').tooltip(persona_action.get('description', ''))

                                    ui.label("Explore Tangents:").classes("text-sm font-medium mt-4")
                                    guided_tangents = await api_get_dynamic_actions_by_group('guided_tangents')
                                    if not guided_tangents:
                                        ui.label("No tangents configured.").classes('text-xs text-gray-500')
                                    else:
                                        with ui.row().classes('gap-2 flex-wrap'):
                                            for tangent_action in guided_tangents:
                                                ui.button(
                                                    tangent_action['name'],
                                                    on_click=lambda bound_action_id=tangent_action['id']: asyncio.create_task(
                                                        process_dynamic_action(
                                                            project_id, stream_id, bound_action_id, [], page_ui_state, guided_tab_container # Pass context
                                                        ))
                                                ).props('color=warning outline dense').tooltip(tangent_action.get('description', ''))