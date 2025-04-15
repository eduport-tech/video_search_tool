import chromadb
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from server.config import CONFIG


cloud_emb_store = chromadb.HttpClient(host="95.217.21.180", port=8005)
# cloude_embd_col = cloude_emb_store.get_collection("timestamp_vdb")
cloud_embed_col = cloud_emb_store.get_collection("Timestamped_Transcription_NEET_3")


class QdrantDBClient:
    def __init__(self, url, api_key):
        self.client = QdrantClient(
            url=url,
            api_key=api_key,
        )
        self.embedding_function = SentenceTransformer("all-MiniLM-L6-v2")

    def _process_result(self, results):
        processed_data = []
        for result in results:
            payload = result.payload
            processed_data = {
                "url": payload.get("video_id"),
                "video_name": payload.get("video_title"),
                "content": payload.get("document"),
                "chapter_name": payload.get("chapter_name"),
                "timestamp_start": payload.get("timestamp_start"),
                "timestamp_end": payload.get("timestamp_end"),
            }
            processed_data.append(processed_data)
        return processed_data

    def _search(
        self, search_query: str, course_name: str | None = None, threshold: float = 0
    ):
        filter_condition = None
        if course_name:
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="course_name", match=MatchValue(value=course_name)
                    )
                ]
            )
        embedded_query = self.embedding_function.encode(search_query)
        result = self.client.search(
            collection_name="test_neet_data",
            query_vector=embedded_query,
            limit=5,
            query_filter=filter_condition,
            score_threshold=threshold,
        )
        return result

    def search_store(
        self, search_query: str, course_name: str | None = None, threshold: float = 0
    ):
        result = self._search(search_query, course_name, threshold)
        return self._process_result(result)


qdrant_db_client = QdrantDBClient(
    url=CONFIG.qdrant_url,
    api_key=CONFIG.qdrant_api_key,
)
