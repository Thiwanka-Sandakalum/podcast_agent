# Book-to-Podcast Pipeline

A modular, LLM-powered pipeline that transforms a book into a podcast transcript and audio, with persistent storage and parallelized processing.

## Features
- **Book Ingestion:** Import book text and store in SQLite database.
- **Chunking:** Split book into manageable sections.
- **Summarization:** Summarize each chunk using Gemini LLM (parallelized).
- **Podcast Planning:** Generate a podcast episode plan (sections/titles/descriptions) with LLM.
- **Script Generation:** Create dialogue scripts for each section (parallelized).
- **Transcript Assembly:** Combine scripts into a full podcast transcript.
- **Text-to-Speech:** Convert transcript to multi-speaker audio using Gemini TTS.
- **Robust Logging:** All LLM and pipeline steps are logged for traceability.
- **Strict Prompting:** Prompts are engineered for reliable, structured LLM output.

## Directory Structure (after restructuring)
```
podcast_agent/
  db/                # Database helpers and schema
  llm/               # LLM utility functions
  pipeline/          # Modular pipeline steps (ingest, chunk, summarize, plan, script, assemble)
  scripts/           # CLI entry points (agent, podcast_tts)
  ...
```

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the pipeline:**
   ```bash
   python -m podcast_agent.scripts.agent --input podcast_agent/my_book.txt --output podcast_agent/podcast_transcript.txt
   ```
3. **Generate podcast audio:**
   ```bash
   python -m podcast_agent.scripts.podcast_tts --input podcast_agent/podcast_transcript.txt --output podcast.wav --cleaned cleaned_transcript.txt --alex_voice Kore --ben_voice Puck
   ```

## Configuration
- Set your Gemini API credentials in a `.env` file.
- Customize voices and director notes in `podcast_tts.py` as needed.

## Parallelization
- Summarization and script generation steps use thread pools for faster LLM calls.

## Evaluation
- Manual and rubric-based evaluation recommended: check content coverage, structure, fidelity, engagement, and completeness.

## License
MIT
