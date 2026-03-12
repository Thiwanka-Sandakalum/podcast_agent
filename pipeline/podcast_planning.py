import sqlite3
import logging
from podcast_agent.podcast_db import get_db_path
from podcast_agent.llm_utils import gemini_plan
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def get_summaries(book_id):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('''
        SELECT summaries.id, summaries.summary_text
        FROM summaries
        JOIN chunks ON summaries.chunk_id = chunks.id
        WHERE chunks.book_id = ?
        ORDER BY chunks.chunk_index
    ''', (book_id,))
    rows = c.fetchall()
    conn.close()
    logging.info(f"Fetched {len(rows)} summaries for book_id={book_id}")
    return rows  # List of (summary_id, summary_text)

def save_podcast_plan(book_id, sections):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("INSERT INTO podcast_plans (book_id) VALUES (?)", (book_id,))
    plan_id = c.lastrowid
    for idx, section in enumerate(sections):
        c.execute(
            "INSERT INTO plan_sections (plan_id, section_index, title, description) VALUES (?, ?, ?, ?)",
            (plan_id, idx, section['title'], section['description'])
        )
    conn.commit()
    conn.close()
    logging.info(f"Saved podcast plan {plan_id} with {len(sections)} sections for book_id={book_id}")
    return plan_id

def plan_podcast_from_summaries(book_id, plan_func):
    import json
    import re
    summaries = [s for _, s in get_summaries(book_id)]
    logging.info(f"Calling plan_func (LLM) with {len(summaries)} summaries")
    sections = plan_func(summaries)
    # Robustly handle string output from LLM
    if isinstance(sections, str):
        # Remove code fences if present (robust)
        cleaned = sections.strip()
        if cleaned.startswith('```'):
            # Remove opening code fence and optional language
            cleaned = cleaned.split('\n', 1)[-1] if '\n' in cleaned else cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned.rsplit('```', 1)[0]
        cleaned = cleaned.strip()
        try:
            sections = json.loads(cleaned)
            logging.info("Parsed LLM output as JSON successfully after removing code fences.")
        except Exception:
            logging.error(f"LLM did not return valid JSON for podcast plan: {sections}")
            raise ValueError(f"LLM did not return valid JSON for podcast plan: {sections}")
    if not (isinstance(sections, list) and all(isinstance(s, dict) and 'title' in s and 'description' in s for s in sections)):
        logging.error(f"Podcast plan sections are not in expected format: {sections}")
        raise ValueError(f"Podcast plan sections are not in expected format: {sections}")
    plan_id = save_podcast_plan(book_id, sections)
    return plan_id, len(sections)

if __name__ == "__main__":
    # Example usage
    book_id = 1  # Replace with actual book ID
    plan_id, n = plan_podcast_from_summaries(book_id, gemini_plan)
    print(f"Podcast plan {plan_id} created with {n} sections.")
