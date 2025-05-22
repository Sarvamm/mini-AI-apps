# ---------------------------------------------------------------------------- #
#                                    IMPORTS                                   #
# ---------------------------------------------------------------------------- #
import ollama
import streamlit as st
import requests
import subprocess
import time
from typing import Generator
import re
import ast

# ---------------------------------------------------------------------------- #
#                               F U N C T I O N S                              #
# ---------------------------------------------------------------------------- #


def is_ollama_running() -> bool:
    """_summary_
    Check if ollama is running or not
    Returns:
        bool: True if it is, False in any other case.
    """
    try:
        response = requests.get("http://localhost:11434", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


# ---------------------------------------------------------------------------- #


def start_ollama() -> None | str:
    """_summary_
    Try to start ollama.
    Returns:
        None | str: _description_
    """
    try:
        subprocess.Popen(
            ["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        time.sleep(3)
        st.session_state.status = "Online"
        return None
    except Exception as e:
        return "Failed to start Ollama:" + str(e)


# ---------------------------------------------------------------------------- #


def get_ollama_stream(
    user_prompt: str, model: str = "qwen2.5-coder:7b"
) -> Generator[str, None, None]:
    """
    Generates a stream of responses from the Ollama chat model based on the provided prompt.

    Args:
        prompt (str): The input prompt to be sent to the Ollama chat model.

    Yields:
        str: A chunk of the response content from the Ollama chat model.

    Notes:
        - The function uses the "qwen2.5-coder:7b" model for generating responses.
        - Responses are streamed in chunks, and each chunk's content is yielded.
    """

    prompt = f"""You are a data analyst assistant working on a with the following columns:
{st.session_state["context"]["columns"]}

Out of which, numerical columns are:
{st.session_state["context"]["numerical_columns"]}

and Categorical columns are:
{st.session_state["context"]["categorical_columns"]}

columns data types are:
{st.session_state["context"]["dtypes"]}


The data frame is loaded in the variable df.
You will be provided a question related to the data frame.
Your task is to answer the question using Python code.
First decide whether the question requires a plot or not.
- If yes, plot it using Plotly Express in Streamlit.
- If no, use pandas methods and display answers using st.write().
Use single quotes for st.write().
Respond only with executable Python code blocks that can run inside exec().
Question:
{user_prompt}"""

    for chunk in ollama.chat(
        model=model, messages=[{"role": "user", "content": prompt}], stream=True
    ):
        yield chunk["message"]["content"]


# ---------------------------------------------------------------------------- #


def callOllama(prompt: str, model: str = "gemma3") -> str:
    """
    Sends a chat prompt to the Ollama API and retrieves the response.
    Args:
        prompt (str): The input message or query to send to the Ollama model.
        model (str, optional): The name of the model to use for the chat. Defaults to "gemma3".
    Returns:
        str: The content of the response message from the Ollama model.
                If no response is received, returns "No response.".
    """

    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response.get("message", {}).get("content", "No response.")


# ---------------------------------------------------------------------------- #


@st.cache_data
def get_context() -> dict:
    """
    Retrieve and cache the context information of a DataFrame stored in the session state.
    This function extracts metadata from a DataFrame, such as column names, numerical
    columns, categorical columns, and data types, and returns it as a dictionary. The
    function is cached to optimize performance.
    Returns:
        dict: A dictionary containing the following keys:
            - "file_name" (str): The name of the file associated with the DataFrame.
            - "columns" (list): A list of all column names in the DataFrame.
            - "numerical_columns" (list): A list of column names with numerical data types.
            - "categorical_columns" (list): A list of column names with non-numerical data types.
            - "dtypes" (pandas.Series): A Series object containing the data types of each column.
    """
    df = st.session_state["df"]
    file_name = st.session_state["file_name"]
    columns = str(df.columns.tolist())
    numerical_columns = str(df.select_dtypes(include=["number"]).columns.tolist())
    categorical_columns = str(df.select_dtypes(exclude=["number"]).columns.tolist())
    dtypes = str(df.dtypes.to_dict())

    context = {
        "file_name": file_name,
        "columns": columns,
        "numerical_columns": numerical_columns,
        "categorical_columns": categorical_columns,
        "dtypes": dtypes,
    }
    return context


# ---------------------------------------------------------------------------- #


@st.cache_data
def get_questions() -> list[str]:
    """
    Generates a list of 15+ questions that a data analyst can plot based on the provided dataset context.

    Returns:
        list[str]: A list of questions generated by the language model, e.g.,
                   ['What is the average age of customers?', 'How many unique products are sold?']

    """
    prompt = f"""Based on the following info extracted from a data set, write interesting questions 
    a data analyst can plot, present your output only in the following format:
    ['Question1', 'Question2', 'Question3']
    also do not use apostrophes in the output.
    eg: ['What is the average age of customers?', 'How many unique products are sold?', 'Correlation between attendance and exam score?']
    
    Data Name: {st.session_state["context"]["file_name"]}
    Numerical Columns: {st.session_state["context"]["numerical_columns"]}
    Categorical Columns: {st.session_state["context"]["categorical_columns"]} 
    """

    response = callOllama(prompt, model="gemma3")

    match = re.search(r"\[(?:'[^']*'(?:,\s*)?)*\]", response)
    if match:
        list_str = match.group(0)
        try:
            question_list = ast.literal_eval(list_str)
            return question_list
        except (ValueError, SyntaxError):
            return []


# ---------------------------------------------------------------------------- #


@st.cache_data
def execute(response: str) -> None:
    """
    Extracts and executes Python code embedded within a response string.

    The function searches for a Python code block within the provided response
    string, extracts the code, and executes it using the `exec` function. If
    an error occurs during execution, it displays the error message.

    Args:
        response (str): The input string containing a Python code block
                        enclosed in triple backticks (```python ... ```).

    Returns:
        None: This function does not return a value.
    """

    match = re.search(r"```python\s*\n(.*?)```", response, re.DOTALL)

    if match:
        code = match.group(1)
        try:
            exec(code, {"df": st.session_state.df, "st": st})
        except Exception as e:
            st.error(f"An error occurred: {e}")


# ------------------------------------ End ----------------------------------- #
