from google.genai import types
import requests
from bs4 import BeautifulSoup
from typing import Iterator
from redis.asyncio import Redis
import logging

from server.models.qa_explanation import QuestionNAnswer
from server.brain.chains import fetch_explanation

logger = logging.getLogger(__name__)

def separate_image_and_text(question_text: str) -> tuple[str, str | None]:
    soup = BeautifulSoup(question_text, 'html.parser')
    image_tag = soup.find('img')
    image_url = None

    if image_tag and image_tag.get('src'):
        image_url = image_tag.get('src')
        image_tag.decompose()

    extracted_text = soup.get_text().strip()
    return extracted_text, image_url


def create_parts_for_item(item_html: str, label: str) -> Iterator[types.Part]:
    extracted_text, image_url = separate_image_and_text(item_html)

    yield types.Part.from_text(text=f"{label}: {extracted_text}")

    if image_url:
        img_bytes = requests.get(image_url).content
        yield types.Part.from_bytes(data=img_bytes, mime_type="image/png")


def prepare_contents(question_answer: QuestionNAnswer):
    content_parts = []

    content_parts.extend(create_parts_for_item(question_answer.question, "Question"))
    for option in question_answer.options:
        label = f"Option {option.option}"
        content_parts.extend(create_parts_for_item(option.value, label))
    content_parts.extend(create_parts_for_item(question_answer.answer, "Answer"))

    contents = [types.Content(role="user", parts=content_parts)]
    return contents


async def fetch_explanation_for_qa(
        question_answer: QuestionNAnswer,
        redis: Redis
):
    cache_key = f"question_{question_answer.question_id}"
    try:
        cached_explanation = await redis.get(cache_key)
    except Exception as e:
        logger.error(f"Redis GET failed: {e}")
        cached_explanation = None 
    if cached_explanation:
        return cached_explanation

    contents = prepare_contents(question_answer)
    response = fetch_explanation(contents=contents)
    explanation_text = response.text

    try:
        await redis.set(cache_key, explanation_text)
    except Exception as e:
        logger.error(f"Redis SET failed: {e}")
    return explanation_text