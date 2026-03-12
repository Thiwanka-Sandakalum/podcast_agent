from google import genai
import json

client = genai.Client()

def gemini_summarize(text):
    prompt = (
        "Summarize the following book section for a podcast episode. "
        "Focus on clarity, engagement, and conversational tone. "
        "Limit to 5-7 sentences.\n"
        "Text:\n" + text
    )
    response = client.models.generate_content(
        model="gemma-3-27b-it",
        contents=prompt,
    )
    return response.text

def gemini_plan(summaries):
    import logging
    joined = "\n\n".join(summaries)
    prompt = (
        "You are a podcast producer. Given these summaries, plan a podcast episode with 3-5 sections.\n"
        "For each section, provide a short, catchy 'title' and a 2-3 sentence 'description'.\n"
        "Respond ONLY with a JSON list in this format. Do not include any explanation, commentary, or extra text. Strictly output valid JSON only.\n"
        "[\n  {\"title\": \"...\", \"description\": \"...\"}, ...\n]\n"
        "Summaries:\n" + joined
    )
    logging.info("Sending podcast planning prompt to Gemini LLM.")
    response = client.models.generate_content(
        model="gemma-3-27b-it",
        contents=prompt,
    )
    logging.info(f"LLM raw response: {response.text}")
    try:
        if response.text is not None:
            return json.loads(response.text)
        else:
            return ""
    except Exception:
        logging.warning("LLM response was not valid JSON, returning raw text.")
        return response.text if response.text is not None else ""

def gemini_script(title, description):
    prompt = (
        f"Write a podcast dialogue for the section titled '{title}'.\n"
        "Use only two speakers: Alex and Ben. No sound effects or music cues.\n"
        "Make the conversation lively, insightful, and natural.\n"
        "Include at least 6 exchanges (alternating lines).\n"
        "Start with Alex introducing the topic, then Ben responds, and continue the discussion.\n"
        f"Section description: {description}"
    )
    response = client.models.generate_content(
        model="gemma-3-27b-it",
        contents=prompt,
    )
    return response.text
