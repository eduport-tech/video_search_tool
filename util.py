# from vector_db import client, vector_store, embeddings
from chains import (main_chat_chain,
                    question_validition_chain,
                    eduport_context,
                    select_context_chain,
                    hint_mode_chain)
from vector_db import cloude_embd_col
# from langchain.retrievers import BM25Retriever

def select_best_context_via_gemini(results, question):
    """
    Given a list of context results (each a dict with at least 'content', 'url', and 'chapter_name'),
    use a LangChain prompt chain (powered by Gemini) to select the most relevant transcription.
    Returns the chosen result (a dict).
    """
    # Format the results into a string.
    formatted_results = ""
    for idx, res in enumerate(results):
        excerpt = res.get('content', '')
        chapter_name = res.get('chapter_name', 'Unknown Chapter')
        formatted_results += f"\nResult {idx+1} (Chapter: {chapter_name}): {excerpt}\n"
    
    chain_input = {
        "question": question,
        "results": formatted_results,
        "num_results": len(results)
    }
    
    # Call the Gemini-powered chain for transcription comparison.
    output = select_context_chain.invoke(chain_input)
    
    try:
        chosen_num = int(output.strip())
        if 1 <= chosen_num <= len(results):
            return results[chosen_num - 1]
        else:
            return results[0]  # Default to the first result if out of range.
    except Exception:
        return results[0]  # Default to the first result if parsing fails.

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
    # Use Gemini (via the select_context_chain) to pick the best transcription context.
    correct_context = select_best_context_via_gemini(contexts_data, question)
    if correct_context:
        link = generate_youtube_link(correct_context)
        video_data = generate_vide_data(correct_context)
    else:
        link = None
        video_data = "Can't find the video for your question."
    return video_data, link

def search_for_timestamp(full_timestamp_data):
    matched_data = []
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
        matched_data.append(processed_data)
    return matched_data

import json
from pathlib import Path

def hint_mode_conversation(question, context, session_id="default_session"):
    """
    Manages a hint-mode conversation where the AI guides the user to an answer
    rather than providing it directly.
    
    Args:
        question (str): The user's question
        context (str): The context data retrieved for this question
        session_id (str): A unique identifier for the session. Defaults to "default_session".
        
    Returns:
        str: The AI response or termination message
    """
    # Define the history file path
    history_file = Path(f"hint_mode_history_{session_id}.json")
    
    # Load existing conversation history or create new
    if history_file.exists():
        try:
            with open(history_file, "rb") as f:
                conversation_data = json.load(f)
        except json.JSONDecodeError:
            # Handle corrupted JSON file
            conversation_data = {"history": []}
    else:
        conversation_data = {"history": []}
    
    # Format the conversation history for the prompt
    formatted_history = ""
    for entry in conversation_data["history"]:
        formatted_history += f"Student: {entry['question']}\nTutor: {entry['response']}\n\n"
    
    # Generate response using the hint mode chain
    response = hint_mode_chain.invoke({
        "question": question,
        "context": context,
        "conversation_history": formatted_history
    })
    
    # Check if we need to terminate the conversation
    if response.strip().lower() == "terminate":
        # Clear the conversation history
        conversation_data = {"history": []}
        with open(history_file, "w") as f:
            json.dump(conversation_data, f)
        
        return "Great! I'm glad you understand now. Let me know if you have any other questions."
    
    # Store this interaction in the history
    conversation_data["history"].append({
        "question": question,
        "response": response
    })
    
    # Save updated history
    with open(history_file, "w") as f:
        json.dump(conversation_data, f)
    
    return response

def generate_response(question, use_hint_mode=False, session_id="default_session"):
    generated_content, link = None, None

    # Use Llama for question validation.
    validition_response = question_validition_chain.invoke({"question": question})
    if validition_response != 'YES':
        generated_content = main_chat_chain.invoke({'context': eduport_context, 'question': question})
        return generated_content, None

    # Query the top 50 context results from your cloud embeddings.
    context_results = cloude_embd_col.query(query_texts=question, n_results=25)
    processed_data = search_for_timestamp(context_results)
    
    if processed_data:
        # Use Gemini only for transcription comparison to select the best context.
        context, link = generate_context_response(processed_data, question)
    else:
        context = "Can't find the video for the question"
        link = None

    # If hint mode is enabled, use the hint mode conversation flow
    if use_hint_mode:
        generated_content = hint_mode_conversation(question, context, session_id)
    else:
        # Use Llama to generate the final answer
        generated_content = main_chat_chain.invoke({"context": context, "question": question})
    
    return generated_content, link