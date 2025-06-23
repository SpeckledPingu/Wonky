-- schema.sql
-- This script defines the database schema for the Research Workspace application.

-- Drop tables in reverse order of dependency to avoid foreign key constraint errors.
DROP TABLE IF EXISTS document_links;
DROP TABLE IF EXISTS document_key_players;
DROP TABLE IF EXISTS document_subjects;
DROP TABLE IF EXISTS key_players;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS research_streams;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS personas;
DROP TABLE IF EXISTS tangents;
DROP TABLE IF EXISTS user_actions;

-- Core tables for projects, streams, and documents
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    goal TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    created_at TEXT NOT NULL -- Storing as ISO 8601 datetime string (e.g., '2024-07-15T10:30:00Z')
);

CREATE TABLE research_streams (
    id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    focus TEXT NOT NULL,
    analysis_type TEXT NOT NULL,
    project_id TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    publication_date TEXT, -- Storing as ISO 8601 date string (e.g., '2024-07-15')
    content TEXT NOT NULL,
    is_hidden BOOLEAN NOT NULL DEFAULT 0,
    parent_id TEXT,
    stream_id TEXT NOT NULL,
    FOREIGN KEY (stream_id) REFERENCES research_streams(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES documents(id) ON DELETE SET NULL
);

-- Many-to-many relationship for linking documents to each other
CREATE TABLE document_links (
    source_document_id TEXT NOT NULL,
    target_document_id TEXT NOT NULL,
    PRIMARY KEY (source_document_id, target_document_id),
    FOREIGN KEY (source_document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (target_document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Lookup tables for subjects/key_players and their join tables
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE document_subjects (
    document_id TEXT NOT NULL,
    subject_id INTEGER NOT NULL,
    PRIMARY KEY (document_id, subject_id),
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

CREATE TABLE key_players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE document_key_players (
    document_id TEXT NOT NULL,
    key_player_id INTEGER NOT NULL,
    PRIMARY KEY (document_id, key_player_id),
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (key_player_id) REFERENCES key_players(id) ON DELETE CASCADE
);

-- Static configuration tables
CREATE TABLE personas (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    icon TEXT NOT NULL,
    prompt_start TEXT NOT NULL
);

CREATE TABLE tangents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    icon TEXT NOT NULL,
    prompt_start TEXT NOT NULL
);

CREATE TABLE user_actions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    prompt_content TEXT NOT NULL
);