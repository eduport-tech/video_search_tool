from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_vertexai import ChatVertexAI
from google import genai
from google.genai import types


# llama_3 = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     temperature=0,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,
# )

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

gemini_2_flash_vertex = ChatVertexAI(
    model="gemini-2.0-flash-001",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

gemini_2_pro_vertex_exp = ChatVertexAI(
    model="gemini-2.0-pro-exp-02-05",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

gemini_2_flash_lite_vertex = ChatVertexAI(
    model="gemini-2.0-flash-lite-001",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

gemini_client = genai.Client(vertexai=True,
                             project="eduport-staging",
                             location="global")

def gemini_2_5_flash(system_instruction: str, contents: list):
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config = types.GenerateContentConfig(
            temperature=0,
            system_instruction=system_instruction,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )
    )
    return response

llm = gemini_2_flash
