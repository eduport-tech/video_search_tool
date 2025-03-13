from base64 import b64encode
import magic

from langchain_core.messages import HumanMessage

from server.brain.core_llms import llm


def get_mime_type_magic(file_bytes):
    try:
        mime = magic.from_buffer(file_bytes, mime=True)
        return mime
    except Exception as e:
        print(f"Error getting MIME type: {e}")
        return "audio/mp3"


def generate_transcription_data(audio_file):
    audio_base64 = b64encode(audio_file).decode("utf-8")

    audio_mime_type = get_mime_type_magic(audio_file)
    audio_input = {
        "type": "media",
        "mime_type": audio_mime_type,
        "data": audio_base64,
    }
    prompt_message = {
        "type": "text",
        "text": "Translate the following audio from any language to English. Return the translated text in English only. Language code: 'en'. Do not return the result in any other language, especially not Malayalam. Output only the translated text.",
    }
    message = HumanMessage(content=[prompt_message, audio_input])
    response = llm.invoke([message])
    return response.content
