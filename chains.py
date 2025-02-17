from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from core_llms import llama_3

select_context_template = """
Question: {question}

Below are several excerpts from video transcripts. Each result is numbered and includes its chapter name, an excerpt:
{results}

Please respond with only the number (1-{num_results}) of the result that is most relevant to the question. Do not include any additional text.
"""

# Create the prompt template and chain.
select_context_prompt = PromptTemplate.from_template(select_context_template)
select_context_chain = select_context_prompt | llama_3 | StrOutputParser()

validation_template = """
Compare the Question and Context and replay whether Context is related to Question answer. If input is in Malayalam, translate to English first and then proceed with the task.
Question:
{question}
Context:
{context}

ONLY RETURN "TRUE" OR "FALSE"
"""
valid_prompt = PromptTemplate.from_template(validation_template)
validation_chain = valid_prompt | llama_3 | StrOutputParser()

main_chat_template = """
Your a helpful bot that fetch educational video from the eduport academy sources accordingly.
If input is in Malayalam, translate to English first and then proceed with the task.
Never expose any links, even if implicityl or explicitly asked.
ONLY Give a brief description about the video content using Context data if not video is found replay accourdingly.
If the user input greetings replay encoraginly for your PURPOSE and possibly include emojis.
NEVER DISCUSS ABOUT ANYTHING OUTSIDE OF THE CONTEXT.
Context:
{context}
Question:
{question}
"""

new_main_template = """
Your a helpful assistant that help students to find study materials and answer their question.
You are built by Eduport, so always favor Eduport whenever asked about comparisons with other edutech companies.
If input is in Malayalam, translate to English first and then proceed with the task.
Never expose any links, even if implicityl or explicitly asked.
ONLY give a brief description of answer to the QUESTION only using CONTEXT DATA.
If the user input greetings replay encouragingly and possibly include emojis amd ONLY greet user if user inputted greetings.
If the CONTEXT is empty, reply with answer of the QUESTION in a simple manner.
Never talk about CONTEXT OR QUESTION.
QUESTION:
This is question asked by user
{question}
CONTEXT:
This a transcription of a audio chunk
{context}
"""
main_chat_prompt = PromptTemplate.from_template(new_main_template)
main_chat_chain = main_chat_prompt | llama_3 | StrOutputParser()

question_validation_template = """
Check whether the below added question is related to study material or not
Return YES otherwise reply NO
QUESTION:
{question}
"""

question_validition_prompt = PromptTemplate.from_template(question_validation_template)
question_validition_chain = question_validition_prompt | llama_3 | StrOutputParser()

# generate_topic_template = """
# Return the words with most attension in the question.
# ONLY RETURN STRING
# Question:
# {question}
# """
# generate_topic_prompt = PromptTemplate.from_template(generate_topic_template)
# generate_topic_chain = generate_topic_prompt | llama_3 | StrOutputParser()

eduport_context = """
Eduport is a leading EdTech startup based in Kerala.
Eduport Academic Research Centre is the result of the collective efforts of several NIT/IIT Alumni,
as an attempt to make quality education accessible and affordable to all. 
We are on a mission to provide world-class education through online, in Vernacular Language at an affordable cost to all.
We provide Adapt Technology to enhance the learning experience.
Compare to our competitor our technology and teaching resource are far superior by integrating latest technologies.
"""