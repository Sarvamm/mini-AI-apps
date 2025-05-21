# Chapter 5: Ollama Model Interaction

Welcome back! We've covered the basic [Streamlit Application Structure](01_streamlit_application_structure_.md) (Chapter 1), learned how to handle [Data Loading and Context](02_data_loading_and_context_.md) (Chapter 2) using Pandas and Streamlit's caching, understood how the [Chat Interface and Flow](03_chat_interface_and_flow_.md) works to display messages and capture user input, and explored how [Streamlit Session State](04_streamlit_session_state_.md) keeps everything persistent across reruns.

Now, it's time for the most exciting part: actually talking to the AI model! This chapter dives into the code that handles the communication with **Ollama**, the local AI platform powering our data analyst assistant.

## What Problem Does Ollama Interaction Solve?

Think of the AI model as the expert data analyst we mentioned before. It has the knowledge to understand questions about data and generate insights or code. But it lives separately from our Streamlit app. We need a way for our app to:

1.  **Know if the expert is available:** Is the Ollama service running?
2.  **Call the expert:** Send the user's question and the data context to Ollama.
3.  **Listen to the expert:** Receive the answer back from Ollama.

This chapter explains how our app uses specific functions to perform these communication tasks, allowing the AI's responses to appear in the chat interface we built in [Chapter 3: Chat Interface and Flow](03_chat_interface_and_flow_.md). The main use case we're addressing is getting the AI's step-by-step response displayed as you wait.

## Key Concepts

To interact with Ollama, we rely on a few key ideas and tools:

*   **Ollama Service:** This is the background process running on your computer (or a server) that hosts the AI models. Our app needs to connect to it, usually over a local network address (like `http://localhost:11434`).
*   **Ollama Python Library:** A convenient Python library that makes it easy to send requests to the Ollama service instead of building raw HTTP requests ourselves.
*   **Prompt Engineering:** Crafting the right instructions (the "prompt") to send to the AI. This includes the user's question PLUS important context about the data from [Chapter 2: Data Loading and Context](02_data_loading_and_context_.md).
*   **Streaming:** Getting the AI's response back piece by piece as it's being generated, rather than waiting for the entire answer. This makes the chat experience feel much faster and more dynamic.

Our app uses functions defined in `utils/functions.py` to manage these interactions.

## Checking and Starting Ollama

Before we can talk to the AI model, we need to make sure the Ollama service is running. The app does this check when it first starts up in `App.py`.

First, a function to check the status:

```python
# --- File: DATARS-AI-Chatbot/utils/functions.py ---
import requests # Need this to make web requests

def is_ollama_running() -> bool:
    """
    Check if ollama is running by trying to connect to its default address.
    Returns: True if it is, False otherwise.
    """
    try:
        # Attempt to make a small request to the Ollama API endpoint
        response = requests.get("http://localhost:11434", timeout=2)
        # If we get a 200 OK status, it's running
        return response.status_code == 200
    except requests.exceptions.RequestException:
        # If connection fails or times out, it's not running
        return False

# ... other functions ...
```
*Code from `DATARS-AI-Chatbot/utils/functions.py` (simplified)*

*   This function uses the `requests` library to try and connect to the standard address where Ollama runs (`http://localhost:11434`).
*   If the connection is successful and returns a 200 status code, the function knows Ollama is ready (`True`).
*   If there's an error (like connection refused or timeout), it assumes Ollama is not running (`False`).

If Ollama isn't running, the app tries to start it:

```python
# --- File: DATARS-AI-Chatbot/utils/functions.py ---
import subprocess # Needed to run external commands
import time # Needed to pause briefly
import streamlit as st # Needed to update session state

def start_ollama() -> None | str:
    """
    Try to start the ollama service using a subprocess command.
    Updates Streamlit session state on success.
    Returns: None on success, an error string on failure.
    """
    try:
        # Run the 'ollama serve' command in the background
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL, # Ignore standard output
            stderr=subprocess.DEVNULL # Ignore standard error
        )

        # Give Ollama a few seconds to start up
        time.sleep(3)
        # If it gets here, assume success and update status in session state
        st.session_state.status = "Online"
        return None # Indicate success
    except Exception as e:
        # If there's an error running the command, return error message
        return "Failed to start Ollama:" + str(e)

# ... other functions ...
```
*Code from `DATARS-AI-Chatbot/utils/functions.py` (simplified)*

*   This function uses Python's `subprocess` module to run the command `ollama serve` just like you would in your terminal.
*   `subprocess.Popen` starts the command without waiting for it to finish, allowing the app to continue.
*   `stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL` prevent any output from the `ollama serve` command from cluttering the app's console.
*   `time.sleep(3)` adds a short pause to give the Ollama service time to initialize before the app tries to connect.
*   If successful, it updates the `"status"` variable in [Streamlit Session State](04_streamlit_session_state_.md) to "Online", which is used in `App.py` to show a success message in the sidebar.

