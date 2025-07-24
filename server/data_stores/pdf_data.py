from server.brain.vector_db import pdf_collection
from weaviate.classes.query import Filter
from sentence_transformers import CrossEncoder

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2", max_length=512)
def get_pdf_data(question: str, user_course , user_history):
    response = pdf_collection.query.hybrid(query=question,
                                           limit=10,
                                           filters=Filter.by_property("course").equal(user_course))
    all_documents = [prop.properties.get('document') for prop in response.objects]
    re_ranked = model.rank(query=question, documents=all_documents, top_k=1)
    return all_documents[re_ranked[0].get('corpus_id')]