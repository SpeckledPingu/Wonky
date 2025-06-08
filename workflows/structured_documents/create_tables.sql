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