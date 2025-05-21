# Chapter 7: Question Generation

Welcome back! In our journey through the `Python-AI-apps` project, we've built the [Streamlit Application Structure](01_streamlit_application_structure_.md) (Chapter 1), loaded and processed [Data Loading and Context](02_data_loading_and_context_.md) (Chapter 2), created the interactive [Chat Interface and Flow](03_chat_interface_and_flow_.md) (Chapter 3), learned how [Streamlit Session State](04_streamlit_session_state_.md) (Chapter 4) keeps everything remembered, handled [Ollama Model Interaction](05_ollama_model_interaction_.md) (Chapter 5) to talk to the AI, and enabled [Code Execution](06_code_execution_.md) (Chapter 6) to run the AI's generated code.

Now, think about the user who has just uploaded their data but isn't sure where to start. They see the chat box but might feel stuck. What kind of questions *can* they even ask about this specific dataset? This is where **Question Generation** comes in.

## What Problem Does Question Generation Solve?

The core problem is user onboarding and guidance. A user might upload a dataset with columns like 'CustomerID', 'Product', 'Price', 'Date', 'City', etc., but not immediately know what meaningful questions to ask the AI about it.

Question generation solves this by having the AI look at the *type* of data you uploaded and come up with relevant, interesting questions *for that specific dataset*. It's like having a friendly data expert look at your spreadsheet and say, "Hey, you could ask about the average price, or maybe the total sales per city, or the most popular products!"

The main use case is **providing helpful, dataset-specific question suggestions to the user**, making it easier for them to start exploring their data with the chatbot. These suggestions appear as clickable buttons just above the chat input.

## Key Concepts

To generate these helpful questions, we need to:

1.  **Leverage Data Context:** Use the information about the dataset (like column names and types) that we extracted in [Chapter 2: Data Loading and Context](02_data_loading_and_context_.md) and stored in [Streamlit Session State](04_streamlit_session_state_.md).
2.  **Ask the AI (Again!):** Make *another* call to the AI model, but this time, the instruction is specifically to generate a *list of questions* based on the provided context. This is different from the main chat interaction where we ask the AI to *answer* a question and generate code.
3.  **Parse the AI's Response:** The AI will return a text response that contains the list of questions. We need to extract this list string and convert it into a proper Python list.
4.  **Store and Manage Questions:** Keep the list of generated questions available throughout the user session using [Streamlit Session State](04_streamlit_session_state_.md). We'll also shuffle it to keep the button suggestions fresh.
5.  **Display as Buttons:** Use Streamlit components to show the top few questions as clickable buttons (as introduced in [Chapter 3: Chat Interface and Flow](03_chat_interface_and_flow_.md)).

Let's see how the app implements this using the `get_questions` function.

## How it Works: The `get_questions` Function

The logic for generating questions is encapsulated in the `get_questions` function located in `utils/functions.py`. This function is called early in the `pages/Main.py` script, right after the data and context are loaded.

Here's a simplified look at the function:

```python
# --- File: DATARS-AI-Chatbot/utils/functions.py ---
# ... (other imports) ...
import ollama # To call the AI model
import streamlit as st # To access session state
import re # To find the list string
import ast # To safely convert string list to Python list

# Use caching to avoid generating questions repeatedly if context doesn't change
@st.cache_data
def get_questions() -> list[str]:
    """
    Generates a list of suggested questions based on the dataset context.
    """
    # 1. Get context from session state
    context = st.session_state['context']

    # 2. Construct the prompt for the AI
    prompt = f"""Based on the following info extracted from a data set, write interesting questions
    a data analyst can plot, present your output only in the following format:
    ['Question1', 'Question2', 'Question3', ...]
    also do not use apostrophes in the output.
    eg: ['What is the average age of customers?', 'How many unique products are sold?']

    Data Name: {context["file_name"]}
    Numerical Columns: {context["numerical_columns"]}
    Categorical Columns: {context["categorical_columns"]}
    """

    # 3. Call the AI model specifically for questions
    # Note: We use callOllama here, which waits for the full response,
    # unlike get_ollama_stream used for the main chat.
    response = callOllama(prompt, model="gemma3") # Use a different, maybe faster model

    # 4. Find the list string in the response
    match = re.search(r"\[(?:'[^']*'(?:,\s*)?)*\]", response)

    # 5. Safely convert the string list to a Python list
    if match:
        list_str = match.group(0) # Get the matched string, e.g., "['Q1', 'Q2']"
        try:
            # ast.literal_eval is safer than eval() for simple Python literals
            question_list = ast.literal_eval(list_str)
            return question_list
        except (ValueError, SyntaxError):
            # Handle cases where the AI didn't return a valid list format
            st.error("Could not parse questions from AI response.")
            return [] # Return empty list if parsing fails

    # Return empty list if no list pattern was found
    return []

# The callOllama function (simplified, from utils/functions.py)
# Used here to get the full response needed for parsing the list
def callOllama(prompt: str, model: str = "gemma3") -> str:
    """
    Sends a chat prompt to the Ollama API and retrieves the full response.
    (Unlike get_ollama_stream which streams)
    """
    # Uses ollama.chat but without stream=True
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response.get("message", {}).get("content", "No response.")

# ... (other functions) ...
```
*Simplified Code from `DATARS-AI-Chatbot/utils/functions.py`*

Let's break down these steps:

1.  **Get Context:** The function starts by retrieving the `context` dictionary from [Streamlit Session State](04_streamlit_session_state_.md). This context, generated in [Chapter 2](02_data_loading_and_context_.md), contains the crucial information about the columns in the uploaded DataFrame.
    ```python
    context = st.session_state['context']
    ```
2.  **Construct the Prompt:** A detailed prompt is created using an f-string. This prompt instructs the AI to act as a data analyst and generate questions *based on the provided context*. It specifically asks for the output to be in the format of a Python list string (e.g., `['Question1', 'Question2']`) and gives examples. This structured request helps guide the AI to produce output that the app can easily parse.
    ```python
    prompt = f"""Based on the following info extracted from a data set, write interesting questions ... format:
    ['Question1', 'Question2', ...]
    ...
    Data Name: {context["file_name"]}
    Numerical Columns: {context["numerical_columns"]}
    Categorical Columns: {context["categorical_columns"]}
    """
    ```
3.  **Call the AI:** The `callOllama` function is used here. Unlike `get_ollama_stream` (from [Chapter 5](05_ollama_model_interaction_.md)) which streams, `callOllama` waits for the *entire* AI response to be ready before returning it as a single string. This is necessary because we need the complete list string before we can parse it. A potentially smaller/faster model like "gemma3" might be chosen for this task as it's a simpler request than analyzing data.
    ```python
    response = callOllama(prompt, model="gemma3")
    ```
4.  **Find the List String:** The AI's response might contain introductory text or explanations before or after the list. We need to find the exact string that looks like a Python list. A regular expression (`re.search`) is used to locate the pattern that matches a list starting with `[` and ending with `]` containing quoted strings.
    ```python
    match = re.search(r"\[(?:'[^']*'(?:,\s*)?)*\]", response)
    ```
    *   `\[` and `\]`: Match the literal square brackets.
    *   `(?: ... )`: A non-capturing group for repeating items.
    *   `'[^']*'`: Matches a single quote, followed by any character *except* a single quote (`[^']*`) zero or more times, followed by a closing single quote. This captures the question string.
    *   `(?:,\s*)?`: Optionally matches a comma and any whitespace after a question.
    *   `*`: Repeats the preceding group (a quoted string followed by an optional comma/whitespace) zero or more times.
    *   This regex tries to find something that looks like `['...', '...']`.
    *   If a match is found, `match.group(0)` gives us the full matched string (e.g., `['What is the average age?', 'Total sales?']`).

