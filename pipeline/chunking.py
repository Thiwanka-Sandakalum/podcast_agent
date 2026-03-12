import sqlite3
import re
from podcast_agent.podcast_db import get_db_path

def get_book_text(book_id):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("SELECT raw_text FROM books WHERE id = ?", (book_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def save_chunks(book_id, chunks):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    for idx, chunk in enumerate(chunks):
        c.execute(
            "INSERT INTO chunks (book_id, chunk_index, chunk_text) VALUES (?, ?, ?)",
            (book_id, idx, chunk)
        )
    conn.commit()
    conn.close()

def chunk_book(book_id):
    text = get_book_text(book_id)
    if not text:
        raise ValueError(f"No book found with id {book_id}")
    # Try to split by 'Chapter' headings first
    chapters = re.split(r"(?i)\\bchapter\\b[\\s\\d:.-]*", text)
    chapters = [c.strip() for c in chapters if c.strip()]
    if len(chapters) > 1:
        chunks = chapters
    else:
        # Fallback: split every ~5000 words
        words = text.split()
        chunks = [" ".join(words[i:i+5000]) for i in range(0, len(words), 5000)]
    save_chunks(book_id, chunks)
    return len(chunks)

if __name__ == "__main__":
    # Example usage
    book_id = 1  # Replace with actual book ID
    num_chunks = chunk_book(book_id)
    print(f"Book {book_id} split into {num_chunks} chunks.")
