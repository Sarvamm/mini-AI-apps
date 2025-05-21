import streamlit as st
import os
import tempfile
import uuid
from datetime import datetime
import json
import base64
import requests
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Gemma 3 Chatbot", layout="wide", initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "current_files" not in st.session_state:
    st.session_state.current_files = []

# Ollama API configuration
OLLAMA_API_BASE = "http://localhost:11434/api"
OLLAMA_MODEL = "gemma3"


# Function to save chat history
def save_chat_history():
    history = {
        "session_id": st.session_state.session_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": st.session_state.messages,
    }

    # Create directory if it doesn't exist
    if not os.path.exists("chat_history"):
        os.makedirs("chat_history")

    # Save to a new file with timestamp
    filename = f"chat_history/chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(history, f, indent=4)

    return filename


# Function to get response from Ollama Gemma 3
def get_gemma_response(
    prompt, system_prompt="You are a helpful assistant.", model=OLLAMA_MODEL
):
    try:
        # Prepare the messages in the format Ollama expects
        formatted_messages = []

        # Add system message if provided
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        # Add all previous messages from the conversation
        for msg in st.session_state.messages:
            # Skip messages with files for now
            if "files" in msg and msg["files"]:
                # For messages with files, add text about the files
                file_info = []
                for file_id in msg["files"]:
                    if file_id in st.session_state.uploaded_files:
                        file_data = st.session_state.uploaded_files[file_id]
                        file_info.append(f"{file_data['name']} ({file_data['type']})")

                file_text = ""
                if file_info:
                    file_text = "\n[Attached files: " + ", ".join(file_info) + "]"

                formatted_messages.append(
                    {"role": msg["role"], "content": msg["content"] + file_text}
                )
            else:
                formatted_messages.append(
                    {"role": msg["role"], "content": msg["content"]}
                )

        # Add the current prompt
        formatted_messages.append({"role": "user", "content": prompt})

        # Make the API request to Ollama
        response = requests.post(
            f"{OLLAMA_API_BASE}/chat",
            json={"model": model, "messages": formatted_messages, "stream": False},
        )

        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            return f"Error: Failed to get response from Ollama. Status code: {response.status_code}. Message: {response.text}"

    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"


# Function to handle file upload and storage
def handle_file_upload(file):
    # Create a temporary file to store the uploaded content
    temp_dir = tempfile.gettempdir()
    file_id = str(uuid.uuid4())

    # Store file metadata and path
    file_info = {
        "id": file_id,
        "name": file.name,
        "type": file.type,
        "size": file.size,
        "temp_path": os.path.join(temp_dir, file_id + "_" + file.name),
    }

    # Save the file to temp directory
    with open(file_info["temp_path"], "wb") as f:
        f.write(file.getbuffer())

    # For images, create a description
    if file.type.startswith("image/"):
        try:
            # Open the image
            image = Image.open(file_info["temp_path"])
            # Get basic image info
            width, height = image.size
            format = image.format
            mode = image.mode
            file_info["description"] = f"Image: {width}x{height} {format} {mode}"
        except Exception as e:
            file_info["description"] = f"Image (could not analyze: {str(e)})"

    # Store in session state
    st.session_state.uploaded_files[file_id] = file_info

    return file_info


