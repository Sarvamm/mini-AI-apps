import base64
import ollama
from io import BytesIO

def image_to_base64(image):
    """Convert a PIL Image to base64 string"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def perform_ocr(image):
    """Perform OCR on the given image using Gemma 3 model"""
    try:
        # Convert image to base64
        img_base64 = image_to_base64(image)
        
        # Prepare the prompt
        prompt = """You are an OCR assistant. Please extract all readable text from the image input and return the result in clean, well-formatted Markdown.
        Extract all text possible do not change anything write down all text in the image, also create tables, underlines wherever necessary"""
        
        # Call Gemma 3 model
        response = ollama.chat(model='gemma3', messages=[
            {
                'role': 'user',
                'content': prompt,
                'images': [img_base64]
                
            }
        ])
        
        # Extract the markdown text from response
        return response['message']['content']
    
    except Exception as e:
        return f"Error performing OCR: {str(e)}"
