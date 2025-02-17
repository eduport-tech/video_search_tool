# from vector_db import client, vector_store, embeddings
from chains import (validation_chain,
                    main_chat_chain,
                    question_validition_chain,
                    eduport_context,
                    select_context_chain)
from vector_db import cloude_embd_col
# from langchain.retrievers import BM25Retriever

from google import genai

# Configure your API key (replace YOUR_API_KEY with your key)
client = genai.Client(api_key="AIzaSyBLOv_Q-Ejfrs7b6g3Eg5h3Lr8J55_BsGA")

def select_best_context_via_gemini(results, question):
    """
    Given a list of context results (each a dict with at least 'content', 'url', and 'chapter_name'),
    use a LangChain prompt chain to ask Gemini to select the most relevant result.
    Returns the chosen result (a dict).
    """
    # Format the results list into a single string.
    formatted_results = ""
    for idx, res in enumerate(results):
        excerpt = res.get('content', '')[:200]  # Use first 200 characters for brevity.
        chapter_name = res.get('chapter_name', 'Unknown Chapter')
        formatted_results += f"\nResult {idx+1} (Chapter: {chapter_name}): {excerpt}\n"
    
    chain_input = {
        "question": question,
        "results": formatted_results,
        "num_results": len(results)
    }
    
    # Call the LangChain prompt chain.
    output = select_context_chain(chain_input)
    
    try:
        chosen_num = int(output.strip())
        if 1 <= chosen_num <= len(results):
            return results[chosen_num - 1]
        else:
            return results[0]  # Default to first if out of range.
    except Exception:
        return results[0]  # Default to first if parsing fails.
  

def get_the_correct_context(context_datas, question):
    for context_data in context_datas:
        page_content = context_data['content']
        valid = validation_chain.invoke({"context": page_content, "question": question})
        if valid == 'TRUE':
            return context_data
    return 'FALSE'

def generate_youtube_link(context_data):
    start_time = int(context_data.get('timestamp_start', 0))
    end_time = int(context_data.get('timestamp_end', 0)) if context_data.get('timestamp_end') else None
    url = context_data.get('url', '')
    video_url = f"https://youtu.be/{url}?start={start_time}"
    if end_time:
        video_url += f"&end={end_time}"
    return video_url

def generate_vide_data(context_data):
    return context_data.get('content', '')

def generate_context_response(contexts_data, question):
    correct_context = get_the_correct_context(contexts_data, question)
    if correct_context != 'FALSE':
        link = generate_youtube_link(correct_context)
        video_data = generate_vide_data(correct_context)
    else:
        link = None
        video_data = "Can't find the video for your question."
    return video_data, link

def search_for_timestamp(full_timestamp_data):
    # print(full_timestamp_data)
    # similarity_distance = full_timestamp_data['distances'][0][0]
    matched_data = []
    # if similarity_distance <= 0.7:
    full_documents_data = full_timestamp_data['documents'][0]
    for ind, ques in enumerate(full_documents_data):
        processed_data = {
            "url": full_timestamp_data['metadatas'][0][ind]['youtube_id'],
            "video_name": full_timestamp_data['metadatas'][0][ind]['video_title'],
            "content": ques,
            "chapter_name": full_timestamp_data['metadatas'][0][ind]['chapter_name'],
            "timestamp_start": full_timestamp_data['metadatas'][0][ind]['timestamp_start'],
            "timestamp_end": full_timestamp_data['metadatas'][0][ind]['timestamp_end'],
        }
        print(processed_data['chapter_name'])
        matched_data.append(processed_data)
    return matched_data

def generate_response(question):
    generated_content, link, context = None, None, None
    validition_response = question_validition_chain.invoke({"question": question})
    if validition_response != 'YES':
        generated_content = main_chat_chain.invoke({'context': eduport_context, 'question': question})
        return generated_content, None

    # Get the top 20 context results from your cloud embeddings collection.
    context_results = cloude_embd_col.query(query_texts=question, n_results=50)
    processed_data = search_for_timestamp(context_results)
    
    if processed_data:
        # Call the defined generate_context_response function to choose the context
        context, link = generate_context_response(processed_data, question)
    else:
        context = "Can't find the video for the question"
        link = None

    generated_content = main_chat_chain.invoke({"context": context, "question": question})
    return generated_content, link