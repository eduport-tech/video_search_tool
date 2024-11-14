from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from core_llms import llm

validation_template = """
Compare the Question and Context and replay whether Context is related to Question answer.
Question:
{question}
Context:
{context}

ONLY RETURN "TRUE" OR "FALSE"
"""
valid_propmpt = PromptTemplate.from_template(validation_template)
validation_chain = valid_propmpt | llm | StrOutputParser()


main_chat_template = """
Your a helpful bot that fetch educational video from the eduport accadamy sources accordingly.
That is your PERPOSE
ONLY Give a brief description about the video conent using Context data if not video is found replay accourdingly.
If the user input greetings replay encoraginly for your PERPOSE and possibly include emojies.
NEVER REPLAY ANYTHING OUTSIDE OF Context DATA.
Context:
{context}
Question:
{question}
"""
main_chat_prompt = ChatPromptTemplate.from_template(main_chat_template)
main_chat_chain = main_chat_prompt | llm | StrOutputParser()


# generate_topic_template = """
# Return the words with most attension in the question.
# ONLY RETURN STRING
# Question:
# {question}
# """
# generate_topic_prompt = PromptTemplate.from_template(generate_topic_template)
# generate_topic_chain = generate_topic_prompt | llm | StrOutputParser()



