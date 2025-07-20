-- =================================================================
--  SCHEMA SCRIPT for Research Analytics Platform (v3.4 - With Saved Results)
-- =================================================================

-- Drop tables in reverse order of creation to respect foreign key constraints
DROP TABLE IF EXISTS saved_search_results;
DROP TABLE IF EXISTS processing_bucket_items;
DROP TABLE IF EXISTS report_sources;
DROP TABLE IF EXISTS document_tags;
DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS extractions;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;

-- -----------------------------------------------------
-- Table `users`
-- -----------------------------------------------------
CREATE TABLE users (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  email TEXT NOT NULL,
  hashed_password TEXT NOT NULL,
  created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
  UNIQUE (username),
  UNIQUE (email)
);
CREATE INDEX ix_users_id ON users (id);
CREATE INDEX ix_users_username ON users (username);
CREATE INDEX ix_users_email ON users (email);

-- -----------------------------------------------------
-- Table `projects`
-- -----------------------------------------------------
CREATE TABLE projects (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  user_id INTEGER NOT NULL,
  created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
  FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_projects_id ON projects (id);

-- -----------------------------------------------------
-- Table `documents`
-- -----------------------------------------------------
CREATE TABLE documents (
  id TEXT NOT NULL PRIMARY KEY,
  project_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  content TEXT,
  summary TEXT, -- <-- ADDED
  color TEXT DEFAULT 'default',
  created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
  updated_at DATETIME,
  FOREIGN KEY(project_id) REFERENCES projects (id)
);
CREATE INDEX ix_documents_id ON documents (id);

-- -----------------------------------------------------
-- Table `tags`
-- -----------------------------------------------------
CREATE TABLE tags (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  UNIQUE (name)
);
CREATE INDEX ix_tags_id ON tags (id);

-- -----------------------------------------------------
-- Table `extractions`
-- -----------------------------------------------------
CREATE TABLE extractions (
  id TEXT NOT NULL PRIMARY KEY,
  project_id INTEGER NOT NULL,
  source_doc_id TEXT NOT NULL,
  type TEXT NOT NULL,
  stance TEXT NOT NULL,
  content TEXT,
  FOREIGN KEY(project_id) REFERENCES projects (id),
  FOREIGN KEY(source_doc_id) REFERENCES documents (id)
);
CREATE INDEX ix_extractions_id ON extractions (id);

-- -----------------------------------------------------
-- Table `reports`
-- -----------------------------------------------------
CREATE TABLE reports (
  id TEXT NOT NULL PRIMARY KEY,
  project_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  content TEXT,
  analysis_type TEXT,
  generated_at DATETIME NOT NULL,
  FOREIGN KEY(project_id) REFERENCES projects (id)
);
CREATE INDEX ix_reports_id ON reports (id);

-- -----------------------------------------------------
-- Table `document_tags` (Join Table)
-- -----------------------------------------------------
CREATE TABLE document_tags (
  document_id TEXT NOT NULL,
  tag_id INTEGER NOT NULL,
  PRIMARY KEY (document_id, tag_id),
  FOREIGN KEY(document_id) REFERENCES documents (id),
  FOREIGN KEY(tag_id) REFERENCES tags (id)
);

-- -----------------------------------------------------
-- Table `report_sources` (Join Table)
-- -----------------------------------------------------
CREATE TABLE report_sources (
  report_id TEXT NOT NULL,
  document_id TEXT NOT NULL,
  PRIMARY KEY (report_id, document_id),
  FOREIGN KEY(report_id) REFERENCES reports (id),
  FOREIGN KEY(document_id) REFERENCES documents (id)
);

-- -----------------------------------------------------
-- Table `processing_bucket_items`
-- -----------------------------------------------------
CREATE TABLE processing_bucket_items (
  project_id INTEGER NOT NULL,
  document_id TEXT NOT NULL,
  added_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
  PRIMARY KEY (project_id, document_id),
  FOREIGN KEY(project_id) REFERENCES projects (id),
  FOREIGN KEY(document_id) REFERENCES documents (id)
);

-- -----------------------------------------------------
-- Table `saved_search_results` (New Table)
-- -----------------------------------------------------
CREATE TABLE saved_search_results (
  project_id INTEGER NOT NULL,
  document_id TEXT NOT NULL,
  saved_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
  PRIMARY KEY (project_id, document_id),
  FOREIGN KEY(project_id) REFERENCES projects (id),
  FOREIGN KEY(document_id) REFERENCES documents (id)
);
