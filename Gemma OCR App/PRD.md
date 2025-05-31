# Prompt PRD: Gemma OCR App

## 🎯 Project Goal:
Build a local-first OCR web app in **Python** using **Streamlit** for the UI and **Ollama** to interface with **Gemma 3**, a local LLM. The app should allow users to upload an image, perform OCR via Gemma 3, and output the result in **Markdown format**.

model_name = "gemma3:latest"
---

##Instructions:
- App.py is the entrypoint file
- pages/Main.py is where you are expected to write the code

## ✅ Functional Requirements:

- [ ] Accept image upload (PNG, JPG, JPEG) via Streamlit.
- [ ] Display uploaded image preview.
- [ ] On button click, send image to Gemma 3 using `ollama.chat()` or `ollama.generate()`.
- [ ] Prompt Gemma to extract readable text from the image and format it as Markdown.
- [ ] Display Markdown output on the UI using `st.markdown()`.
- [ ] Add "Copy to Clipboard" and "Download as .md" buttons.

---

## 🧠 LLM Prompt (for Gemma 3 via Ollama):

```python
prompt = f"""
You are an OCR assistant. Please extract readable text from the image input and return the result in clean, well-formatted Markdown.
"""
