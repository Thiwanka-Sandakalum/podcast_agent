import sqlite3
from podcast_agent.podcast_db import get_db_path
from podcast_agent.llm_utils import gemini_script

def get_plan_sections(plan_id):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('''
        SELECT id, title, description
        FROM plan_sections
        WHERE plan_id = ?
        ORDER BY section_index
    ''', (plan_id,))
    rows = c.fetchall()
    conn.close()
    return rows  # List of (section_id, title, description)

def save_section_script(section_id, script_text):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute(
        "INSERT INTO section_scripts (section_id, script_text) VALUES (?, ?)",
        (section_id, script_text)
    )
    conn.commit()
    conn.close()

def generate_scripts_for_plan(plan_id, script_func):
    import concurrent.futures
    sections = get_plan_sections(plan_id)

    def script_and_save(args):
        section_id, title, description = args
        script = script_func(title, description)
        save_section_script(section_id, script)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        list(executor.map(script_and_save, sections))
    return len(sections)

if __name__ == "__main__":
    # Example usage
    plan_id = 1  # Replace with actual plan ID
    n = generate_scripts_for_plan(plan_id, gemini_script)
    print(f"Generated {n} section scripts for plan {plan_id}.")
