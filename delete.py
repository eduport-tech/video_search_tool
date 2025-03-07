# Import the hint_mode_conversation function from your existing code
from IPython.display import clear_output

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

import os
from langchain_groq.chat_models import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["GROQ_API_KEY"] = "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"
os.environ["GOOGLE_API_KEY"] = "AIzaSyCkNqf6Bpmwi_fax72ukDXiJIZ-dI2kJPA"
llama_3 = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

gemini_2_flash = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

gemini_2_flash_exp = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

gemini_2_flash_lite = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

llm = gemini_2_flash_exp

# Define the hint mode template
hint_mode_template = """
As a tutor, your job is to help guide the student toward the correct answer by asking simple, thoughtful questions and gently steering them in the right direction.
Avoid repeating the student's questions.
Use relatable examples, especially from Kerala, to make concepts easier to understand.
If the student makes a mistake, tell them that they are wrong in a friendly manner.
If the student is unsure,  explain things clearly, but not too overly.
Once the student finds the answer, acknowledge their effort and avoid pushing further.
Keep the pace comfortable and don't overcomplicate things.
Do not talk about anything non-academic

Question: {question}
Context: {context}
Conversation History: {conversation_history}
"""

# Create the hint mode prompt template
hint_mode_prompt = PromptTemplate.from_template(hint_mode_template)

# Define the hint mode chain
hint_mode_chain = hint_mode_prompt | llm | StrOutputParser()

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
        formatted_history += f"{entry['question']}\n {entry['response']}\n\n"
    
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

def run_chat_interface():
    """
    Runs a simple terminal-based chat interface within a Jupyter notebook
    that uses the hint_mode_conversation function.
    """
    # Ask for a session ID to enable different conversation threads
    session_id = input("Enter a session ID (or press Enter for default): ").strip()
    if not session_id:
        session_id = "default_session"
    
    print(f"\n=== Hint Mode Chat (Session: {session_id}) ===")
    print("Type 'quit', 'exit', or 'q' to end the conversation.\n")
    
    # Get initial context information
    print("Please provide some context for this tutoring session:")
    context = input("Context: ").strip()
    
    while True:
        # Get the user's question
        print("\nWhat's your question? (or type 'quit' to exit)")
        question = input("You: ").strip()
        
        # Check if the user wants to quit
        if question.lower() in ['quit', 'exit', 'q']:
            print("\nEnding the conversation. Goodbye!")
            break
            
        # Check if the question is empty
        if not question:
            print("Please ask a question or type 'quit' to exit.")
            continue
            
        # Get the AI response using the hint_mode_conversation function
        print("\nThinking...")
        response = hint_mode_conversation(question, context, session_id)
        
        # Display the response
        print(f"\nTutor: {response}")
        
        # Check if the response was a termination message
        if "Great! I'm glad you understand now." in response:
            print("\nThis question has been completed. You can ask a new question or type 'quit' to exit.")
            
            # Optionally ask for new context for the next question
            new_context = input("\nDo you want to provide new context? (Enter to keep current context or type new context): ").strip()
            if new_context:
                context = new_context
                print(f"Context updated for session: {session_id}")

# Run the chat interface
if __name__ == "__main__" or '__main__' == __name__:
    run_chat_interface()