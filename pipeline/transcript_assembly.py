import sqlite3
from podcast_agent.podcast_db import get_db_path
from datetime import datetime

def get_section_scripts(plan_id):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('''
        SELECT section_scripts.script_text
        FROM section_scripts
        JOIN plan_sections ON section_scripts.section_id = plan_sections.id
        WHERE plan_sections.plan_id = ?
        ORDER BY plan_sections.section_index
    ''', (plan_id,))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def save_transcript(book_id, transcript_text):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute(
        "INSERT INTO transcripts (book_id, transcript_text, created_at) VALUES (?, ?, ?)",
        (book_id, transcript_text, datetime.now())
    )
    transcript_id = c.lastrowid
    conn.commit()
    conn.close()
    return transcript_id

def assemble_and_export_transcript(book_id, plan_id, output_path=None):
    scripts = get_section_scripts(plan_id)
    transcript = "\n\n".join(s for s in scripts if s)
    transcript_id = save_transcript(book_id, transcript)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcript)
    return transcript_id, transcript

if __name__ == "__main__":
    # Example usage
    book_id = 1  # Replace with actual book ID
    plan_id = 1  # Replace with actual plan ID
    transcript_id, transcript = assemble_and_export_transcript(book_id, plan_id, "final_transcript.txt")
    print(f"Transcript {transcript_id} saved and exported.")
