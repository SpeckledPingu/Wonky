CREATE TABLE IF NOT EXISTS insights (
    citation TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    result_id TEXT NOT NULL,
    insight_type TEXT,
    insight_name TEXT,
    insight_synopsis TEXT,
    related_citations TEXT,
    insight_text TEXT,
    insight_data TEXT,
    text TEXT,
    FOREIGN KEY (result_id) REFERENCES search_results(result_id)
);

CREATE TABLE IF NOT EXISTS policies (
    citation TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    result_id TEXT NOT NULL,
    source_document_id TEXT,
    policy_name TEXT,
    policy_type TEXT,
    primary_objective TEXT,
    mechanism_of_action TEXT,
    policy_details TEXT,
    key_stakeholders TEXT, -- Stored as a JSON object
    authors_apparent_stance TEXT,
    specific_evidence TEXT,
    policy_text TEXT,
    arguments_in_favor TEXT,  -- Stored as a JSON array
    arguments_against TEXT,   -- Stored as a JSON array
    locations_in_source TEXT, -- Stored as a JSON array
    FOREIGN KEY (result_id) REFERENCES search_results(result_id)
);

CREATE TABLE IF NOT EXISTS search_results (
    run_id TEXT NOT NULL,
    result_id TEXT PRIMARY KEY,
    title TEXT,
    summary TEXT,
    source_file TEXT,
    start_index INTEGER,
    end_index INTEGER,
    chunk_id TEXT,
    id TEXT,
    type TEXT,
    typeId TEXT,
    active INTEGER,
    source TEXT,
    topics TEXT,
    version_id TEXT,
    date TEXT,
    _distance REAL,
    grounding TEXT
);