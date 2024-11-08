from core_llms import llm
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

validation_propmt = """
Compare the Inputed Question and Context and replay whether the question is fully or partially answered or not.
Inputed Question:
{question}
Context:
{context}

ONLY RETURN "TRUE" OR "FALSE"
"""
valid_propmpt = PromptTemplate.from_template(validation_propmt)
validation_chain = valid_propmpt | llm | StrOutputParser()

def get_the_correct_context(context_datas, question):
  for context_data in context_datas:
    page_content = context_data[0].page_content
    valid = validation_chain.invoke({"context": page_content, "question": question})
    if valid == 'TRUE':
      return context_data
  return 'FALSE'

def generate_youtube_link(context_data):
  metadata = context_data[0].metadata
  start_time = int(metadata['timestamp_start'])
  end_time = int(metadata['timestamp_end'])
  url = metadata['url']
  video_url = f"{url}&start={start_time}&end={end_time}"
  return video_url

def generate_vide_data(context_data):
  data = context_data[0].page_content
  confidence = context_data[1]
  return data

def generate_context_response(contexts_data, question):
  correct_context = get_the_correct_context(contexts_data, question)
  print(contexts_data, "genrate-------->>")
  if correct_context != 'FALSE':
    link = generate_youtube_link(correct_context)
    print(link)
    video_data = generate_vide_data(correct_context)
  else:
    link = None
    video_data = "Can't find the video for your question."
  return video_data, link