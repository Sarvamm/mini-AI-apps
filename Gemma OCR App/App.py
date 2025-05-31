import streamlit as st
from streamlit_extras.buy_me_a_coffee import button

version: str = "0.0.1"
logo_gif: str = "https://media1.tenor.com/m/d54XfQ2BGwcAAAAd/raccoon-circle-dance-round.gif"
coffee_username: str = "astrayn"

#Page setup
HomePage = st.Page(
    page="pages/Main.py",
    icon="🏠",
    title = "Main",
    default = True
)

AboutPage = st.Page(
    page="pages/About.py",
    icon="👤",    
    title = "About"
)

# Navigation Bar
pg = st.navigation([HomePage, AboutPage])

st.set_page_config(
    page_title="Gemma OCR App",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
    
)

st.logo(logo_gif, size='large')
with st.sidebar:
    st.caption("Support me by clicking on this button 👇")
    button(username=coffee_username, floating=False, width=221)
    st.caption(version)



pg.run()