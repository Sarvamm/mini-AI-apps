# ---------------------------------------------------------------------------- #
#                                 I M P O R T S                                #
# ---------------------------------------------------------------------------- #
import streamlit as st
import time
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from pydantic import Field, BaseModel
from typing import Dict
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ------------------------- Initializing Chat Models ------------------------- #
qwen = ChatOllama(model="qwen3:latest", temperature=0.6, extract_reasoning=True)
qwq = ChatGroq(
    model="qwen-qwq-32b",
    temperature=0.6,
    streaming=True,
    api_key="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"
)
model = qwen
# ----------------------- Preparing structured outputs ----------------------- #
class questions_output(BaseModel):
    """Response to the prompt in the following format only"""
    thinking_content: str = Field(description="All the reasoning/thinking content here")
    response_content: list[str] = Field(
        description="Generate questions in the format of list of strings"
    )
class quiz_output(BaseModel):
    """Response to the prompt in the following format only"""
    class QuestionItem(BaseModel):
        question: str = Field(description="Question to be asked")
        extra_content: str = Field(
            description="Optionally any extra content such as markdown formula etc"
        )
        image_link: str = Field(
            description="Optionally and image link related to the question"
        )
        options: Dict[str, bool] = Field(
            description="A dictionary with string options each pointing to a bool, True if the option is correct and false otherwise"
        )

    thinking_content: str = Field(description="All the reasoning/thinking content here")
    response_content: list[QuestionItem] = Field(
        description="A list containing questions items"
    )


# ---------------- Modified models that give structured output --------------- #
model_questions = model.with_structured_output(questions_output)
model_quiz = model.with_structured_output(quiz_output)

# ---------------------------------------------------------------------------- #
def streamer(text: str, speed: float = 0.01):
    for char in text:
        time.sleep(speed)
        yield char


# -------------------------- Constructing runnables -------------------------- #
NOTES_PROMPT_TEMPLATE = r"""
You are a professional college professor. Generate a set of comprehensive notes based on the topic provided.
The notes should be detailed, well-structured, and easy to understand. 
Use $...$ to wrap *every* mathematical expression, including equations, formulas, or symbols.
The notes should be suitable for students in their final year of high school or the first year of university.
Use proper markdown formatting where necessary. Use headers, subheader, dividers etc. 
For math or physics related topics, use Latex in inline markdown using the $ symbol. For example: $E=mc^2$.
Wrap full LaTeX blocks like matrices in $$...$$.
Example: $$A = \begin{{bmatrix}} 1 & 2 \\ 3 & 4 \end{{bmatrix}}$$
Wrap inline formulas like $a_{{ij}}$ or $x^2 + y^2 = z^2$.
Do not forget to include both dollar signs.

Here are the topics:
{topics}
    """

notes_prompt = PromptTemplate.from_template(NOTES_PROMPT_TEMPLATE)


# ---------------------------------------------------------------------------- #
QUESTIONS_PROMPT_TEMPLATE = r"""
You are a professional college professor. And you are creating a test paper.
Generate a set of questions that challenge the students' understanding of the given topic.
The questions should be clear, concise, and relevant to the given topics.
Use $...$ to wrap *every* mathematical expression, including equations, formulas, or symbols.
For math or physics related topics, use LaTeX in inline markdown using the $ symbol. For example: $E=mc^2$.
Wrap full LaTeX blocks like matrices in $$...$$.
Example: $$A = \begin{{bmatrix}} 1 & 2 \\ 3 & 4 \end{{bmatrix}}$$
Wrap inline formulas like $a_{{ij}}$ or $x^2 + y^2 = z^2$.
Do not forget to include both dollar signs.
wrap response questions in list of strings, wrap each question in triple quotes.
Respond only with a list of questions of the format:
[["Question1", "Question2", "Question3"]]

Here are the topics:
{topics}
"""

questions_prompt = PromptTemplate.from_template(QUESTIONS_PROMPT_TEMPLATE)

to_list = lambda question_output: question_output.response_content  # noqa: E731

# ---------------------------------------------------------------------------- #
ANSWER_PROMPT_TEMPLATE = r"""
You are a professional college professor. And based on the notes you provided, the students have 
come up with some questions, your job is to provide answers for each question.
The answers should be detailed and well-explained. 
Use $...$ to wrap *every* mathematical expression, including equations, formulas, or symbols.
Use proper markdown formatting where necessary. Use headers, subheader, dividers etc. 
For math or physics related topics, use Latex in inline markdown using the $ symbol. For example: $E=mc^2$.
Wrap full LaTeX blocks like matrices in $$...$$.
Example: $$A = \begin{{bmatrix}} 1 & 2 \\ 3 & 4 \end{{bmatrix}}$$
Wrap inline formulas like $a_{{ij}}$ or $x^2 + y^2 = z^2$.
Do not forget to include both dollar signs.

Here is the question: 
{question}
    """

answer_prompt = PromptTemplate.from_template(ANSWER_PROMPT_TEMPLATE)
# ---------------------------------------------------------------------------- #
QUIZ_PROMPT_TEMPLATE = r"""
You are a college professor tasked with creating a multiple choice question quiz on these topics:
{topic}
The output should be json formatted  like this:

[[
  {{
    "question": "If a train travels 120 miles in 2 hours, what is its average speed?",
    "extra_content": "", #Optional content: more context to the question
    "image_link": "", #Optional content: image associated with question
    "options": {{
      "60 mph": true, #true if the option is correct false otherwise
      "40 mph": false,
      "100 mph": false,
      "240 mph": false
    }}
  }},
  
  and so on..
  
]]
"""
quiz_prompt = PromptTemplate.from_template(QUIZ_PROMPT_TEMPLATE)


def process(x: list) -> list:
    return list(map(dict, x))
to_quiz_questions = lambda x: process(x.response_content)  # noqa: E731

# ---------------------------------- Chains ---------------------------------- #
questions_chain = questions_prompt | model_questions | to_list
quiz_chain = quiz_prompt | model_quiz | to_quiz_questions

output_parser = StrOutputParser()
notes_chain = notes_prompt | model | output_parser
answer_chain = answer_prompt | model | output_parser
# ----------------------------------- Main UI ----------------------------------- #

st.write_stream(streamer("# Notes-LM", speed=0.05))
st.session_state.user_input = st.text_area("Enter topics here")


if st.session_state.user_input != "":
    con = st.container(border=True)

    con.write_stream(streamer("Thinking...", speed=0.05))
    con.write_stream(
        notes_chain.stream({"topics": st.session_state.user_input}),
    )

    st.divider()

    @st.cache_data
    def cache_questions() -> list[str]:
        return questions_chain.invoke({"topics": st.session_state.user_input})
    
    def generate_qna() -> None:
        questions = cache_questions()[1::]

        for ques in questions:
            with st.chat_message("user"):
                st.write_stream(streamer(ques, speed=0.005))

            with st.chat_message("assistant"):
                con = st.container(border=True)

                con.write_stream(answer_chain.stream({"question": ques}))

                st.divider()


    @st.cache_data
    def generate_quiz() -> None:
        st.session_state.quiz_questions = quiz_chain.invoke(
            {"topic": st.session_state.user_input}
        )
        
# ---------------------------------- BUTTONS --------------------------------- #
    with st.sidebar():
        if st.button("Generate QnA"):
            generate_qna()
        if st.button("Generate Quiz"):
            generate_quiz()
        

else:
    st.write("""Please enter some topics to get started.
             Enter comma separated topics for better results.""")

# ------------------------------------ End ----------------------------------- #
