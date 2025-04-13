import streamlit as st
import os
import ollama 

def fix_text(text):

    model="gemma3";
    prompt = f"""The following text contains errors like lots of spaces, incorrect formatting and spelling mistakes
    .Your job as a text editor assistant is to rewrite the text with proper formatting and correct spellings. 
    Reply with only the formated text. Fix all the text within the three braces.
    Here is the text:
     ((( {text} )))"""

    work = ollama.generate(model =model , prompt= prompt)
    fixed_text = work.get("response", "")
    return fixed_text

def main():
    st.title("Simple Text Fixer")
    
    # File uploader - just one button
    uploaded_file = st.file_uploader("Upload a text file", type=["txt"])
    
    if uploaded_file is not None:
        # Read file content
        text_content = uploaded_file.getvalue().decode("utf-8")
        
        # Display original text
        st.subheader("Original Text:")
        st.text_area("", text_content, height=200, disabled=True)
        
        # Fix text button - just one button
        if st.button("Fix Text"):
            # Process the text
            fixed_text = fix_text(text_content)
            
            # Display the fixed text
            st.subheader("Fixed Text:")
            st.text_area("", fixed_text, height=200)
            
            # Save the file
            output_filename = f"fixed_{uploaded_file.name}"
            with open(output_filename, "w") as f:
                f.write(fixed_text)
            
            st.success(f"Fixed text saved as: {output_filename}")
            st.download_button(
                label="Download Fixed Text",
                data=fixed_text,
                file_name=output_filename,
                mime="text/plain"
            )

if __name__ == "__main__":
    main()