# ---------------------------------------------------------------------------- #
#                                    IMPORTS                                   #
# ---------------------------------------------------------------------------- #

import streamlit as st
from streamlit_extras.buy_me_a_coffee import button
from utils.functions import is_ollama_running, start_ollama

# ------------------------------- Configuration ------------------------------ #
version: str = "0.0.1"
logo_gif: str = (
    "https://media1.tenor.com/m/d54XfQ2BGwcAAAAd/raccoon-circle-dance-round.gif"
)
coffee_username: str = "astrayn"


# ---------------------------------------------------------------------------- #
#                          Initialising session states                         #
# ---------------------------------------------------------------------------- #
if "status" not in st.session_state:
    st.session_state["status"] = "Offline"

if not is_ollama_running():
    start_ollama()
    if st.session_state["status"] == "Online":
        st.sidebar.success("ollama is running")

# ---------------------------------------------------------------------------- #

if "df" not in st.session_state:
    st.session_state["df"] = None
if "file_name" not in st.session_state:
    st.session_state["file_name"] = None
    
with st.sidebar:
    file = st.file_uploader("Upload data", ["csv"])

    if file is not None:
        st.session_state["file_name"] = file.name
        import pandas as pd

        st.session_state["df"] = pd.read_csv(file)

# ---------------------------------------------------------------------------- #

if "context" not in st.session_state:
    st.session_state["context"] = None
if "questions" not in st.session_state:
    st.session_state["questions"] = None


# ---------------------------------------------------------------------------- #
#                                  Page Setup                                  #
# ---------------------------------------------------------------------------- #
HomePage = st.Page(page="pages/Main.py", icon=":material/spa:", title="Main", default=True)
AboutPage = st.Page(page="pages/About.py", icon=":material/person:", title="About")


pg = st.navigation([HomePage, AboutPage])

st.logo(logo_gif, size="large")
with st.sidebar:
    st.markdown(8 * "<br>", unsafe_allow_html=True)
    st.caption("Support me by clicking on this button 👇")
    button(username=coffee_username, floating=False, width=221)
    st.caption(version)

pg.run()
# ------------------------------------ End ----------------------------------- #
