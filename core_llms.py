import os
from langchain_groq.chat_models import ChatGroq

os.environ["GROQ_API_KEY"] = "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"
llm = ChatGroq(
    model="llama-3.3-70b-specdec",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)