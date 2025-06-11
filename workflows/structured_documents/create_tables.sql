CREATE TABLE IF NOT EXISTS research_runs (
    run_id TEXT,
    project_id TEXT,
    run_timestamp TEXT,
    subject_matter TEXT,
    focus TEXT,
    analysis_type TEXT,
    id TEXT,
    type TEXT,
    typeId TEXT,
    number TEXT,
    active INTEGER, -- 0 for false, 1 for true
    topics TEXT,    -- Store as JSON string or comma-separated values
    date TEXT,      -- Store as ISO8601 string (e.g., "YYYY-MM-DD")
    title TEXT,
    summary TEXT,
    doc_id TEXT,
    filename TEXT,
    source_file TEXT,
    source_document TEXT,
    source_dataset TEXT
);

CREATE TABLE IF NOT EXISTS overviews (
    run_id TEXT,
    run_timestamp TEXT,
    project_id TEXT,
    subject_matter TEXT,
    focus TEXT,
    analysis_type TEXT,
    overview TEXT,
    overview_citations TEXT,
    overview_type TEXT,
    overview_pages TEXT,
    source_document TEXT,
    source_dataset TEXT
);

CREATE TABLE IF NOT EXISTS overview_sources (
    run_id TEXT,
    run_timestamp TEXT,
    project_id TEXT,
    subject_matter TEXT,
    focus TEXT,
    analysis_type TEXT,
    text TEXT,
    citation TEXT,
    source_document TEXT,
    source_dataset TEXT
);

-- DROP TABLE IF EXISTS research_runs;
-- DROP TABLE IF EXISTS overviews;
-- DROP TABLE IF EXISTS overview_sources;
-- DROP TABLE IF EXISTS projects;

CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT,
    project_name TEXT,
    project_timestamp TEXT,
    project_goal TEXT,
    project_description TEXT

);

CREATE TABLE IF NOT EXISTS dynamic_actions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    action_type TEXT,
    output_destination TEXT,
    prompt_template TEXT,
    ui_group TEXT,
    required_inputs TEXT, -- JSON string, e.g., '[{"name": "subject", "label": "Subject Matter", "type": "text", "required": true}]'
    is_user_defined INTEGER
);

INSERT INTO dynamic_actions (id, name, description, action_type, output_destination, prompt_template, ui_group, required_inputs, is_user_defined)
VALUES
('generate_custom_summary', 'Generate Custom Summary', 'Generates a summary based on user-provided subject and focus.', 'process_documents', 'new_document', 'Summarize the selected documents focusing on {subject_matter} regarding {focus}. Selected documents:\n{selected_doc_titles_list}', 'document_actions',
'[
    {"name": "subject_matter", "label": "Subject Matter", "type": "text", "required": true, "default": "General Overview"},
    {"name": "focus", "label": "Specific Focus", "type": "textarea", "required": true, "default": "Key challenges and opportunities"},
    {"name": "max_length", "label": "Max Summary Length (words)", "type": "number", "required": false, "default": 250}
]', 1);