# Function to get text content from a file
def get_file_content(file_path, file_type, max_length=10000):
    try:
        if file_type.startswith("text/") or file_path.endswith(
            (".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".csv")
        ):
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(max_length)
                if len(content) == max_length:
                    content += "... [content truncated]"
                return content
        else:
            return f"[Binary file: {os.path.basename(file_path)}]"
    except Exception as e:
        return f"[Error reading file: {str(e)}]"


# Function to download chat history
def get_download_link(filename):
    with open(filename, "r") as f:
        data = f.read()
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="{os.path.basename(filename)}">Download chat history</a>'
    return href


# Check if Ollama is available
def check_ollama_availability():
    try:
        response = requests.get(f"{OLLAMA_API_BASE}/tags")
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Ollama returned status code {response.status_code}"
    except Exception as e:
        return False, str(e)


# Callback for clear chat button
def clear_chat():
    st.session_state.messages = []
    st.session_state.uploaded_files = {}
    st.session_state.current_files = []


# Callback for loading chat history
def load_chat_history(selected_file):
    if os.path.exists(os.path.join("chat_history", selected_file)):
        with open(os.path.join("chat_history", selected_file), "r") as f:
            loaded_history = json.load(f)
            st.session_state.messages = loaded_history["messages"]


# Function to handle sending a message
def send_message(message, files=None):
    if not message:
        return

    # Add user message to chat history
    user_message_data = {
        "role": "user",
        "content": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Attach files if any were uploaded
    if files:
        user_message_data["files"] = files

    st.session_state.messages.append(user_message_data)

    # Create a message that includes file content for the AI
    ai_message = message

    # Add file content to the message for text files
    if files:
        file_contents = []
        for file_id in files:
            if file_id in st.session_state.uploaded_files:
                file_info = st.session_state.uploaded_files[file_id]

                # For text files, include the content
                if file_info["type"].startswith("text/") or file_info["name"].endswith(
                    (".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".csv")
                ):
                    content = get_file_content(
                        file_info["temp_path"], file_info["type"]
                    )
                    file_contents.append(
                        f"File: {file_info['name']}\n\nContent:\n{content}\n"
                    )
                # For images, just mention them
                elif file_info["type"].startswith("image/"):
                    description = file_info.get("description", "An image file")
                    file_contents.append(f"File: {file_info['name']} - {description}")
                # For other files, just mention them
                else:
                    file_contents.append(
                        f"File: {file_info['name']} ({file_info['type']})"
                    )

        if file_contents:
            ai_message += "\n\n" + "\n\n".join(file_contents)

    # Get bot response
    system_prompt = st.session_state.get(
        "system_prompt", "You are a helpful assistant."
    )
    model = st.session_state.get("model", OLLAMA_MODEL)
    response = get_gemma_response(ai_message, system_prompt, model)

    # Add bot response to chat history
    bot_message_data = {
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    st.session_state.messages.append(bot_message_data)

    # Clear the current files after sending
    st.session_state.current_files = []


# Sidebar with settings and options
with st.sidebar:
    st.title("Gemma 3 Chatbot")

    # Check Ollama availability
    ollama_available, ollama_info = check_ollama_availability()

    if ollama_available:
        st.success("✅ Connected to Ollama")

        # Get available models
        available_models = [tag["name"] for tag in ollama_info.get("models", [])]

        # Model settings
        st.header("Model Settings")

        if available_models:
            st.session_state.model = st.selectbox(
                "Select Model",
                options=available_models,
                index=available_models.index(OLLAMA_MODEL)
                if OLLAMA_MODEL in available_models
                else 0,
            )
        else:
            st.session_state.model = st.text_input("Model Name", value=OLLAMA_MODEL)
            st.caption(
                "No models found in Ollama. Make sure you've pulled the models first."
            )
            if st.button("Pull Gemma 3"):
                st.info("Attempting to pull gemma3 model... This might take a while.")
                try:
                    response = requests.post(
                        f"{OLLAMA_API_BASE}/pull", json={"name": "gemma3"}
                    )
                    if response.status_code == 200:
                        st.success(
                            "Successfully initiated model pull. This might take a while to complete."
                        )
                    else:
                        st.error(f"Failed to pull model: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.error(f"❌ Cannot connect to Ollama: {ollama_info}")
        st.info(
            "Please make sure Ollama is running and accessible at http://localhost:11434"
        )
        st.session_state.model = OLLAMA_MODEL

    # System prompt
    st.header("System Prompt")
    st.session_state.system_prompt = st.text_area(
        "System Instructions",
        value=st.session_state.get(
            "system_prompt",
            "You are a helpful AI assistant powered by Gemma 3. Answer questions clearly and helpfully.",
        ),
        height=100,
    )

    temperature = st.slider(
        "Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1
    )

    # Display session ID
    st.header("Session Info")
    st.code(f"Session ID: {st.session_state.session_id}")

    # Chat management
    st.header("Chat Management")
    if st.button("Clear Chat"):
        clear_chat()

    if st.button("Save Chat"):
        saved_file = save_chat_history()
        st.markdown(get_download_link(saved_file), unsafe_allow_html=True)

    # Chat history files
    st.header("Previous Chats")
    if os.path.exists("chat_history"):
        history_files = [f for f in os.listdir("chat_history") if f.endswith(".json")]
        if history_files:
            selected_file = st.selectbox("Load Previous Chat", history_files)
            if st.button("Load"):
                load_chat_history(selected_file)

# Main chat interface
st.title("Gemma 3 Chat Interface")
st.caption("Powered by Ollama")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        # If there are files attached to this message, show them
        if "files" in message and message["files"]:
            st.write("Attached files:")
            for file_id in message["files"]:
                if file_id in st.session_state.uploaded_files:
                    file_info = st.session_state.uploaded_files[file_id]
                    st.write(f"- {file_info['name']} ({file_info['type']})")

                    # For images, display them
                    if file_info["type"].startswith("image/"):
                        st.image(file_info["temp_path"])
                    # For text files, show a preview
                    elif file_info["type"].startswith("text/") or file_info[
                        "name"
                    ].endswith((".txt", ".md", ".py")):
                        with open(file_info["temp_path"], "r", errors="replace") as f:
                            content = f.read()
                            st.code(
                                content[:1000] + ("..." if len(content) > 1000 else "")
                            )

# File uploader
uploaded_files = st.file_uploader(
    "Upload files to include in your message", accept_multiple_files=True, type=None
)  # Allow all file types

# Process uploaded files
if uploaded_files:
    st.write("Files to be sent with your next message:")
    st.session_state.current_files = []
    for uploaded_file in uploaded_files:
        file_info = handle_file_upload(uploaded_file)
        st.session_state.current_files.append(file_info["id"])
        st.write(
            f"- {file_info['name']} ({file_info['type']}, {file_info['size']} bytes)"
        )


# Chat input - use a callback for the chat input
def on_message_submit():
    if st.session_state.user_input:
        send_message(st.session_state.user_input, st.session_state.current_files)
        st.session_state.user_input = ""  # Clear the input


# Use a text input with a button instead of chat_input to avoid auto-rerun issues
col1, col2 = st.columns([5, 1])
with col1:
    st.text_input(
        "Type your message here...", key="user_input", on_change=on_message_submit
    )
with col2:
    if st.button("Send"):
        on_message_submit()

# Footer information
st.markdown("---")
st.caption("Gemma 3 Chatbot Interface powered by Ollama")
