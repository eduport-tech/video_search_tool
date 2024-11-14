import streamlit as st

from core_llms import llm
from util import generate_response
from trasncription import generate_transcription_data

st.title("Video search tool")

question = st.chat_input("Say something")
audio_value = st.audio_input("Record a voice message")
# question = "gravitation field"
if question:
    generated_content, link = generate_response(question)
    st.write(generated_content)
    if link:
        st.link_button("Video", link)

if audio_value:
    audio_data = generate_transcription_data(audio_value)
    print(audio_data,"response data----->>>")
    if audio_data:
        generated_content, link = generate_response(audio_data)
        st.write(generated_content)
        if link:
            st.link_button("Video", link)