These two functions are called in `App.py` at the very beginning, powered by [Streamlit Session State](04_streamlit_session_state_.md) to remember the status:

```python
# --- File: DATARS-AI-Chatbot/App.py ---
# ... (imports) ...
from utils.functions import is_ollama_running, start_ollama # Import the functions

# Initializing session state for status
if "status" not in st.session_state:
    st.session_state["status"] = "Offline"

# Check and potentially start Ollama when the app first loads
if not is_ollama_running():
    start_ollama()
    # Check status again after attempting to start
    if st.session_state["status"] == "Online":
        st.sidebar.success("ollama is running")
    # Note: If start_ollama fails, the status remains "Offline"

# ... (rest of App.py) ...
```
*Code from `DATARS-AI-Chatbot/App.py` (simplified)*

This ensures that if Ollama isn't running when the app starts, it attempts to launch it and updates the status displayed in the sidebar.

## Sending Prompts and Getting the Stream

The core interaction happens when the user asks a question in the chat. As we saw in [Chapter 3: Chat Interface and Flow](03_chat_interface_and_flow_.md), this triggers the `enter` function in `pages/Main.py`, which in turn calls `get_ollama_stream`.

This is the function that packages the question and context into a prompt and sends it to Ollama:

```python
# --- File: DATARS-AI-Chatbot/utils/functions.py ---
import ollama # Need this library to talk to Ollama API
import streamlit as st # Need this to access session state

def get_ollama_stream(
    user_prompt: str, model: str = "qwen2.5-coder:7b"
) -> Generator[str, None, None]: # This indicates it 'yields' strings
    """
    Sends the user prompt + data context to Ollama and streams the response.
    """
    # --- 1. Construct the full prompt ---
    # Get context from session state (loaded in Chapter 2 & 4)
    context = st.session_state['context']

    # Create a detailed instruction prompt including the context
    prompt = f'''You are a data analyst assistant working on a with the following columns:
{context['columns']} # Details about columns
Out of which, numerical columns are:
{context['numerical_columns']} # Numerical column names
and Categorical columns are:
{context['categorical_columns']} # Categorical column names
columns data types are:
{context['dtypes']} # Data types of columns

The data frame is loaded in the variable df. # Tell the AI the variable name
You will be provided a question related to the data frame.
Your task is to answer the question using Python code.
First decide whether the question requires a plot or not.
- If yes, plot it using Plotly Express in Streamlit.
- If no, use pandas methods and display answers using st.write().
Use single quotes for st.write().
Respond only with executable Python code blocks that can run inside exec().
Question:
{user_prompt}''' # The actual user question

    # --- 2. Call Ollama API and stream the response ---
    # Use the ollama library to chat with the specified model
    # stream=True is key here - it tells Ollama to send response piece-by-piece
    for chunk in ollama.chat(
        model=model, messages=[{"role": "user", "content": prompt}], stream=True
    ):
        # Each 'chunk' is a small part of the response
        # We 'yield' the content of the message from this chunk
        yield chunk["message"]["content"]

# ... other functions ...
```
*Code from `DATARS-AI-Chatbot/utils/functions.py` (simplified)*

Let's break down the important parts:

1.  **Accessing Context:** It retrieves the `context` dictionary from [Streamlit Session State](04_streamlit_session_state_.md). This dictionary was created in [Chapter 2: Data Loading and Context](02_data_loading_and_context_.md) and holds the crucial information about the uploaded data.
2.  **Constructing the Prompt:** An f-string is used to build the complete prompt sent to the AI. This prompt includes:
    *   Instructions on *what* the AI should be (a data analyst assistant).
    *   Detailed information about the data (column names, types) pulled directly from the `context` dictionary. This is crucial for the AI to understand the data it's working with.
    *   Instructions on the expected output format (Python code, how to plot, how to display results).
    *   The user's actual question (`user_prompt`).
3.  **Calling `ollama.chat`:** The `ollama.chat` function from the `ollama` library is called.
    *   `model="qwen2.5-coder:7b"` specifies which AI model to use (this can be changed).
    *   `messages=[{"role": "user", "content": prompt}]` provides the conversation history. In this case, it's just one message: the system instruction + user question combined in our crafted `prompt`.
    *   **`stream=True`**: This is vital! It tells the Ollama service *not* to wait until it has the full answer. Instead, it should send parts of the answer as soon as they are ready.
4.  **Yielding Chunks:** Because `stream=True` is used, `ollama.chat` doesn't return a single response. It returns an *iterator*. We loop through this iterator (`for chunk in ollama.chat(...)`). In each iteration, `chunk` contains a small piece of the AI's response.
    *   `yield chunk["message"]["content"]`: Instead of collecting all chunks into a single variable, the `yield` keyword means this function is a **generator**. Every time `yield` is encountered, the function pauses, sends the specified value (`chunk["message"]["content"]`) back to the caller (`pages/Main.py`), and remembers where it left off. The next time the caller asks for a value, the function resumes from that point. This is how we achieve the "streaming" effect in the UI.

