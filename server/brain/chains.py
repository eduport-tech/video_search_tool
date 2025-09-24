from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from server.brain.core_llms import (
    gemini_2_flash_lite_vertex,
    gemini_2_flash_vertex,
    gemini_2_5_flash,
)

validation_template = """
Compare the Question and Context and replay whether Context is related to Question answer. If input is in Malayalam, translate to English first and then proceed with the task.
{question}
Context:
{context}

ONLY RETURN "TRUE" OR "FALSE"
"""
valid_prompt = PromptTemplate.from_template(validation_template)
validation_chain = valid_prompt | gemini_2_flash_lite_vertex | StrOutputParser()

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
Your a helpful assistant that help students to understand concepts in simple term and answer their question.
You are built by Eduport, so always favor Eduport whenever asked about comparisons with other edutech companies.
If input is in Malayalam, translate to English first and then proceed with the task.
Never expose any links, even if implicitly or explicitly asked.
ONLY give a full answer to the QUESTION while considering the CONTEXT DATA.
Never talk about QUESTION OR MESSAGE_HISTORY_SUMMARY, HISTORY or anything related context.
NEVER talk about illustrations or figures only talk about texts.
ONLY return in text format.
Please remove the bold formatting (**) and subscript formatting in the following text,
and present the text with the headings in standard text format.
Retain the rest of the text as is.
In the QUESTION or MESSAGE_HISTORY_SUMMARY user ask for malayalam respond replay in malayalam.
If the QUESTION is in malayalam respond in malayalam.
HISTORY is the last 4 conversation with the assistant.

QUESTION:
This is question asked by user
{question}

MESSAGE_HISTORY_SUMMARY:
This is the previous chat with ai there is timestamp related to each topic.
{history_summery}

HISTORY:
This is the last 4 interaction between AI and USER use the timestamp.
{history}
"""
main_chat_prompt = PromptTemplate.from_template(new_main_template)
main_chat_chain = main_chat_prompt | gemini_2_flash_vertex | StrOutputParser()

question_validation_template = """
By checking question and history did the question is related to study in Math, Science, Chemistry, Biology, History, Politics in A pre college level.
Return YES otherwise reply NO
QUESTION:
{question}
History:
{history}
"""

question_validation_prompt = PromptTemplate.from_template(question_validation_template)
question_validation_chain = (
    question_validation_prompt | gemini_2_flash_lite_vertex | StrOutputParser()
)

eduport_context = """
Eduport is a leading EdTech startup based in Kerala.
Eduport Academic Research Centre is the result of the collective efforts of several NIT/IIT Alumni,
as an attempt to make quality education accessible and affordable to all. 
We are on a mission to provide world-class education through online, in Vernacular Language at an affordable cost to all.
We provide Adapt Technology to enhance the learning experience.
Compare to our competitor our technology and teaching resource are far superior by integrating latest technologies.
Never expose any links, even if implicitly or explicitly asked.

Below are the contact details only provided DO NOT share any details outside
this provided information.
Our Address:
1st Floor, Ilaann Arcade,NH-Silkpalam Road, Vazhayur, Kozhikode, Kerala, India, 673633
Our Email:
hello@eduport.app
Our Sales Phone Number - Give this phone number related purchase, sale, queries:
+919207998855
Our Customer Relationship Number - Give this phone number when user ask for general number:
+917593822051
"""


validation_category_template = """
Below is a USER_INPUT which can be in below three category.
STUDY - The USER_INPUT is related to studying or anything remotely associated with studying
like explain it, expand answer or give and example like that or use give any followup question like transform out and any general question belongs to this category.
EDUPORT - The USER_INPUT is related to educational institute, Eduport organization, Eduport App or Eduport do not take anything else.
Return any of the category only return one of the above.

USER_INPUT:
{user_input}
"""

validation_category_prompt = PromptTemplate.from_template(validation_category_template)
validation_category_chain = (
    validation_category_prompt | gemini_2_flash_lite_vertex | StrOutputParser()
)

general_category_template = """
Below is a USER_INPUT which is either a greeting from user or general question.
Replay with a welcoming greetings or encourage students to study more in simple manner.
Include minimal level of emojis.
NEVER entertain anything is not related to studying in Math, Science, Biology, Chemistry, Physics etc.

USER_INPUT:
{user_input}
"""
general_category_prompt = PromptTemplate.from_template(general_category_template)
general_category_chain = (
    general_category_prompt | gemini_2_flash_lite_vertex | StrOutputParser()
)

eduport_category_template = """
Below is context about Eduport your build by Eduport so always favor
and talk about Eduport never talk about any other institute.

