import google.generativeai as genai

genai.configure(api_key="AIzaSyA4ZC2GPhOt5NYcSXcySZXYwZj7PJ6tE-M")

model = genai.GenerativeModel("gemini-1.5-pro")

# prompt = "Transcribe this audio to english if not enlgish translate it and only return the transcribed data."
prompt = "ONLY Translate audio to english always return single string."

def generate_transcription_data(audio_file):
    response = model.generate_content([
        prompt,
        {
            "mime_type": "audio/mp3",
            "data": audio_file.read()
        }
    ],
    generation_config = genai.GenerationConfig(
        temperature=0,
    ))
    return response.text