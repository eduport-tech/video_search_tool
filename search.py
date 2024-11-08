import os
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from core_llms import llm
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from util import generate_context_response
import streamlit as st



st.title("Video search tool")
prompt_text = """
Your a helpful bot that fetch educational video from the eduport accadamy sources accordingly.
That is your PERPOSE
ONLY Give a brief description about the video conent using context data if not video is found replay accourdingly.
If the user input greetings replay encoraginly for your PERPOSE and possibly include emojies
Context:
{context}
Question:
{question}
"""

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# setup chromadb client
client = chromadb.PersistentClient(path="./chroma_db")

# collection
collection = client.get_or_create_collection(name="video_embeddings",
                                             metadata={"hnsw:space": "cosine"})


vector_store = Chroma(client=client,
                      collection_name="video_embeddings",
                      embedding_function=embeddings,)

#print(vector_store.similarity_search("gravitaional field", filter={"timestamp_end": {"$gte": 90}}))

prompt = ChatPromptTemplate.from_template(prompt_text)

chain = prompt | llm | StrOutputParser()

question = st.chat_input("Say something")
if question:
    context_data = vector_store.similarity_search_by_vector_with_relevance_scores(embeddings.embed_query(question))
    context, link = generate_context_response(context_data, question)
    generated_content = chain.invoke({"context": context, "question": question})
    st.write(generated_content)
    print(generated_content, link, context)
    # st.video("https://www.youtube.com/watch?v=3FGuMoTydHw&t=1229s", autoplay=True, start_time=generated_link.split('&start=')[1].split('&end=')[0])
    if link:
        st.link_button("Video", link)
    # st.write(f"User has sent the following prompt: {prompt}")
#question = "What is the approximate radius of Earth?"

