-- Table for storing research papers associated with a project and stream
CREATE TABLE papers (
    id TEXT PRIMARY KEY, -- Assuming UUIDs or similar text-based IDs
    project_id TEXT NOT NULL,
    stream_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    -- Optional: Foreign keys if you have projects and research_streams tables
    -- FOREIGN KEY (project_id) REFERENCES projects(id),
    -- FOREIGN KEY (stream_id) REFERENCES research_streams(id)
    -- Consider an index for faster lookups by project_id and stream_id
);

-- Table for storing chat messages within a project and stream
CREATE TABLE chat_messages (
    id TEXT PRIMARY KEY, -- Assuming UUIDs or similar text-based IDs
    project_id TEXT NOT NULL,
    stream_id TEXT NOT NULL,
    text TEXT NOT NULL,
    sent_by_user BOOLEAN NOT NULL,
    avatar TEXT, -- URL to an avatar image
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    -- Optional: Foreign keys
    -- FOREIGN KEY (project_id) REFERENCES projects(id),
    -- FOREIGN KEY (stream_id) REFERENCES research_streams(id)
    -- Index for ordering and filtering
);


-- Table for storing user-specific prompt components
CREATE TABLE prompt_components (
    id TEXT PRIMARY KEY,                      -- Unique identifier for the component
    user_id TEXT NOT NULL,                    -- Identifier for the user who owns this component
    name TEXT NOT NULL,                       -- Name of the prompt component
    type TEXT NOT NULL,                       -- Type/category of the component (e.g., 'rules', 'reasoning')
    content TEXT NOT NULL,                    -- The actual content of the prompt component
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp of creation
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp of last update
    -- Optional: FOREIGN KEY (user_id) REFERENCES users(id) -- If you have a users table
    -- Consider an index for faster lookups by user_id
);

-- Table for storing user-specific prompt library items
CREATE TABLE prompt_library (
    id TEXT PRIMARY KEY,                      -- Unique identifier for the library item
    user_id TEXT NOT NULL,                    -- Identifier for the user who owns this item
    name TEXT NOT NULL,                       -- Name of the library item
    type TEXT NOT NULL,                       -- Type/category of the library item (e.g., 'personas', 'actions')
    content TEXT NOT NULL,                    -- The actual content of the library item
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp of creation
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp of last update
    -- Optional: FOREIGN KEY (user_id) REFERENCES users(id) -- If you have a users table
    -- Consider an index for faster lookups by user_id
);


-- Table for storing research streams associated with a project
-- CREATE TABLE research_streams (
--     id TEXT PRIMARY KEY);-- Unique identifier for

