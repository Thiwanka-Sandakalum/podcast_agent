"""
podcast_tts.py
Convert a podcast transcript (text file) into a natural, multi-speaker podcast audio using Gemini TTS.
"""
import os
import re
import wave
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def clean_transcript(input_path, output_path, speakers):
    """
    Cleans the transcript for TTS: removes 'Speaker:' prefixes, asterisks, and keeps only lines with clear speaker names.
    Writes cleaned transcript to output_path.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    cleaned_lines = []
    for line in lines:
        # Remove 'Speaker:' and asterisks, keep only lines with 'Name:'
        line = line.strip()
        if not line:
            continue
        # Remove 'Speaker:' prefix
        if line.startswith('Speaker:'):
            line = line[len('Speaker:'):].strip()
        # Remove asterisks and sound effect lines
        if line.startswith('**') or line.startswith('---') or line.startswith('(Outro') or line.startswith('(Intro'):
            continue
        # Only keep lines with speaker names
        match = re.match(r'(\w+):', line)
        if match and match.group(1) in speakers:
            cleaned_lines.append(line)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    return '\n'.join(cleaned_lines)

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

def transcript_to_audio(transcript_text, output_wav, speakers_voices, director_note=None):
    """
    Calls Gemini TTS API to convert transcript_text to audio, mapping speakers to voices.
    """
    client = genai.Client()
    # Add director's note if provided
    if director_note:
        prompt = director_note + "\n\n" + transcript_text
    else:
        prompt = transcript_text
    # Build MultiSpeakerVoiceConfig
    speaker_voice_configs = []
    for speaker, voice in speakers_voices.items():
        speaker_voice_configs.append(
            types.SpeakerVoiceConfig(
                speaker=speaker,
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
                )
            )
        )
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=speaker_voice_configs
                )
            ),
        )
    )
    data = response.candidates[0].content.parts[0].inline_data.data
    wave_file(output_wav, data)
    print(f"Audio saved to {output_wav}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Podcast Transcript to Audio with Gemini TTS")
    parser.add_argument('--input', type=str, required=True, help='Input transcript text file')
    parser.add_argument('--output', type=str, default='podcast.wav', help='Output WAV file')
    parser.add_argument('--cleaned', type=str, default='cleaned_transcript.txt', help='Cleaned transcript file')
    parser.add_argument('--alex_voice', type=str, default='Kore', help='Voice for Alex')
    parser.add_argument('--ben_voice', type=str, default='Puck', help='Voice for Ben')
    args = parser.parse_args()

    speakers = ['Alex', 'Ben']
    speakers_voices = {'Alex': args.alex_voice, 'Ben': args.ben_voice}
    director_note = (
        "# AUDIO PROFILE: Alex & Ben\n"
        "## THE SCENE: Professional podcast studio, friendly and insightful.\n"
        "### DIRECTOR'S NOTES\n"
        "Alex: Upbeat, friendly, American accent.\n"
        "Ben: Calm, insightful, British accent.\n"
        "Pacing: Natural, conversational, engaging.\n"
    )

    # Clean transcript
    cleaned_text = clean_transcript(args.input, args.cleaned, speakers)
    # Generate audio
    transcript_to_audio(cleaned_text, args.output, speakers_voices, director_note=director_note)

if __name__ == "__main__":
    main()
