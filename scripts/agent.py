from dotenv import load_dotenv
from podcast_agent.db.podcast_db import init_db
from podcast_agent.llm.llm_utils import gemini_plan, gemini_script, gemini_summarize
from podcast_agent.pipeline.book_ingest import insert_book
from podcast_agent.pipeline.chunking import chunk_book
from podcast_agent.pipeline.podcast_planning import plan_podcast_from_summaries
from podcast_agent.pipeline.section_scripts import generate_scripts_for_plan
from podcast_agent.pipeline.summarization import summarize_chunks
from podcast_agent.pipeline.transcript_assembly import assemble_and_export_transcript
load_dotenv()

def main(input=None, output="podcast_transcript.txt", title=None, author=None):
	"""
	Run the book-to-podcast pipeline. Arguments can be passed directly or via argparse in main.py.
	"""
	if input is None:
		raise ValueError("Input file path must be provided.")
	init_db()
	with open(input, "r", encoding="utf-8") as f:
		book_text = f.read()
	book_id = insert_book(book_text, title=title, author=author)
	print(f"Book inserted with ID: {book_id}")

	num_chunks = chunk_book(book_id)
	print(f"Book split into {num_chunks} chunks.")

	summarize_chunks(book_id, gemini_summarize)
	print("Chunks summarized.")

	plan_id, n_sections = plan_podcast_from_summaries(book_id, gemini_plan)
	print(f"Podcast plan created with {n_sections} sections.")

	generate_scripts_for_plan(plan_id, gemini_script)
	print("Section scripts generated.")

	transcript_id, transcript = assemble_and_export_transcript(book_id, plan_id, output)
	print(f"Transcript saved to {output} (DB id: {transcript_id})")