DROP TABLE if exists research_streams;
CREATE TABLE research_streams (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    focus TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Table for storing projects
CREATE TABLE projects
(
    id   TEXT PRIMARY KEY, -- Unique identifier for the project (e.g., "project_alpha")
    name TEXT NOT NULL    -- The display name of the project (e.g., "Project Alpha")
);

-- Mock data for 'projects' table
-- INSERT INTO projects (id, name) VALUES
-- ('project_alpha_2', 'Project Alpha Alphass'),
-- ('project_beta', 'Project Beta'),
-- ('project_gamma', 'Project Gamma');
--
-- -- Mock data for 'research_streams' table
-- -- Assuming research_streams needs more than just an ID, based on research_stream_page.py
-- -- Let's add project_id, subject, and focus.
-- -- If your 'research_streams' table is truly just 'id TEXT PRIMARY KEY',
-- -- you'll need to adjust it or this mock data.
-- -- For now, I'll assume it should be more comprehensive like:
-- -- CREATE TABLE research_streams (
-- --     id TEXT PRIMARY KEY,
-- --     project_id TEXT NOT NULL,
-- --     subject TEXT NOT NULL,
-- --     focus TEXT NOT NULL,
-- --     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
-- --     FOREIGN KEY (project_id) REFERENCES projects(id)
-- -- );
-- -- If you update your table, use the inserts below. If not, you'll need to simplify these.
--
-- -- To make this runnable with your current schema, I'll just insert IDs.
-- -- However, this means the other Python files (like research_stream_page.py)
-- -- which expect subject/focus won't be able to get that from a DB query on this table alone.
-- -- The application currently stores this extra info in app.storage.user or derives it.
--
-- INSERT INTO research_streams (id) VALUES
-- ('rs_alpha_1'), -- Belongs to Project Alpha, Stream 1
-- ('rs_alpha_2'), -- Belongs to Project Alpha, Stream 2
-- ('rs_beta_1');   -- Belongs to Project Beta, Stream 1
--
-- -- If you were to expand research_streams table as suggested:
-- -- INSERT INTO research_streams (id, project_id, subject, focus) VALUES
-- -- ('rs_alpha_1', 'project_alpha', 'AI Ethics', 'Bias in Machine Learning'),
-- -- ('rs_alpha_2', 'project_alpha', 'Quantum Computing', 'Cryptography Applications'),
-- -- ('rs_beta_1', 'project_beta', 'Renewable Energy', 'Solar Panel Efficiency');
--
-- -- Mock data for 'papers' table
-- INSERT INTO papers (id, project_id, stream_id, title, content) VALUES
-- ('paper_001', 'project_alpha', 'rs_alpha_1', 'The Ethical Implications of AI', '# Ethical AI\nContent about AI ethics...'),
-- ('paper_002', 'project_alpha', 'rs_alpha_1', 'Understanding Algorithmic Bias', '# Algorithmic Bias\nDetails on bias in ML...'),
-- ('paper_003', 'project_beta', 'rs_beta_1', 'Advancements in Solar Technology', '# Solar Tech\nRecent solar advancements...');
--
-- -- Mock data for 'chat_messages' table
-- INSERT INTO chat_messages (id, project_id, stream_id, text, sent_by_user, avatar, timestamp) VALUES
-- ('msg_001', 'project_alpha', 'rs_alpha_1', 'Hello! How can I help you with your research today?', FALSE, 'https://robohash.org/ai.png?size=40x40', '2023-10-26 10:00:00'),
-- ('msg_002', 'project_alpha', 'rs_alpha_1', 'Tell me about the key challenges in AI ethics.', TRUE, 'https://robohash.org/user.png?size=40x40', '2023-10-26 10:01:00'),
-- ('msg_003', 'project_alpha', 'rs_alpha_1', 'One key challenge is ensuring fairness and avoiding bias in AI systems, especially when they are used for critical decisions.', FALSE, 'https://robohash.org/ai.png?size=40x40', '2023-10-26 10:02:00');
--
-- -- Mock data for 'prompt_components' table
-- INSERT INTO prompt_components (id, user_id, name, type, content) VALUES
-- ('comp_db_1', 'user123', 'Conciseness Rule', 'rules', 'Provide answers in no more than three sentences.'),
-- ('comp_db_2', 'user123', 'Factual Verification Step', 'reasoning', 'Always cross-reference numerical data with at least two sources.'),
-- ('comp_db_3', 'user456', 'Technical Explanation Style', 'rules', 'Explain concepts as if to a software engineer with 5 years of experience.');
--
-- -- Mock data for 'prompt_library' table
-- INSERT INTO prompt_library (id, user_id, name, type, content) VALUES
-- ('lib_db_1', 'user123', 'Socratic Tutor Persona', 'personas', 'Act as a Socratic tutor. Ask guiding questions to help me understand complex topics.'),
-- ('lib_db_2', 'user123', 'Summarize Action', 'actions', 'Summarize the provided text, highlighting key arguments and conclusions.'),
-- ('lib_db_3', 'user456', 'Code Generation Persona', 'personas', 'You are an expert Python programmer. Generate clean, efficient code based on the requirements.');

-- Mock data for 'projects' table
-- Drop Table if exists projects;
-- Drop Table if exists research_streams;
Drop Table if exists papers;
-- Drop Table if exists chat_messages;
-- Drop Table if exists prompt_components;
-- Drop Table if exists prompt_library;


    -- In /Users/jameslittiebrant/DataspellProjects/PKMResearcher/ui/table_builder.sql
-- Modify the 'papers' table definition:
CREATE TABLE papers (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    stream_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_new INTEGER DEFAULT 0 -- Add this line (0 for false, 1 for true)
    -- Optional: Foreign keys if you have projects and research_streams tables
    -- FOREIGN KEY (project_id) REFERENCES projects(id),
    -- FOREIGN KEY (stream_id) REFERENCES research_streams(id)
    -- Consider an index for faster lookups by project_id and stream_id
);

-- DELETE FROM projects; -- Clear existing mock data if any
INSERT INTO projects (id, name) VALUES
('proj_alpha_01', 'AI Ethics Research'),
('proj_beta_02', 'Quantum Computing Applications'),
('proj_gamma_03', 'Renewable Energy Solutions');

-- Mock data for 'research_streams' table
-- DELETE FROM research_streams; -- Clear existing mock data
-- Ensure these project_id values exist in the 'projects' table
INSERT INTO research_streams (id, project_id, subject, focus) VALUES
('rs_alpha_ethics_001', 'proj_alpha_01', 'Algorithmic Bias', 'Fairness in ML Models'),
('rs_alpha_ethics_002', 'proj_alpha_01', 'AI Governance', 'Policy and Regulation'),
('rs_beta_quantum_001', 'proj_beta_02', 'Quantum Cryptography', 'Secure Communication Protocols'),
('rs_gamma_energy_001', 'proj_gamma_03', 'Solar Panel Tech', 'Efficiency Improvements');

-- Mock data for 'papers' table
-- DELETE FROM papers; -- Clear existing mock data
-- Ensure project_id and stream_id values exist in their respective tables
INSERT INTO papers (id, project_id, stream_id, title, content, is_new) VALUES
('paper_a01_s01_001', 'proj_alpha_01', 'general', 'The Landscape of Algorithmic Bias', '# Understanding Bias\nAn overview of different types of bias in machine learning systems and their societal impact.', 1),
('paper_a01_s01_002', 'proj_alpha_01', 'general', 'Mitigation Strategies for ML Bias', '# Addressing Fairness\nTechniques and best practices for reducing bias in AI models during development and deployment.', 1),
('paper_b02_s01_001', 'proj_beta_02', 'general', 'Post-Quantum Cryptography Challenges', '# Quantum Threats\nExploring the vulnerabilities of current cryptographic systems to quantum computers and the need for new standards.', 1),
('paper_g03_s01_001', 'proj_gamma_03', 'general', 'Next-Generation Solar Cell Materials', '# Solar Innovation\nReview of emerging materials like perovskites and their potential to revolutionize solar panel efficiency and cost.', 1);

UPDATE papers
                       SET is_new = 1
                       WHERE project_id = 'proj_alpha_01' AND stream_id = 'general';


INSERT INTO papers (id, project_id, stream_id, title, content, is_new) VALUES
('paper_a01_s01_001', 'proj_alpha_01', 'general', 'The Landscape of Algorithmic Bias', '# Understanding Bias\nAn overview of different types of bias in machine learning systems and their societal impact.', 1),
('paper_a01_s01_0023', 'proj_alpha_01', 'general', 'Mitigation Strategies for ML Bias', '# Addressing Fairness\nTechniques and best practices for reducing bias in AI models during development and deployment.', 1);


-- Mock data for 'chat_messages' table
-- DELETE FROM chat_messages; -- Clear existing mock data
-- Ensure project_id and stream_id values exist
INSERT INTO chat_messages (id, project_id, stream_id, text, sent_by_user, avatar, timestamp) VALUES
('msg_a01_s01_001', 'proj_alpha_01', 'rs_alpha_ethics_001', 'Hello! How can I assist with your research on algorithmic bias today?', FALSE, 'https://robohash.org/ai_ethics_bot.png?size=40x40', '2023-11-01 10:00:00'),
('msg_a01_s01_002', 'proj_alpha_01', 'rs_alpha_ethics_001', 'Can you summarize the main types of bias discussed in "The Landscape of Algorithmic Bias" paper?', TRUE, 'https://robohash.org/user_researcher1.png?size=40x40', '2023-11-01 10:05:00'),
('msg_a01_s01_003', 'proj_alpha_01', 'rs_alpha_ethics_001', 'Certainly. The paper highlights selection bias, measurement bias, and algorithmic bias itself, stemming from skewed data or flawed model assumptions.', FALSE, 'https://robohash.org/ai_ethics_bot.png?size=40x40', '2023-11-01 10:07:00'),
('msg_b02_s01_001', 'proj_beta_02', 'rs_beta_quantum_001', 'What are the primary concerns regarding quantum computers and current encryption methods?', TRUE, 'https://robohash.org/user_researcher2.png?size=40x40', '2023-11-02 14:30:00');

-- Mock data for 'prompt_components' table
-- DELETE FROM prompt_components; -- Clear existing mock data
INSERT INTO prompt_components (id, user_id, name, type, content, created_at, updated_at) VALUES
('comp_user123_concise_01', 'user123', 'Brevity Mandate', 'rules', 'Responses should be a maximum of three sentences unless more detail is explicitly requested.', '2023-10-01 09:00:00', '2023-10-05 11:00:00'),
('comp_user123_verify_02', 'user123', 'Data Cross-Reference', 'reasoning', 'All statistical data or numerical claims must be verifiable against at least two independent sources mentioned in the provided documents.', '2023-10-02 14:00:00', '2023-10-02 14:00:00'),
('comp_user456_tech_style_01', 'user456', 'Engineer-Level Explanation', 'rules', 'Explain complex technical concepts as if addressing a software engineer with 5-7 years of experience. Avoid oversimplification.', '2023-10-03 16:30:00', '2023-10-03 16:30:00');

-- Mock data for 'prompt_library' table
-- DELETE FROM prompt_library; -- Clear existing mock data
INSERT INTO prompt_library (id, user_id, name, type, content, created_at, updated_at) VALUES
('lib_user123_socratic_01', 'user123', 'Socratic Inquiry Persona', 'personas', 'Adopt the role of a Socratic tutor. Guide the user to deeper understanding by asking probing questions rather than providing direct answers.', '2023-10-10 10:00:00', '2023-10-11 10:00:00'),
('lib_user123_summarize_02', 'user123', 'Executive Summary Action', 'actions', 'Generate a concise executive summary of the provided text, focusing on key findings, conclusions, and actionable insights.', '2023-10-11 15:00:00', '2023-10-11 15:00:00'),
('lib_user456_python_expert_01', 'user456', 'Python Code Architect Persona', 'personas', 'You are an expert Python developer specializing in scalable and maintainable code. Generate Python code that adheres to PEP 8 and includes clear docstrings.', '2023-10-12 11:20:00', '2023-10-12 11:20:00');

-- SQL to create the dynamic_actions table
CREATE TABLE IF NOT EXISTS dynamic_actions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    ui_group TEXT NOT NULL CHECK(ui_group IN ('document_actions', 'guided_personas', 'guided_tangents')),
    action_type TEXT NOT NULL CHECK(action_type IN ('process_documents', 'set_chat_persona', 'inject_chat_prompt')),
    output_destination TEXT NOT NULL CHECK(output_destination IN ('new_document', 'chat_message')),
    prompt_template TEXT,
    is_user_defined INTEGER NOT NULL DEFAULT 0, -- 0 for built-in, 1 for user-defined
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Optional: Trigger to update 'updated_at' on modification
CREATE TRIGGER IF NOT EXISTS update_dynamic_actions_updated_at
AFTER UPDATE ON dynamic_actions
FOR EACH ROW
BEGIN
    UPDATE dynamic_actions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- SQL to insert mock data (run once, or use ON CONFLICT)
INSERT INTO dynamic_actions (id, name, description, ui_group, action_type, output_destination, prompt_template, is_user_defined) VALUES
('action_summarize_doc', 'Summarize Selected', 'Generates a summary of the selected documents.', 'document_actions', 'process_documents', 'new_document', 'Please summarize the key findings from the following documents:\n{selected_doc_titles_list}', 0),
('action_keywords_doc', 'Extract Keywords', 'Extracts relevant keywords from the selected documents.', 'document_actions', 'process_documents', 'new_document', 'Identify and list the main keywords from these documents:\n{selected_doc_titles_list}', 0),
('action_report_snippet_doc', 'Generate Report Snippet', 'Creates a report snippet based on selected documents.', 'document_actions', 'process_documents', 'new_document', 'Draft a concise report snippet incorporating insights from:\n{selected_doc_titles_list}', 0),
('action_summarize_chat', 'Summarize to Chat', 'Generates a summary of selected documents and posts to chat.', 'document_actions', 'process_documents', 'chat_message', 'Summarize the key points of: {selected_doc_titles_list}', 0),

('persona_economist', 'Economist', 'Adopt an economist persona for the chat.', 'guided_personas', 'set_chat_persona', 'chat_message', 'From an economist''s perspective, considering factors like supply, demand, and market impact, how would you analyze this?', 0),
('persona_scientist', 'Scientist', 'Adopt a scientist persona for the chat.', 'guided_personas', 'set_chat_persona', 'chat_message', 'Approaching this as a scientist, focusing on empirical evidence and methodology, what are your thoughts?', 0),
('persona_historian', 'Historian', 'Adopt a historian persona for the chat.', 'guided_personas', 'set_chat_persona', 'chat_message', 'As a historian, considering the historical context and precedents, how do you interpret this situation?', 0),

('tangent_devils_advocate', 'Devil''s Advocate', 'Play devil''s advocate on the current topic.', 'guided_tangents', 'inject_chat_prompt', 'chat_message', 'Let''s play devil''s advocate. What are the strongest counter-arguments or alternative explanations?', 0),
('tangent_assumptions', 'Assumptions?', 'Question the underlying assumptions.', 'guided_tangents', 'inject_chat_prompt', 'chat_message', 'What are the core assumptions being made here, and how valid are they?', 0),
('tangent_alternatives', 'Alternatives?', 'Explore alternative solutions or perspectives.', 'guided_tangents', 'inject_chat_prompt', 'chat_message', 'Are there any alternative approaches, solutions, or perspectives we haven''t considered?', 0)
ON CONFLICT(id) DO NOTHING;



