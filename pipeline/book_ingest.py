from podcast_agent.podcast_db import init_db, get_db_path
import sqlite3
from datetime import datetime

def insert_book(raw_text, title=None, author=None):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO books (title, author, raw_text, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            title or "Untitled Book",
            author or "Unknown Author",
            raw_text,
            datetime.now(),
        ),
    )
    book_id = c.lastrowid
    conn.commit()
    conn.close()
    return book_id

if __name__ == "__main__":
    init_db()
    # Example usage
    with open("../my_book.txt", "r", encoding="utf-8") as f:
        text = f.read()
    book_id = insert_book(text, title="My Book Example")
    print(f"Book inserted with ID: {book_id}")
