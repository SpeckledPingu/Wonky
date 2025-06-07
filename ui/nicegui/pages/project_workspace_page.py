# pages/project_workspace_page.py

from nicegui import ui, app
import time  # For simulating AI response delay
import uuid  # For generating unique IDs for new papers
import asyncio  # Added for asyncio.sleep

# Mock data for papers
mock_papers_data = {
    "stream_1": [
        {"id": "paper_a", "title": "The Future of AI in Research",
         "content": "# Paper A\n\nThis is detailed content for Paper A about AI."},
        {"id": "paper_b", "title": "Advanced Quantum Computing",
         "content": "# Paper B\n\nThis is detailed content for Paper B on Quantum Computing."},
        {"id": "paper_c", "title": "Bio-engineering Breakthroughs",
         "content": "# Paper C\n\nThis is detailed content for Paper C regarding Bio-engineering."},
    ],
    "stream_retro_0": [  # Example for a stream that might have a retro ID
        {"id": "paper_x", "title": "Data Analysis Techniques", "content": "# Paper X\n\nContent for data analysis."},
    ],
    "default_stream": [
        {"id": "paper_default", "title": "Generic Research Paper",
         "content": "# Default Paper\n\nThis is some default content if the stream ID is not found."},
    ]
}


def get_paper_title_by_id(paper_id: str) -> str:
    """Helper function to get paper title by its ID from mock_papers_data."""
    for s_id, papers_list in mock_papers_data.items():
        for p in papers_list:
            if p['id'] == paper_id:
                return p['title']
    return "Unknown Paper"