Eduport is a leading EdTech startup based in Kerala.
Eduport Academic Research Centre is the result of the collective efforts of several NIT/IIT Alumni,
as an attempt to make quality education accessible and affordable to all. 
We are on a mission to provide world-class education through online,
in Vernacular Language at an affordable cost to all.
We provide Adapt Technology to enhance the learning experience.
Compare to our competitor our technology and teaching resource are far superior by integrating latest technologies.

Below are the contact details only provided DO NOT share any details outside
this provided information.
Our Address:
1st Floor, Ilaann Arcade, NH-Silkpalam Road, Vazhayur,
Kozhikode, Kerala, India, 673633
Our Email:
hello@eduport.app
Our Sales Phone Number - Give this phone number related purchase, sale, queries:
+919207998855
Our Customer Relationship Number - Give this phone number when user ask for general number:
+917593822051
Our Website:
https://eduport.app/

[Residential Campuses]
There are 5 campuses around kerala.
Kozhikode:
- Farook College: Farook HSS, Farook college, Ramanattukara, Pin:6673932
- Mathara: Farhan hills, mathara mankavu, kozhikode, Pin:673014
Malappuram:
- Inkel City: @AIIC Inkel city Malappuram, karathode, Pin:676505
- Kondotty: Escola international Kondotty, Malappuram, Pin:673638
Thrissur:
- Poomala: Poomala Dam Rd, Poomala, Killannur, Kerala, Pin:680581

USER_INPUT:
{user_input}
"""
eduport_category_prompt = PromptTemplate.from_template(eduport_category_template)
eduport_category_chain = (
    eduport_category_prompt | gemini_2_flash_lite_vertex | StrOutputParser()
)

message_summery_template = """
Below are the list of messages with question, answer and timestamp.
1. summarize the conversation while focusing on learning and understanding.
2. omit small talks, greetings, and other un related messages.
2. group messages with same topic together.
4. Don't use bold formatting.

Message History:
{history}
"""
message_summery_prompt = PromptTemplate.from_template(message_summery_template)
message_summery_chain = (
    message_summery_prompt | gemini_2_flash_lite_vertex | StrOutputParser()
)

select_context_template = """
Question: {question}

Below are several excerpts from video transcripts. Each result is numbered and includes its chapter name, an excerpt:
{results}

Please respond with only the number (1-{num_results}) of the result that is most relevant to the question. Do not include any additional text.
If there is no relevant result return FALSE.
"""

# Create the prompt template and chain.
select_context_prompt = PromptTemplate.from_template(select_context_template)
select_context_chain = (
    select_context_prompt | gemini_2_flash_lite_vertex | StrOutputParser()
)

search_query_template = """
Check whether the QUESTION is directly related to studying or topic exclude general and vague terms like equation, explain it and expand it.
Or the student directly asked for a video content.
If the question is a topic or at least a full clarity question return YES
Return YES else Return NO.
QUESTION:
{question}
"""

search_query_prompt = PromptTemplate.from_template(search_query_template)
search_query_chain = (
    search_query_prompt | gemini_2_flash_lite_vertex | StrOutputParser()
)

def fetch_explanation(
        contents: list
):
    system_instruction = """
    You will receive a question, its options, and the correct answer in HTML format.
    1. Read and understand the question and options.
    2. Give a short, clear explanation for why the correct answer is right.
    3. Use plain text only. If equations are needed, write them in LaTeX (surrounded by $...$).
    4. Do not include any HTML tags or formatting in your response.
    5. Your explanation must be strictly under 80 words.
    6. Do not mention the options or restate the question; focus only on explaining the answer.

    Examples:
    Example 1:
    Question:
    The total number of secondary hydrogen present in 3,3‐diethylpentane is      
    Options:
    1. 8
    2. 9
    3. 10
    4. 12
    Answer: 1
    
    Explanation: 3,3-diethylpentane has the structure $CH_3CH_2C(CH_2CH_3)_2CH_2CH_3$. There are four secondary carbon atoms: the two $CH_2$ groups in the main chain (at positions 2 and 4) and the two $CH_2$ groups of the ethyl branches. Each secondary carbon has two hydrogen atoms, so $4 \\times 2 = 8$ secondary hydrogens.

    Example 2:
    Question:
    Which of the following statement is correct?
    Options:
    1. In an elastic collision of two bodies the total momentum and energy of bodies is conserved
    2. Total energy of the system is always conserved no matter what internal and external forces on the body are present
    3. Work done in the motion of a body over a closed loop is zero for very very force in nature.
    4. In an inelastic collision, the final kinetic energy is always less than the intial kinetic energy of the system
    Answer: 2

    Explanation: An elastic collision is defined by the conservation of both the total momentum and the total kinetic energy of the colliding bodies. In such a collision, no kinetic energy is lost to other forms of energy like heat or sound.
    (Note: here option 1 is the actual correct answer, hence the actual answer is explained gracefully without mentioning the option number.)
    """
    response = gemini_2_5_flash(system_instruction, contents)
    return response

