import streamlit as st
import ollama

def get_response(prompt):
    response = ollama.chat(model="gemma3", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

# Streamlit UI
st.set_page_config(page_title="Chatbot", page_icon="💬", layout="wide")
st.title("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if user_input := st.chat_input("Type your message..."):
    st.session_state["messages"].append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    response = get_response(user_input)
    st.session_state["messages"].append({"role": "assistant", "content": response})
    
    with st.chat_message("assistant"):
        st.markdown(response)
