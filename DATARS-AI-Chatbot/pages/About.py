import streamlit as st
import streamlit.components.v1 as components

pfpurl = "https://media.licdn.com/dms/image/v2/D5603AQHt8xwJzuPRGQ/profile-displayphoto-shrink_800_800/B56ZQCcJF1H0Ac-/0/1735207720129?e=1750896000&v=beta&t=9QkZtGEvAMqKBt-YVg3r7VZKpI68g1g-raYFeVjyU50"
# Custom CSS for styling
st.markdown("""
<style>
    .stApp {
        background-color: #00010f;
        color: #f0f0f0;
    }

    h1 {
        text-align: center;
        color: #f0f0f0;
        font-size: 2.5rem;
    }

    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #a0a0a0;
        margin-bottom: 2rem;
    }


    .social-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, #1f1f1f, #292929);
    color: #00bfff;
    text-decoration: none;
    border-radius: 12px;
    margin: 0.5rem;
    width: 160px;
    border: 1px solid rgba(0, 191, 255, 0.2);
    box-shadow: 0 0 8px rgba(0, 191, 255, 0.2);
    transition: all 0.3s ease;
    font-weight: 500;
    }

    .social-btn img {
        filter: brightness(0) invert(1);
        transition: transform 0.3s ease;
    }

    .social-btn:hover {
        background: linear-gradient(135deg, #0f2027, #203a43);
        color: #ffffff;
        border-color: #00bfff;
        box-shadow: 0 0 12px rgba(0, 191, 255, 0.6);
        transform: translateY(-2px);
    }

    .social-btn:hover img {
        transform: scale(1.1);
    }


    .social-btn:hover {
        background-color: #2c3e50;
        transform: translateY(-3px);
    }

    .coffee-section {
        display: flex;
        justify-content: center;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #a0a0a0;
        font-size: 0.9rem;
    }

    #MainMenu, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Profile circle
st.markdown(f"""
<div style="display: flex; justify-content: center; margin-top:-4rem;">
    <img src="{pfpurl}" alt="Profile" style="
        width: 150px;
        height: 150px;
        object-fit: cover;
        border-radius: 50%;
        border: 3px solid #8e44ad;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    ">
</div>
""", unsafe_allow_html=True)


# Title & subtitle
st.markdown("<h1>Sarvamm</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Data Science Student | AI Enthusiast</p>', unsafe_allow_html=True)

# About Section
st.markdown('<div class="about-section">', unsafe_allow_html=True)
st.markdown("""
<p style="text-align: justify; text-align-last: center;">
First year Data Science student specializing in AI and machine learning. Experienced in Python, SQL, and data visualization, with hands-on projects in predictive modeling and NLP. Constantly learning and exploring the field of intelligent systems. Open to discussions and collaboration!
</p>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# Social Links
# Social Links with images
st.markdown("""
<div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; margin-top: 1rem;">
    <a href="https://linkedin.com/in/sarvamm" target="_blank" class="social-btn">
        <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn" width="20" height="20">
        LinkedIn
    </a>
    <a href="https://github.com/Sarvamm" target="_blank" class="social-btn">
        <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" alt="GitHub" width="20" height="20">
        GitHub
    </a>
</div>
""", unsafe_allow_html=True)



# Buy Me a Coffee
st.markdown('<p style="text-align: center; margin-top: 2rem;">☕ If you like my work, support me here:</p>', unsafe_allow_html=True)
components.html("""
    <div style="display: flex; justify-content: center;">
        <a href="https://www.buymeacoffee.com/astrayn" target="_blank">
            <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" 
                alt="Buy Me A Coffee" 
                style="height: 60px !important; width: 217px !important;" >
        </a>
    </div>
""", height=100)

# Footer
st.markdown('<div class="footer">© 2025 Sarvamm</div>', unsafe_allow_html=True)