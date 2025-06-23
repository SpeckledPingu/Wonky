# seed.py
import sqlite3
import uuid
from datetime import datetime, timedelta
from faker import Faker
import random
import os

# --- Configuration ---
DB_FILE = "research_workspace.db"
SCHEMA_FILE = "schema.sql"
NUM_PROJECTS = 10
MAX_STREAMS_PER_PROJECT = 5
MAX_DOCS_PER_STREAM = 20

# Initialize Faker for generating dummy data
fake = Faker()


# --- Helper Functions ---
def generate_id(prefix):
    """Generates a unique ID with a given prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")  # Enforce foreign key constraints
    return conn


# --- Data Population Functions ---

def create_schema(conn):
    """Creates database schema from the .sql file."""
    print("Creating database schema...")
    with open(SCHEMA_FILE, 'r') as f:
        conn.executescript(f.read())
    print("Schema created successfully.")


def create_static_data(conn):
    """Populates the database with static configuration data (personas, etc.)."""
    print("Populating static data (personas, tangents, user actions)...")
    cursor = conn.cursor()
    
    personas = [
        ('analyst', 'Policy Analyst', 'UserCog', "As a seasoned policy analyst, let's examine this."),
        ('legal', 'Legal Expert', 'Scale', "From a legal perspective, considering relevant case law and statutes..."),
        ('economist', 'Economist', 'Brain', "Analyzing the economic implications, including costs and benefits...")
    ]
    cursor.executemany("INSERT INTO personas (id, name, icon, prompt_start) VALUES (?, ?, ?, ?)", personas)
    
    tangents = [
        ('explore', 'Explore Ideas', 'Lightbulb', "Let's brainstorm some innovative ideas related to this topic."),
        ('counterfactuals', 'Identify Counterfactuals', 'Shuffle',
         "What if the key assumptions were different? Let's explore..."),
        ('devilsAdvocate', "Devil's Advocate", 'EyeOff',
         "Playing devil's advocate, what are the strongest arguments against this?")
    ]
    cursor.executemany("INSERT INTO tangents (id, name, icon, prompt_start) VALUES (?, ?, ?, ?)", tangents)
    
    user_actions = [
        ('userAction1', 'Analyze Fiscal Impact (Custom)', 'System: You are an economist... Analysis: ...'),
        ('userAction2', 'Identify Public Sentiment Trends', 'System: You are a social media analyst... Analysis: ...')
    ]
    cursor.executemany("INSERT INTO user_actions (id, name, prompt_content) VALUES (?, ?, ?)", user_actions)
    
    conn.commit()
    print("Static data populated.")


def create_dynamic_data(conn):
    """Generates and inserts a large amount of dynamic mock data."""
    print("Generating and populating dynamic data (projects, streams, documents)...")
    cursor = conn.cursor()
    
    # Generate reusable subjects and key players
    subjects = list({fake.bs().title() for _ in range(50)})
    key_players = list({fake.name() for _ in range(50)})
    cursor.executemany("INSERT INTO subjects (name) VALUES (?)", [(s,) for s in subjects])
    cursor.executemany("INSERT INTO key_players (name) VALUES (?)", [(p,) for p in key_players])
    subject_ids = [row[0] for row in cursor.execute("SELECT id FROM subjects").fetchall()]
    key_player_ids = [row[0] for row in cursor.execute("SELECT id FROM key_players").fetchall()]
    
    all_doc_ids = []
    
    for i in range(NUM_PROJECTS):
        project_id = generate_id("proj")
        project_data = (
            project_id,
            f"{fake.catch_phrase()}: A Study",
            fake.bs(),
            fake.paragraph(nb_sentences=3),
            random.choice(['FilePlus', 'Network', 'BarChart3', 'FileHeart', 'FileText']),
            fake.date_time_this_year().isoformat()
        )
        cursor.execute("INSERT INTO projects (id, name, goal, description, icon, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                       project_data)
        
        num_streams = random.randint(0, MAX_STREAMS_PER_PROJECT)
        for j in range(num_streams):
            stream_id = generate_id("rs")
            stream_data = (
                stream_id,
                fake.bs().title(),
                fake.sentence(nb_words=4),
                random.choice(['Legal Review', 'Historical Analysis', 'Impact Analysis', 'Data Synthesis']),
                project_id
            )
            cursor.execute(
                "INSERT INTO research_streams (id, subject, focus, analysis_type, project_id) VALUES (?, ?, ?, ?, ?)",
                stream_data)
            
            project_doc_ids = []
            num_docs = random.randint(1, MAX_DOCS_PER_STREAM)
            for k in range(num_docs):
                doc_id = generate_id("doc")
                parent_id = random.choice(project_doc_ids) if project_doc_ids and random.random() > 0.7 else None
                doc_data = (
                    doc_id,
                    f"{fake.sentence(nb_words=5).replace('.', '')}.{random.choice(['pdf', 'docx', 'txt'])}",
                    random.choice(['pdf', 'docx', 'txt', 'html', 'xlsx']),
                    fake.date_this_decade().isoformat(),
                    '\n\n'.join(fake.paragraphs(nb=5)),
                    random.choice([0, 1]),
                    parent_id,
                    stream_id
                )
                cursor.execute(
                    "INSERT INTO documents (id, name, type, publication_date, content, is_hidden, parent_id, stream_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    doc_data)
                project_doc_ids.append(doc_id)
                all_doc_ids.append(doc_id)
                
                # Add subjects and key players to the document
                for _ in range(random.randint(1, 4)):
                    cursor.execute("INSERT OR IGNORE INTO document_subjects (document_id, subject_id) VALUES (?, ?)",
                                   (doc_id, random.choice(subject_ids)))
                for _ in range(random.randint(0, 3)):
                    cursor.execute(
                        "INSERT OR IGNORE INTO document_key_players (document_id, key_player_id) VALUES (?, ?)",
                        (doc_id, random.choice(key_player_ids)))
    
    # Add some document links
    for _ in range(len(all_doc_ids) // 2):
        source, target = random.sample(all_doc_ids, 2)
        cursor.execute("INSERT OR IGNORE INTO document_links (source_document_id, target_document_id) VALUES (?, ?)",
                       (source, target))
    
    conn.commit()
    print(f"Dynamic data populated: {NUM_PROJECTS} projects created.")


# --- Main Execution ---
def main():
    """Main function to set up and seed the database."""
    if os.path.exists(DB_FILE):
        print(f"Database file '{DB_FILE}' already exists. Deleting it to start fresh.")
        os.remove(DB_FILE)
    
    conn = get_db_connection()
    try:
        create_schema(conn)
        create_static_data(conn)
        create_dynamic_data(conn)
        print("\nDatabase setup and seeding complete!")
        print(f"Database file created: '{DB_FILE}'")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()