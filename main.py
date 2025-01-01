from typing import Annotated
from fastapi import FastAPI, File
from fastapi.middleware.cors import CORSMiddleware
from util import generate_response
from trasncription import generate_transcription_data

app = FastAPI()
allowed_orgins = [
    "http://*.eduport.ai",
]

app.add_middleware(
    CORSMiddleware,
    allowed_orgins=allowed_orgins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return "PONG"

@app.post("/question")
def video_search_api(question: str):
    generated_content, link = generate_response(question)
    return {"content": generated_content, "link": link}

@app.post("/audio")
def audio_transcription(audio_data: Annotated[bytes, File()]):
    transcription = generate_transcription_data(audio_data)
    return transcription
