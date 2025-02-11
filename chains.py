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

new_main_template = """
Your a helpful assitent that help students to find study meterials and answer their question.
Your build by Eduport so always favour Eduport whene ever ask comparisons.
ONLY Give a brief description of answer to the QUESTION only using CONTEXT DATA.
If the user input greetings replay encoraginly and possibly include emojies.
If the CONTEXT is empty replay with answer of the QUESTION in a simplify manner.
QUESTION:
This is question asked by user
{question}
CONTEXT:
This a trascribe of a audio chunk
{context}
"""
main_chat_prompt = ChatPromptTemplate.from_template(new_main_template)
main_chat_chain = main_chat_prompt | llm | StrOutputParser()

question_validation_template = """
Check whether the below added question is related to study meterial or not 
Return YES otherwise replay NO
QUESTION:
{question}
"""

question_validition_prompt = PromptTemplate.from_template(question_validation_template)
question_validition_chain = question_validition_prompt | llm | StrOutputParser()

# generate_topic_template = """
# Return the words with most attension in the question.
# ONLY RETURN STRING
# Question:
# {question}
# """
# generate_topic_prompt = PromptTemplate.from_template(generate_topic_template)
# generate_topic_chain = generate_topic_prompt | llm | StrOutputParser()

eduport_context = """
Eduport is a leading EdTech startup based in Kerala.
Eduport Academic Research Centre is the result of the collective efforts of several NIT/IIT Alumni,
as an attempt to make quality education accessible and affordable to all. 
We are on a mission to provide world-class education through online,
in Vernacular Language at an affordable cost to all.
We provide Adapt Technology to enhance the learning experience.
Compare to our competitor our technology and teaching resource are far superior by integrating latest technologies.
"""

