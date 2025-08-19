from google.genai import types

def generate_gemini_contents(question, history):
    history_contents = generate_history_contents(history)
    history_contents.append(types.Content(role="user", parts=[types.Part(text=question)]))
    print(history_contents)
    return history_contents

def generate_history_contents(history):
    contents = []
    for message in history:
        user_message = types.Content(role="user", parts=[types.Part(text=message.question)])
        model_answer = types.Content(role="assistant", parts=[types.Part(text=message.answer)])
        contents.append(user_message)
        contents.append(model_answer)
    return contents