Back in `pages/Main.py` (as seen in [Chapter 3](03_chat_interface_and_flow_.md)), the `enter` function receives this generator and uses `st.write_stream` to display the content chunk by chunk:

```python
# --- File: DATARS-AI-Chatbot/pages/Main.py ---
# ... (imports) ...
from utils.functions import get_ollama_stream # Import the function

def enter(prompt):
    # ... (display user message, add to history) ...

    # Call the function to get the AI's response stream
    stream = get_ollama_stream(prompt)

    # Display assistant message and stream response in the UI
    with st.chat_message("assistant"):
        # st.write_stream takes the generator and displays yielded chunks
        # It also returns the complete response string when done
        response = st.write_stream(stream)

    # ... (add assistant message to history, execute code, rerun) ...
```
*Code from `DATARS-AI-Chatbot/pages/Main.py` (simplified)*

`st.write_stream` is the Streamlit component designed specifically to work with generators like the one returned by `get_ollama_stream`. It continuously updates the text in the chat bubble as new chunks are yielded, creating the smooth streaming effect.

## How it Works: The Streaming Flow

Let's visualize the key steps when the user asks a question and the AI streams its response.

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Streamlit
    participant MainPagePy [pages/Main.py]
    participant Functions [utils/functions.py]
    participant OllamaLib [ollama library]
    participant OllamaServer [Ollama Service]

    User->>Browser: Types question / Clicks button
    Browser->>Streamlit: Sends action (triggers rerun)
    Streamlit->>MainPagePy: Executes pages/Main.py (rerun 1)

    Note over MainPagePy: user_input is detected; enter() is called

    MainPagePy->>Browser: Displays User message
    MainPagePy->>Functions: Calls get_ollama_stream(prompt)

    Functions->>OllamaLib: Calls ollama.chat(..., stream=True)
    OllamaLib->>OllamaServer: Sends API request with prompt

    OllamaServer-->>OllamaLib: Sends first chunk of response
    OllamaLib-->>Functions: Yields first chunk

    Functions-->>MainPagePy: Returns first chunk (via generator)

    Note over Streamlit: Streamlit detects yielded data

    Streamlit->>Browser: Displays first chunk in Assistant bubble
    Browser->>User: Sees first part of AI response appear

    OllamaServer-->>OllamaLib: Sends next chunk
    OllamaLib-->>Functions: Yields next chunk
    Functions-->>MainPagePy: Returns next chunk

    Note over Streamlit: Streamlit detects yielded data

    Streamlit->>Browser: Displays next chunk (appends to bubble)
    Browser->>User: Sees more text appear

    Note over OllamaServer,OllamaLib,Functions,MainPagePy: ... continues streaming chunks ...

    OllamaServer-->>OllamaLib: Sends final chunk (end of stream)
    OllamaLib-->>Functions: Yields final chunk
    Functions-->>MainPagePy: Returns final chunk + signals end of stream

    Note over Streamlit: Streamlit detects end of stream

    Streamlit->>Browser: Displays final chunk & completes Assistant bubble
    MainPagePy->>MainPagePy: st.write_stream() returns complete response
    MainPagePy->>SessionState: Adds complete response to history
    MainPagePy->>MainPagePy: Calls execute() (Next Chapter)
    MainPagePy->>Streamlit: Calls st.rerun() (rerun 2)

    Streamlit->>MainPagePy: Executes pages/Main.py (rerun 2)

    Note over MainPagePy: Renders full history, clears input, shuffles buttons
    Streamlit->>Browser: Updates UI

    Browser->>User: Sees final state (full response, charts, cleared input)
```

This diagram shows how `get_ollama_stream` acts as a bridge, using the `ollama` library to send the prompt to the Ollama service and then *yielding* the response chunks back to `pages/Main.py`, which uses `st.write_stream` to show them live in the browser. The process finishes with saving the complete response and triggering another rerun to finalize the UI state.

## Summary

In this chapter, we learned how our app interacts with the Ollama AI model:

*   Functions like `is_ollama_running` and `start_ollama` in `utils/functions.py` are used by `App.py` to check and potentially launch the Ollama service at startup.
*   The core interaction function, `get_ollama_stream` (in `utils/functions.py`), is called from `pages/Main.py` when a user asks a question.
*   `get_ollama_stream` accesses the data context from [Streamlit Session State](04_streamlit_session_state_.md) to build a detailed prompt that includes information about the user's data.
*   It uses the `ollama` Python library to send this prompt to the Ollama service with the `stream=True` option.
*   It acts as a generator, using `yield` to send chunks of the AI's response back as they are received.
*   Back in `pages/Main.py`, `st.write_stream` receives these chunks and displays the AI's response piece by piece in the chat interface, providing a dynamic user experience.

Now that we know how the app gets the AI's response, which often contains Python code, the next step is to understand how that code is extracted and run to produce charts or calculations. Let's explore [Code Execution](06_code_execution_.md) in the next chapter.

[Chapter 6: Code Execution](06_code_execution_.md)

---