5.  **Safely Convert to List:** Once the list string is extracted, we need to convert it into an actual Python list object. We use `ast.literal_eval()` for this. `ast.literal_eval` is a function from Python's `ast` (Abstract Syntax Trees) module. It's much safer than the standard `eval()` function because it can *only* evaluate simple Python literal expressions (like strings, numbers, tuples, lists, dicts, booleans, and None). It cannot execute arbitrary code, which is important when evaluating input from an external source like an AI.
    ```python
    if match:
        list_str = match.group(0)
        try:
            question_list = ast.literal_eval(list_str) # Convert string to list
            return question_list # Return the list
        except (ValueError, SyntaxError):
            # If the string wasn't actually a valid Python list literal
            st.error("Could not parse questions from AI response.")
            return [] # Return empty list
    # ...
    return [] # Return empty list if no list pattern found at all
    ```
    A `try...except` block is used here to catch errors that might occur if the regex found *something* that looked *a bit* like a list, but wasn't valid Python syntax for `ast.literal_eval`.

The `@st.cache_data` decorator ensures that this potentially slow AI call only happens once for a given dataset context. If the user uploads a new file, the context changes, the cache is invalidated, and `get_questions` runs again.

## Using the Generated Questions

Once `get_questions()` returns the list of strings, this list is stored in [Streamlit Session State](04_streamlit_session_state_.md) under the key `"questions"` in the `pages/Main.py` file.

```python
# --- File: DATARS-AI-Chatbot/pages/Main.py ---
# ... (imports and status checks) ...

st.title("DATARS - AI")
if st.session_state["df"] is not None: # Check if data is loaded
    with st.status("Loading", expanded=True) as status:
        # ... (Ollama status check) ...

        # If context is not loaded, get it (from Chapter 2)
        if st.session_state["context"] is None:
            st.session_state["context"] = get_context()
            st.write("Context loaded")

        # If questions are not loaded, get them using the function
        if st.session_state["questions"] is None:
            st.session_state["questions"] = get_questions() # Calls the function!
            st.write("Questions loaded")

        status.update(label="Loading complete!", state="complete", expanded=False)

    # ... (Rest of chat interface code) ...

    # ------------------------- Render suggestion buttons ------------------------ #
    def render_buttons() -> None:
        """
        Function to render the three question buttons above the chat input
        """
        # Get the first 3 questions from the list stored in session state
        q1, q2, q3 = st.session_state["questions"][:3]

        # Create columns and buttons (as shown in Chapter 3)
        left, mid, right = st.columns([1, 1, 1])
        if left.button(q1, key=f"left_{q1}"):
            st.session_state.user_input = q1
        if mid.button(q2, key=f"mid_{q2}"):
            st.session_state.user_input = q2
        if right.button(q3, key=f"right_{q3}"):
            st.session_state.user_input = q3
        return None

    # ... (Show history, chat input, enter function) ...

    def enter(prompt):
        # ... (Display user message, call get_ollama_stream, stream response, execute) ...

        # After a conversation turn is complete, shuffle the questions list
        rd.shuffle(st.session_state.questions) # Shuffles the list in session state

        # ... (Clear user_input, st.rerun) ...

    # ... (Call enter function if needed) ...

# ... (Else block for no data) ...
```
*Simplified Code from `pages/Main.py`*

Here's how the generated questions are used:

1.  **Initial Load:** When the `pages/Main.py` script runs for the first time after data upload (and `st.session_state["questions"]` is `None`), `get_questions()` is called, and the resulting list is stored in `st.session_state["questions"]`. This happens inside the `st.status` block for user feedback.
2.  **Displaying Buttons:** The `render_buttons()` function (called after the history display) accesses `st.session_state["questions"]` and takes the *first three* questions from the list (`[:3]`) to display on the buttons.
3.  **Shuffling:** Inside the `enter()` function (which runs after *every* AI interaction), `rd.shuffle(st.session_state.questions)` is called. This shuffles the *entire list* of questions stored in session state. Because the list is shuffled, the *next* time `render_buttons()` is called (which happens on the subsequent rerun triggered by `st.rerun()`), it will pick three *different* questions from the top of the now-shuffled list.

