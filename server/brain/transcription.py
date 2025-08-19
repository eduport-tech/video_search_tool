import logging

import magic
import mimetypes
from fastapi import BackgroundTasks
from google.genai import types

from server.models.user import User
from server.config import CONFIG
from server.brain.core_llms import gemini_client
from server.utils.audio_processing import record_audio_input

logger = logging.getLogger(__name__)

def get_mime_type_and_extension_magic(file_bytes):
    try:
        mime = magic.from_buffer(file_bytes, mime=True)
        return mime, mimetypes.guess_extension(mime, strict=False)
    except Exception as e:
        print(f"Error getting MIME type: {e}")
        return "audio/mp3"


async def generate_transcription_data(audio_file, background_tasks: BackgroundTasks, user_id, user_token):
    # audio_base64 = b64encode(audio_file).decode("utf-8")

    audio_mime_type, extension = get_mime_type_and_extension_magic(audio_file)
    initial_file_type = audio_mime_type
    if audio_mime_type == "video/webm":
        audio_mime_type = "audio/webm"
    # audio_input = {
    #     "type": "media",
    #     "mime_type": audio_mime_type,
    #     "data": audio_base64,
    # }
    # prompt_message = {
    #     "type": "text",
    #     "text": "Translate the following audio from any language to English. Return the translated text in English only. Language code: 'en'. Do not return the result in any other language, especially not Malayalam. Output only the translated text.",
    # }
    model_name = "gemini-2.0-flash-001"
    prompt_message = """
    Translate the following audio from any language to English.
    Return the translated text in English only.
    Language code: 'en'.
    Do not return the result in any other language, especially not Malayalam.
    Output only the translated text.
    """
    # message = HumanMessage(content=[prompt_message, audio_input])
    # response = llm.invoke([message])
    user_content = [
        prompt_message,
        types.Part.from_bytes(
            data=audio_file,
            mime_type=audio_mime_type,
        )
    ]
    audio_token_count = gemini_client.models.count_tokens(
        model=model_name,
        contents=user_content,
    )
    if audio_token_count.total_tokens > CONFIG.max_audio_token_limit:
        logger.error(msg=f"The given audio limit crossed EPSID:{user_id}->AudioToken:{audio_token_count.total_tokens}")
        return None
    response = gemini_client.models.generate_content(
        model=model_name,
        contents=user_content
    )
    # await record_audio_input(audio_file, file_type=initial_file_type, usage_data={}, transcribed_text=response.text, user=user, extension=extension)
    background_tasks.add_task(record_audio_input,
                             audio_file=audio_file,
                             file_type=initial_file_type,
                             user_id=user_id,
                             user_token=user_token,
                             extension=extension,
                             response=response)
    return response.text
