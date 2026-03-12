import sqlite3
from pathlib import Path

def get_db_path():
    return str(Path(__file__).parent / "podcast_pipeline.db")

def init_db():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    # Books table
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            raw_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Chunks table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            chunk_index INTEGER,
            chunk_text TEXT NOT NULL,
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
    ''')
    # Summaries table
    c.execute('''
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chunk_id INTEGER,
            summary_text TEXT NOT NULL,
            FOREIGN KEY(chunk_id) REFERENCES chunks(id)
        )
    ''')
    # Podcast plans table
    c.execute('''
        CREATE TABLE IF NOT EXISTS podcast_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
    ''')
    # Plan sections table
    c.execute('''
        CREATE TABLE IF NOT EXISTS plan_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER,
            section_index INTEGER,
            title TEXT,
            description TEXT,
            FOREIGN KEY(plan_id) REFERENCES podcast_plans(id)
        )
    ''')
    # Section scripts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS section_scripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER,
            script_text TEXT,
            FOREIGN KEY(section_id) REFERENCES plan_sections(id)
        )
    ''')
    # Transcripts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            transcript_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
