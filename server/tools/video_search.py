from server.brain.vector_db import qdrant_db_client
from typing_extensions import TypedDict
from server.brain.chains import search_query_chain
from server.utils.util import (
    search_for_timestamp,
    generate_context_response,
    find_video_topic,
)
from server.brain.vector_db import cloud_embed_col


class VideoResponse(TypedDict):
    url: str
    content: str


def get_query_video(query_string: str, video_id: int) -> VideoResponse:
    is_video_search = search_query_chain.invoke({"question": query_string}).rstrip()
    if is_video_search == "YES":
        if video_id:
            video_topic = find_video_topic(query_string, video_id)
            if video_topic:
                search_query = {"topic": video_topic}
        context = cloud_embed_col.query(
            query_texts=query_string, where=search_query, n_results=10
        )
        processed_data = search_for_timestamp(context) if context else None
        if processed_data:
            context, link = generate_context_response(processed_data, query_string)
    return context, link


class VideoSearchTool:
    pass
