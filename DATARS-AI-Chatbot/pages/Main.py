# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #
import streamlit as st
import random as rd
from utils.functions import get_ollama_stream, get_context, get_questions, execute

# ---------------------------------------------------------------------------- #
#                                    Status                                    #
# ---------------------------------------------------------------------------- #
st.title("DATARS - AI")
if st.session_state["df"] is not None:
    with st.status("Loading", expanded=True) as status:
        if st.session_state["status"] == "Online":
            st.write("Ollama is running")

        if st.session_state["context"] is None:
            st.session_state["context"] = get_context()
            st.write("Context loaded")

        if st.session_state["questions"] is None:
            st.session_state["questions"] = get_questions()
            st.write("Questions loaded")
        status.update(label="Loading complete!", state="complete", expanded=False)
        

    # ------------------------- Render suggestion buttons ------------------------ #
    def render_buttons() -> None:
        """
        Function to render the three question buttons abover the chat input
        """
        
        q1, q2, q3 = st.session_state["questions"][:3]

        left, mid, right = st.columns([1, 1, 1])

        if left.button(q1, key=f"left_{q1}"):
            st.session_state.user_input = q1
        if mid.button(q2, key=f"mid_{q2}"):
            st.session_state.user_input = q2
        if right.button(q3, key=f"right_{q3}"):
            st.session_state.user_input = q3
        return None

    # ---------------------------------------------------------------------------- #
    #                                 Show history                                 #
    # ---------------------------------------------------------------------------- #
    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_input" not in st.session_state:
        st.session_state.user_input = None
    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        if message["role"] == "assistant":
            with st.chat_message("assistant"):
                with st.expander("Show Code"):
                    st.markdown(message["content"])
                con = st.container(border=True)
                with con:
                    execute(message["content"])
    st.divider()
    render_buttons()

    # ---------------------------------------------------------------------------- #
    #                                 Main function                                #
    # ---------------------------------------------------------------------------- #
    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    chat_box_input = st.chat_input("Ask your question")

    def enter(prompt):
        if isinstance(prompt, str):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            stream = get_ollama_stream(prompt)

            # Stream the response to the chat using `st.write_stream`, then store it in
            # session state.
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

            con = st.container(border=True)
            with con:
                execute(response)
            st.session_state.user_input = None
            rd.shuffle(st.session_state.questions)
            st.rerun()

    if chat_box_input is not None:
        st.session_state.user_input = chat_box_input

    enter(st.session_state.user_input)
    
    st.session_state.user_input = None
    

else:
    st.markdown(f"""
### 🤖 Chat with Your Data

This chatbot lets you ask **natural language questions** about your dataset — and it replies with charts, insights, and Python code!

#### ✅ What it can do:
- Answer questions using pandas or visual plots
- Auto-generate Plotly graphs
- Show you the Python code behind every answer
- Display output, errors, and Streamlit elements

> **To begin:** Upload a CSV file on the main page or data overview tab.

📁 *Once uploaded, come back here to start chatting with your data!*

                """)
    st.warning("Upload a file to get started.")

# ------------------------------------ End ----------------------------------- #
