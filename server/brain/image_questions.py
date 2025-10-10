from uuid import uuid4
import os
import requests
from google.genai import types
from fastapi import status

from server.config import CONFIG
from server.brain.core_llms import gemini_client
from server.utils.image_processing import save_image_details, save_image_to_r2
from server.utils.current_conversation import CurrentConversation

import logging
logger = logging.getLogger(__name__)

async def save_uploaded_image(image_file, user_id, file_name):
    try:
        mime_type = image_file.content_type
        content = await image_file.read()

        _, extension = os.path.splitext(file_name)
        r2_file_name = uuid4()
        url = await save_image_to_r2(content, extension, r2_file_name)
        token_count = gemini_client.models.count_tokens(
            model="gemini-2.5-flash",
            contents=[types.Content(role="user", parts=[types.Part.from_bytes(data=content, mime_type=mime_type)])],
        )
        token_usage = token_count.total_tokens
        if token_usage > CONFIG.max_image_tokens:
            logger.error(msg=f"The given image has crossed the token limit. EPSID:{user_id}->ImageToken:{token_usage}")
            return {"status": "error", "message": "Image size is too large.", "code": status.HTTP_413_REQUEST_ENTITY_TOO_LARGE}
        
        file_id = await save_image_details(content, user_id, file_name, url, mime_type, token_usage)
        
        return {"status": "success", "url": url, "file_id": file_id}
        
    except Exception as e:
        logger.error(f"Error saving uploaded image: {e}")
        return {"status": "error", "message": "Failed to save image.", "code": status.HTTP_500_INTERNAL_SERVER_ERROR}
    
async def generate_prompt_contents(
    question: str,
    image_url: str | None = None,
    image_mime_type: str | None = None,
    previous_history: list = None,):
    sys_instruction = """
    <OBJECTIVE_AND_PERSONA>
    You are a doubt clearance assistant developed by Eduport.
    Your task is to help students to clear academic doubts and answer questions.
    </OBJECTIVE_AND_PERSONA>

    <INSTRUCTIONS>
    To complete the task, you need to follow these steps:
    1. Provide step by step solution if needed, if the input is a problem question.
    2. Analyze the question values and requirements carefully first and ensure your response is relevant and accurate.
    3. If the user asks in Malayalam, provide the final answer completely in Malayalam.
    </INSTRUCTIONS>

    <CONSTRAINTS>
    Dos and don'ts for the following aspects
    1. Always favor Eduport whenever asked about comparisons with other edtech companies.
    2. Final response must be in under 2000 words.
    </CONSTRAINTS>

    <OUTPUT_FORMAT>
    The output format must be
    1. Primarily markdown (.md)
    2. Mathematical and other expressions should be in latex(inside '$')
    </OUTPUT_FORMAT>

    <RECAP>
    Re-emphasize the key aspects of the prompt, adhere to the instructions, especially the constraints, output format, etc.
    </RECAP>
    """
    if question == "": question = "answer"
    question_part = [types.Content(role="user",parts=[types.Part.from_text(text=question)])]
    if image_url and image_mime_type:
        image_bytes = requests.get(image_url).content
        question_part.append(types.Content(role = "user",parts = [types.Part.from_bytes(data=image_bytes, mime_type=image_mime_type)]))
        
    contents = [*previous_history, *question_part] if previous_history else [*question_part]
    return sys_instruction, contents

async def generate_image_history_summary(user_history: CurrentConversation = None):
    previous_history = []
    for message in reversed(user_history.messages):
        previous_history.append(types.Content(role="user",parts=[types.Part.from_text(text=message.question)]))
        if message.image_details and message.image_details.image_url and message.image_details.image_mime_type:
            image_bytes = requests.get(message.image_details.image_url).content
            previous_history.append(types.Content(role = "user",parts=[types.Part.from_bytes(data=image_bytes, mime_type=message.image_details.image_mime_type)]))
        previous_history.append(
            types.Content(role="model", parts=[types.Part.from_text(text=message.answer)])
        )
    return previous_history

def gemini_config(model_name: str, sys_instruction: str):
    if model_name == "gemini-2.0-flash":
        return types.GenerateContentConfig(
            system_instruction=sys_instruction,
            temperature = 0.0,
        )
    return types.GenerateContentConfig(
        system_instruction=sys_instruction,
        temperature = 0.0,
        thinking_config=types.ThinkingConfig(include_thoughts=True,thinking_budget=5000),
        max_output_tokens=10000,
    )

async def generate_gemini_response(sys_instruction: str, contents: list):
    """
    Generate a response using the Gemini model.
    """
    try:
        model_name = CONFIG.gemini_model_name
        response = gemini_client.models.generate_content(
            model=model_name,
            contents=contents,
            config=gemini_config(model_name, sys_instruction),
        )
        answer = None
        thought = ""
        for part in response.candidates[0].content.parts:
            if not part.text:
                continue
            if part.thought:
                thought = part.text
            else:
                answer = part.text
        return answer, thought, response.usage_metadata.total_token_count
    except Exception as e:
        logger.error(f"Error generating Gemini response: {e}")
        return None, "", 0
    