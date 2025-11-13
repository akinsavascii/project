import os
import tempfile
from PIL import Image
import google.generativeai as genai

GEMINI_KEY = os.getenv('GEMINI_API_KEY')

def _ocr_with_gemini(image_path):
    if not GEMINI_KEY:
        raise Exception("GEMINI_API_KEY not set. OCR requires Gemini API.")
    
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        img = Image.open(image_path)
        
        prompt = "Bu görseldeki tüm metni çıkar. Sadece metni ver, başka bir şey ekleme."
        response = model.generate_content([prompt, img])
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Gemini OCR failed: {str(e)}")

def pdf_to_text(pdf_path, dpi=200):
    try:
        from pdf2image import convert_from_path
    except ImportError:
        raise Exception("pdf2image not installed")
    
    try:
        pages = convert_from_path(pdf_path, dpi=dpi)
        texts = []
        for i, page in enumerate(pages):
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                page.save(tmp.name, 'PNG')
                tmp_path = tmp.name
            
            try:
                text = _ocr_with_gemini(tmp_path)
                texts.append(text)
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        return '\n\n'.join(texts)
    except Exception as e:
        raise Exception(f"PDF processing failed: {str(e)}")

def image_to_text(image_path):
    return _ocr_with_gemini(image_path)