This provides a fresh set of suggestions after each user interaction, encouraging further exploration of the data.

## How it Works: The Question Generation Flow

Let's visualize the flow for generating and using questions.

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Streamlit
    participant MainPagePy [pages/Main.py]
    participant SessionState [Session State]
    participant Functions [utils/functions.py]
    participant OllamaLib [ollama library]
    participant OllamaServer [Ollama Service]

    User->>Browser: Uploads file
    Browser->>Streamlit: Triggers rerun
    Streamlit->>MainPagePy: Executes pages/Main.py (Rerun 1)

    Note over MainPagePy: Data is loaded; context is generated and stored in Session State

    MainPagePy->>MainPagePy: Checks if st.session_state["questions"] is None
    alt questions is None
        MainPagePy->>Functions: Calls get_questions()
        Functions->>SessionState: Reads st.session_state["context"]
        Functions->>Functions: Crafts prompt
        Functions->>Functions: Calls callOllama(prompt)
        Functions->>OllamaLib: Calls ollama.chat() (not streamed)
        OllamaLib->>OllamaServer: Sends API request
        OllamaServer-->>OllamaLib: Sends full response string
        OllamaLib-->>Functions: Returns full response
        Functions->>Functions: Uses re.search() to find list string
        Functions->>Functions: Uses ast.literal_eval() to convert string to list
        Functions-->>SessionState: Stores resulting list (st.session_state["questions"])
        Functions-->>MainPagePy: Returns the list (cached)
    end

    MainPagePy->>MainPagePy: Calls render_buttons()
    MainPagePy->>SessionState: Reads st.session_state["questions"]
    MainPagePy->>MainPagePy: Selects first 3 questions
    MainPagePy->>Browser: Sends UI with 3 question buttons

    Browser->>User: Sees the buttons
```

This diagram shows that question generation is a one-time process triggered when data is first loaded and there are no questions in session state. It uses the data context to ask the AI for suggestions, parses the AI's specific response format, and stores the list persistently. This stored list is then used whenever the buttons are rendered.

After a user interacts with the chat, the `enter` function shuffles the list in session state, so the *next* time `render_buttons` runs (after the `st.rerun()` call), it will display a different set of three questions from the shuffled list.

## Summary

In this chapter, we learned how our app generates helpful question suggestions:

*   It uses the dataset context stored in [Streamlit Session State](04_streamlit_session_state_.md) to inform the AI.
*   It makes a dedicated call to the AI model using the `callOllama` function (different from the streaming chat function), with a prompt specifically asking for a list of questions.
*   It uses Python's `re` module to find the string representation of a list within the AI's response.
*   It uses Python's `ast.literal_eval` to safely convert this string into a usable Python list of questions.
*   The generated list is stored in [Streamlit Session State](04_streamlit_session_state_.md) (`st.session_state["questions"]`) and cached using `@st.cache_data` to avoid regenerating it unnecessarily.
*   The `render_buttons` function in `pages/Main.py` reads the first three questions from this list to display as clickable suggestions.
*   After each chat interaction, the list in session state is shuffled (`rd.shuffle`) to provide variety in the button suggestions.

With question generation, data loading, context handling, AI interaction, code execution, persistent session state, and a responsive chat interface, our AI data assistant application is now fully functional!

This concludes the main tutorial chapters for the `Python-AI-apps` project. You now have a solid understanding of the core components and how they work together to create this interactive data analysis tool powered by local AI.

Where to go next? You could explore modifying the prompts sent to the AI (`get_ollama_stream` and `get_questions`) to see how it affects the responses, experiment with different Ollama models, or enhance the Streamlit interface further!

---