import streamlit as st
import pyperclip
from PIL import Image
from utils.ocr_utils import perform_ocr


st.title("📝 Gemma OCR App")
st.markdown("""
This app uses Gemma 3 to perform OCR (Optical Character Recognition) on images and returns the text in Markdown format.
Upload an image to get started!
""")

# File uploader
uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Create columns for layout
    col1, col2 = st.columns([1,4])

    with col1:
        st.subheader("Uploaded Image")
        # Display image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image")

        # Process button
        if st.button("Extract Text", type="primary"):
            with st.spinner("Processing image..."):
                # Perform OCR
                markdown_text = perform_ocr(image)

                # Store result in session state
                st.session_state["markdown_result"] = markdown_text
                st.success("Text extracted successfully!")

    with col2:
        st.subheader("Extracted Text")

        # Display results if available
        if "markdown_result" in st.session_state:
            # Display markdown
            st.markdown(st.session_state["markdown_result"])

            # Buttons for copy and download
            col_copy, col_download = st.columns(2)

            with col_copy:
                if st.button("📋 Copy to Clipboard"):
                    pyperclip.copy(st.session_state["markdown_result"])
                    st.success("Copied to clipboard!")

            with col_download:
                if st.button("💾 Download as .md"):
                    # Create download button
                    md_string = st.session_state["markdown_result"]
                    st.download_button(
                        label="Click to Download",
                        data=md_string,
                        file_name="extracted_text.md",
                        mime="text/markdown",
                    )
