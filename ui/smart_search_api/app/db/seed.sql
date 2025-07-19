-- =================================================================
--  SEED SCRIPT for Research Analytics Platform (v3.1 - Expanded Data)
-- =================================================================

-- Clean slate
DELETE FROM users;
DELETE FROM projects;
DELETE FROM documents;
DELETE FROM tags;
DELETE FROM document_tags;
DELETE FROM extractions;
DELETE FROM reports;
DELETE FROM report_sources;
DELETE FROM processing_bucket_items;

-- -----------------------------------------------------
-- Seed `users`
-- -----------------------------------------------------
INSERT INTO users (id, username, email) VALUES 
(1, 'testuser', 'test@example.com'),
(2, 'anotheruser', 'another@example.com');

-- -----------------------------------------------------
-- Seed `projects`
-- -----------------------------------------------------
INSERT INTO projects (id, user_id, name) VALUES
(101, 1, 'AI Research Project'),
(102, 1, 'Climate Policy Analysis'),
(201, 2, 'Quantum Mechanics Study'),
(202, 2, 'Healthcare Data Initiative');

-- -----------------------------------------------------
-- Seed `documents`
-- -----------------------------------------------------
-- Project 101 (User 1)
INSERT INTO documents (id, project_id, title, content, color) VALUES
('doc-001', 101, 'The Impact of AI on Scientific Research', '# AI Research...', 'blue'),
('doc-006', 101, 'Machine Learning for Financial Data Analysis', '# Machine Learning for Finance...', 'default'),
('doc-009', 101, 'Genomic Data Sequencing and Analysis', '# Genomic Data...', 'purple');

-- Project 102 (User 1)
INSERT INTO documents (id, project_id, title, content, color) VALUES
('doc-002', 102, 'Climate Change Policies: A Global Overview', '# Climate Policies...', 'green'),
('doc-007', 102, 'Renewable Energy Data Report', '# Renewable Energy...', 'green'),
('doc-008', 102, 'The Ethics of Data Collection', '# Data Ethics...', 'blue');

-- Project 201 (User 2)
INSERT INTO documents (id, project_id, title, content, color) VALUES
('doc-003', 201, 'Advances in Quantum Computing', '# Quantum Computing...', 'purple'),
('doc-201', 201, 'A Study on Quantum Entanglement', '# Quantum Entanglement...', 'blue');

-- Project 202 (User 2)
INSERT INTO documents (id, project_id, title, content, color) VALUES
('doc-004', 202, 'Big Data Analytics in Healthcare', '# Healthcare Data...', 'red'),
('doc-010', 202, 'Urban Planning with Geospatial Data', '# Urban Planning...', 'red');


-- -----------------------------------------------------
-- Seed `tags` and `document_tags`
-- -----------------------------------------------------
INSERT INTO tags (id, name) VALUES (1, 'AI'), (2, 'Research'), (3, 'Technology'), (4, 'Climate'), (5, 'Policy'), (6, 'Environment'), (7, 'Quantum'), (8, 'Computing'), (9, 'Physics'), (10, 'Data'), (11, 'Healthcare'), (12, 'Finance');

INSERT INTO document_tags (document_id, tag_id) VALUES
('doc-001', 1), ('doc-001', 2), ('doc-001', 10),
('doc-002', 4), ('doc-002', 5), ('doc-002', 6),
('doc-003', 7), ('doc-003', 8), ('doc-003', 9),
('doc-004', 10), ('doc-004', 11),
('doc-006', 1), ('doc-006', 10), ('doc-006', 12),
('doc-201', 7), ('doc-201', 9);


-- -----------------------------------------------------
-- Seed `extractions`
-- -----------------------------------------------------
INSERT INTO extractions (id, project_id, source_doc_id, type, stance, content) VALUES
('ext-001', 101, 'doc-001', 'insight', 'pro', 'AI-driven data analysis is the most significant factor in accelerating genomic research.'),
('ext-002', 102, 'doc-002', 'policy', 'pro', 'A global carbon tax is proposed as the most effective policy for reducing emissions.'),
('ext-003', 102, 'doc-002', 'insight', 'con', 'National interests frequently undermine international cooperation on climate agreements.'),
('ext-004', 201, 'doc-003', 'case_study', 'pro', 'Case Study: A 53-qubit quantum processor successfully demonstrated supremacy over classical supercomputers.'),
('ext-005', 202, 'doc-004', 'policy', 'con', 'Current data collection policies are inadequate to protect user privacy.');


-- -----------------------------------------------------
-- Seed `reports` and `report_sources`
-- -----------------------------------------------------
INSERT INTO reports (id, project_id, title, content, analysis_type, generated_at) VALUES
('report-proj1-01', 101, 'Key AI Research Themes', '## AI Research Report...', 'extract_themes', '2025-07-19 08:00:00'),
('report-proj2-01', 102, 'Summary of Climate Policies', '## Climate Summary...', 'summarize', '2025-07-19 11:00:00'),
('report-proj201-01', 201, 'Quantum Entanglement Analysis', '## Quantum Report...', 'summarize', '2025-07-20 09:00:00');

INSERT INTO report_sources (report_id, document_id) VALUES
('report-proj1-01', 'doc-001'),
('report-proj2-01', 'doc-002'),
('report-proj201-01', 'doc-201');


-- -----------------------------------------------------
-- Seed `processing_bucket_items`
-- -----------------------------------------------------
INSERT INTO processing_bucket_items (project_id, document_id) VALUES 
(101, 'doc-001'),
(102, 'doc-008'),
(202, 'doc-010');

