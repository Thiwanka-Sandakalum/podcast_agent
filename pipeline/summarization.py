import sqlite3
from podcast_agent.podcast_db import get_db_path
from podcast_agent.llm_utils import gemini_summarize

def get_chunks(book_id):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("SELECT id, chunk_text FROM chunks WHERE book_id = ? ORDER BY chunk_index", (book_id,))
    rows = c.fetchall()
    conn.close()
    return rows  # List of (chunk_id, chunk_text)

def save_summary(chunk_id, summary_text):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute(
        "INSERT INTO summaries (chunk_id, summary_text) VALUES (?, ?)",
        (chunk_id, summary_text)
    )
    conn.commit()
    conn.close()

def summarize_chunks(book_id, summarize_func):
    import concurrent.futures
    chunks = get_chunks(book_id)

    def summarize_and_save(args):
        chunk_id, chunk_text = args
        summary = summarize_func(chunk_text)
        save_summary(chunk_id, summary)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        list(executor.map(summarize_and_save, chunks))
    return len(chunks)

if __name__ == "__main__":
    # Example usage
    book_id = 1  # Replace with actual book ID
    n = summarize_chunks(book_id, gemini_summarize)
    print(f"Summarized {n} chunks for book {book_id}.")
