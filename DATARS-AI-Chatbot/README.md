# Datars AI - Chatbot

This project is a **Streamlit application** that allows users to **upload CSV data** and then **chat with it** using an **Ollama AI model**.
It handles loading the data, understanding its structure, interacting with the AI to get answers or code, executing that code to display results or plots, and managing the chat conversation flow, even suggesting questions to get started.


## Visual Overview

```mermaid
flowchart TD
    A0["Streamlit Application Structure
"]
    A1["Streamlit Session State
"]
    A2["Data Loading and Context
"]
    A3["Ollama Model Interaction
"]
    A4["Code Execution
"]
    A5["Chat Interface and Flow
"]
    A6["Question Generation
"]
    A0 -- "Initializes State" --> A1
    A0 -- "Structures Page" --> A5
    A2 -- "Stores Data/Context" --> A1
    A3 -- "Stores Status" --> A1
    A5 -- "Manages Chat History" --> A1
    A5 -- "Sends Prompt" --> A3
    A5 -- "Triggers Code Execution" --> A4
    A6 -- "Uses Ollama" --> A3
    A6 -- "Uses Context" --> A2
    A3 -- "Uses Context" --> A2
```

## Chapters

1. [Streamlit Application Structure
](01_streamlit_application_structure_.md)
2. [Data Loading and Context
](02_data_loading_and_context_.md)
3. [Chat Interface and Flow
](03_chat_interface_and_flow_.md)
4. [Streamlit Session State
](04_streamlit_session_state_.md)
5. [Ollama Model Interaction
](05_ollama_model_interaction_.md)
6. [Code Execution
](06_code_execution_.md)
7. [Question Generation
](07_question_generation_.md)

---