def create_project_workspace_content(project_id: str, stream_id: str) -> None:
    """Creates the content for the Project Workspace page."""
    stream_id = 'stream_1'
    # Dictionary to hold page-specific variables
    page_vars = {
        'current_doc_content': '### Select a paper from the "Papers" tab to view its content here.',
        'chat_messages': [
            {'text': 'Hello! How can I help you with your research today?', 'sent': False,
             'avatar': 'https://robohash.org/ai.png?size=40x40', 'stamp': time.strftime('%H:%M')}
        ],
        'selected_papers_for_chat_or_action': set(),
        'search_results': [],  # To store current search results
    }

    # --- Chat Panel Elements ---
    chat_container_id = f"chat-container-{project_id}-{stream_id}"

    async def send_message(text_input_element):
        user_message_text = text_input_element.value.strip()
        if not user_message_text:
            ui.notify("Please enter a message.", type='warning')
            return
        page_vars['chat_messages'].append({
            'text': user_message_text, 'sent': True,
            'avatar': 'https://robohash.org/user.png?size=40x40', 'stamp': time.strftime('%H:%M')
        })
        text_input_element.value = ''
        chat_messages_display.refresh()
        await ui.run_javascript(
            f"setTimeout(() => {{ const el = document.getElementById('{chat_container_id}'); if(el) el.scrollTop = el.scrollHeight; }}, 0);")
        ai_response_text = f"You said: '{user_message_text}'. That's interesting!"
        if page_vars['selected_papers_for_chat_or_action']:
            first_selected_paper_id = list(page_vars['selected_papers_for_chat_or_action'])[0]
            paper_title_to_discuss = get_paper_title_by_id(first_selected_paper_id)
            ai_response_text += f" Let's discuss '{paper_title_to_discuss}'."
            ui.notify(f"Context from '{paper_title_to_discuss}' was included in the AI's thought process (mock).",
                      type='info')
        if 'selected_papers_display_actions' in page_vars and hasattr(page_vars['selected_papers_display_actions'],
                                                                      'refresh'):
            page_vars['selected_papers_display_actions'].refresh()
        ui.timer(1.0, lambda: add_ai_response(ai_response_text), once=True)

    async def add_ai_response(text):
        page_vars['chat_messages'].append({
            'text': text, 'sent': False,
            'avatar': 'https://robohash.org/ai.png?size=40x40', 'stamp': time.strftime('%H:%M')
        })
        chat_messages_display.refresh()
        await ui.run_javascript(
            f"setTimeout(() => {{ const el = document.getElementById('{chat_container_id}'); if(el) el.scrollTop = el.scrollHeight; }}, 0);")

    # --- UI Layout ---
    with ui.column().classes('w-full h-screen p-0 m-0 gap-0'):
        project_name_display = project_id.replace("_", " ").title()
        stream_name_display = stream_id.replace("_", " ").title()
        ui.label(f'Workspace: {project_name_display} - Stream: {stream_name_display}') \
            .classes('text-xl font-semibold p-4 bg-gray-100 w-full text-center')

        with ui.splitter(value=33).classes('w-full flex-grow') as main_splitter:
            # Left Panel
            with main_splitter.before:
                with ui.column().classes('w-full h-full p-2'):
                    ui.label('Research & Documents').classes('text-lg font-medium mb-2')
                    with ui.tabs().classes('w-full') as left_tabs:
                        papers_tab = ui.tab('Papers', icon='article')
                        document_tab = ui.tab('Document', icon='description')

                    with ui.tab_panels(left_tabs, value=papers_tab).classes(
                            'w-full flex-grow border-t border-gray-300'):
                        with ui.tab_panel(papers_tab).classes('p-2 overflow-auto'):
                            ui.label('Research Papers').classes('text-md font-semibold mb-1')

                            @ui.refreshable
                            def papers_list_display_left_panel():  # Made this refreshable
                                # Ensure the current stream_id has an entry in mock_papers_data
                                if stream_id not in mock_papers_data:
                                    mock_papers_data[stream_id] = []

                                current_stream_papers = mock_papers_data.get(stream_id, [])
                                if not current_stream_papers:
                                    ui.label("No papers found for this stream. Try searching and adding some!")
                                else:
                                    for paper_item in current_stream_papers:
                                        with ui.row().classes('items-center w-full'):
                                            def toggle_paper_for_context(p_id, event_value, current_paper_title):
                                                if event_value:
                                                    page_vars['selected_papers_for_chat_or_action'].add(p_id)
                                                    ui.notify(f'"{current_paper_title}" added to context.',
                                                              type='positive')
                                                else:
                                                    page_vars['selected_papers_for_chat_or_action'].discard(p_id)
                                                    ui.notify(f'"{current_paper_title}" removed from context.',
                                                              type='info')
                                                if 'selected_papers_display_actions' in page_vars and hasattr(
                                                        page_vars['selected_papers_display_actions'], 'refresh'):
                                                    page_vars['selected_papers_display_actions'].refresh()

                                            ui.checkbox(value=paper_item['id'] in page_vars[
                                                'selected_papers_for_chat_or_action'],
                                                        on_change=lambda e, p_id=paper_item['id'], p_title=paper_item[
                                                            'title']: toggle_paper_for_context(p_id, e.value, p_title)) \
                                                .tooltip(f'Add/Remove "{paper_item["title"]}" for chat/actions')

                                            def show_paper_content_closure(p_content_for_closure):
                                                def actual_handler():
                                                    page_vars['current_doc_content'] = p_content_for_closure
                                                    document_markdown_display.refresh()
                                                    left_tabs.set_value(document_tab)

                                                return actual_handler

                                            ui.button(paper_item['title'],
                                                      on_click=show_paper_content_closure(paper_item['content'])) \
                                                .props('flat dense no-caps padding="none"') \
                                                .classes(
                                                'text-primary hover:underline cursor-pointer flex-grow text-left ml-2')

                            papers_list_display_left_panel()  # Initial call
                            page_vars[
                                'papers_list_display_left_panel_ref'] = papers_list_display_left_panel  # Store ref for external refresh

                        with ui.tab_panel(document_tab).classes('p-2 overflow-auto'):
                            ui.label('Selected Document View').classes('text-md font-semibold mb-1')

                            @ui.refreshable
                            def document_markdown_display():
                                ui.markdown(page_vars['current_doc_content'])

                            document_markdown_display()

            # Middle & Right Panels
            with main_splitter.after:
                with ui.splitter(value=50).classes('w-full h-full') as middle_right_splitter:
                    # Middle Panel (Chat & Search)
                    with middle_right_splitter.before:
                        with ui.column().classes('w-full h-full p-2'):
                            ui.label('Interaction Hub').classes('text-lg font-medium mb-2')
                            with ui.tabs().classes('w-full') as middle_tabs:
                                chat_tab_middle = ui.tab('Chat', icon='chat')
                                search_tab_middle = ui.tab('Search', icon='search')

                            with ui.tab_panels(middle_tabs, value=chat_tab_middle).classes(
                                    'w-full flex-grow border-t border-gray-300'):
                                # Chat Tab
                                with ui.tab_panel(chat_tab_middle).classes('p-1 flex flex-col h-full'):
                                    ui.label('AI Chat').classes('text-md font-semibold mb-1')
                                    with ui.column().classes('w-full h-0 flex-grow overflow-y-auto gap-2 p-2').props(
                                            f'id="{chat_container_id}"') as chat_messages_column:
                                        @ui.refreshable
                                        def chat_messages_display():
                                            for msg in page_vars['chat_messages']:
                                                ui.chat_message(text=msg['text'], sent=msg['sent'],
                                                                avatar=msg['avatar'], stamp=msg['stamp']) \
                                                    .classes('w-full')

                                        chat_messages_display()
                                    with ui.row().classes('w-full p-2 items-center border-t mt-auto'):
                                        chat_input = ui.input(placeholder='Type your message...').props(
                                            'outlined dense clearable') \
                                            .classes('flex-grow').on('keydown.enter',
                                                                     lambda e: send_message(chat_input))
                                        ui.button(icon='send', on_click=lambda: send_message(chat_input)) \
                                            .props('round flat color=primary')

                                # Search Tab
                                with ui.tab_panel(search_tab_middle).classes('p-1 flex flex-col h-full'):
                                    ui.label('Ad-hoc Research').classes('text-md font-semibold mb-1')
                                    search_input_middle = ui.input(label='Search Query',
                                                                   placeholder='Enter search terms...').classes(
                                        'w-full')

                                    async def handle_search():
                                        query = search_input_middle.value.strip()
                                        if not query:
                                            ui.notify("Please enter a search query.", type='warning')
                                            return
                                        ui.notify(f"Searching for: '{query}' (mock backend call)...", type='info')
                                        # Simulate backend call & results
                                        await asyncio.sleep(0.5)  # Simulate network delay - Changed to asyncio.sleep
                                        results = []
                                        for i in range(3):  # Generate 3 mock results
                                            new_id = str(uuid.uuid4())  # Unique ID for potential new paper
                                            results.append({
                                                "id": new_id,
                                                "title": f"Search Result {i + 1} for '{query}'",
                                                "content": f"# Search Result: {query}\n\nThis is mock content for search result {i + 1} about '{query}'.\n\nUUID: {new_id}"
                                            })
                                        page_vars['search_results'] = results
                                        search_results_display_middle.refresh()

                                    ui.button('Search', on_click=handle_search).props('color=secondary').classes(
                                        'mt-2 w-full')

                                    ui.separator().classes('my-2')
                                    ui.label("Search Results:").classes('text-sm font-medium')

                                    @ui.refreshable
                                    def search_results_display_middle():
                                        if not page_vars['search_results']:
                                            ui.label("No results to display. Run a search.").classes(
                                                'text-xs text-gray-500')
                                        else:
                                            with ui.column().classes(
                                                    'w-full gap-1 overflow-y-auto flex-grow h-0'):  # Scrollable results
                                                for result in page_vars['search_results']:
                                                    with ui.card().classes('w-full p-2 shadow-sm'):
                                                        with ui.row().classes('w-full items-center justify-between'):
                                                            ui.label(result['title']).classes('text-sm flex-grow')

                                                            def add_search_result_to_papers(
                                                                    res=dict(result)):  # Capture result correctly
                                                                if stream_id not in mock_papers_data:
                                                                    mock_papers_data[stream_id] = []
                                                                # Check if paper with this ID already exists
                                                                if not any(p['id'] == res['id'] for p in
                                                                           mock_papers_data[stream_id]):
                                                                    mock_papers_data[stream_id].append(res)
                                                                    ui.notify(f"'{res['title']}' added to papers.",
                                                                              type='positive')
                                                                    if 'papers_list_display_left_panel_ref' in page_vars:
                                                                        page_vars[
                                                                            'papers_list_display_left_panel_ref'].refresh()
                                                                else:
                                                                    ui.notify(f"'{res['title']}' is already in papers.",
                                                                              type='info')

                                                            ui.button(icon='add_circle_outline', on_click=lambda
                                                                r=result: add_search_result_to_papers(r)) \
                                                                .props('flat dense round color=positive') \
                                                                .tooltip('Add to Papers (Left Panel)')

                                    search_results_display_middle()

                    # Right Panel (Actions & Guided Chat)
                    with middle_right_splitter.after:
                        with ui.column().classes('w-full h-full p-2'):
                            ui.label('Actions & Guidance').classes('text-lg font-medium mb-2')
                            with ui.tabs().classes('w-full') as right_tabs:
                                actions_tab = ui.tab('Actions', icon='build')
                                guided_chat_tab = ui.tab('Guided Chat', icon='question_answer')

                            with ui.tab_panels(right_tabs, value=actions_tab).classes(
                                    'w-full flex-grow border-t border-gray-300 p-2 gap-2'):
                                with ui.tab_panel(actions_tab).classes('p-1 w-full'):
                                    ui.label('Document Actions').classes('text-md font-semibold mb-2')

                                    @ui.refreshable
                                    def selected_papers_display_actions():
                                        if not page_vars['selected_papers_for_chat_or_action']:
                                            ui.label(
                                                "No papers selected. Check boxes in the 'Papers' tab to select.").classes(
                                                'text-sm text-gray-500 mb-2')
                                        else:
                                            ui.label("Selected Papers for Action:").classes('text-sm font-medium mb-1')
                                            with ui.list().props('dense bordered separator').classes(
                                                    'mb-2 w-full rounded-md'):
                                                for paper_id_sel in page_vars['selected_papers_for_chat_or_action']:
                                                    ui.item(get_paper_title_by_id(paper_id_sel)).classes('text-xs')

                                    page_vars['selected_papers_display_actions'] = selected_papers_display_actions
                                    selected_papers_display_actions()

                                    def perform_action(action_name: str):
                                        if not page_vars['selected_papers_for_chat_or_action']:
                                            ui.notify("Please select paper(s) from the 'Papers' tab first.",
                                                      type='warning')
                                            return
                                        selected_titles = [get_paper_title_by_id(pid) for pid in
                                                           page_vars['selected_papers_for_chat_or_action']]
                                        ui.notify(
                                            f"Performing '{action_name}' on: {', '.join(selected_titles)} (mock backend call).",
                                            type='info')

                                    with ui.column().classes('gap-2 w-full'):
                                        ui.button('Summarize Selected', on_click=lambda: perform_action("Summarize")) \
                                            .props('color=primary outline').classes('w-full')
                                        ui.button('Extract Keywords',
                                                  on_click=lambda: perform_action("Extract Keywords")) \
                                            .props('color=secondary outline').classes('w-full')
                                        ui.button('Generate Report Snippet',
                                                  on_click=lambda: perform_action("Generate Report Snippet")) \
                                            .props('color=accent outline').classes('w-full')

                                with ui.tab_panel(guided_chat_tab).classes('p-1 w-full'):
                                    ui.label('Guided Chat Prompts').classes('text-md font-semibold mb-2')
                                    ui.label("Set Persona:").classes("text-sm font-medium mt-2")
                                    with ui.row().classes('gap-2 flex-wrap'):  # Added flex-wrap
                                        personas = ["Economist", "Scientist", "Historian", "Skeptic", "Futurist"]
                                        for p_name in personas:
                                            ui.button(p_name, on_click=lambda name=p_name: ui.notify(
                                                f"Chat persona set to '{name}' (mock). Next message will use this.",
                                                type='info')) \
                                                .props('color=info outline dense')
                                    ui.label("Explore Tangents:").classes("text-sm font-medium mt-4")
                                    with ui.row().classes('gap-2 flex-wrap'):  # Added flex-wrap
                                        tangents = ["Devil's Advocate", "Assumptions?", "Alternatives?",
                                                    "Implications?", "Ethical Concerns"]
                                        for t_name in tangents:
                                            ui.button(t_name, on_click=lambda name=t_name: ui.notify(
                                                f"Next AI response will explore: '{name}' (mock).", type='info')) \
                                                .props('color=warning outline dense')

