import streamlit as st
import ollama

st.title("Text Translator")

# Input box for text
text_to_translate = st.text_area("Enter text to translate:")

# Select target language
target_language = st.selectbox("Select target language:", ["Spanish", "French", "Dutch", "Hindi", "Arabic", "Japanese", "Chinese", "Korean", "Hebrew"], format_func=lambda x: x.upper())

# Translate button
if st.button("Translate"):
    if text_to_translate:
        # Use Ollama library to translate the text
        prompt = f"""Translate the following text to {target_language}. only reply with the translation:
         : {text_to_translate}"""

        response = ollama.chat(model="gemma3", messages=[{"role": "user", "content": prompt}])
        translated_text = response["message"]["content"]
        st.text_area("Translated text:", translated_text, height=150)
    else:
        st.warning("Please enter text to translate.")
