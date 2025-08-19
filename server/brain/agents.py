from google.genai import types

def get_grounding_tool():
    grounding_tool = types.Tool(
        google_search=types.GoogleSearch()
    )
    return grounding_tool

def get_gemini_config(system_prompt=""):
    grounding_tool = get_grounding_tool()
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=[grounding_tool]
    )
    return config