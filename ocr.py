import os
import tempfile
import time
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.getenv('GEMINI_API_KEY')

_last_request_time = 0
_request_count = 0
_minute_start = 0

def _rate_limit_wait(rpm_limit=30):
    """Rate limiting: dakikada maximum rpm_limit istek"""
    global _last_request_time, _request_count, _minute_start
    
    current_time = time.time()
    
    if current_time - _minute_start >= 60:
        _request_count = 0
        _minute_start = current_time
    
    if _request_count >= rpm_limit:
        wait_time = 60 - (current_time - _minute_start)
        if wait_time > 0:
            print(f"⏳ Rate limit: {wait_time:.1f} saniye bekleniyor...")
            time.sleep(wait_time)
            _request_count = 0
            _minute_start = time.time()
    
    min_interval = 60.0 / rpm_limit
    time_since_last = current_time - _last_request_time
    if time_since_last < min_interval:
        wait = min_interval - time_since_last
        time.sleep(wait)
    
    _last_request_time = time.time()
    _request_count += 1

def _ocr_with_gemini(image_path):
    if not GEMINI_KEY:
        raise Exception("GEMINI_API_KEY not set. Please add it to environment variables or .env file.")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        
        models_to_try = [
            ('gemini-2.0-flash-lite', 30),
            ('gemini-2.0-flash', 15),
            ('gemini-2.5-flash', 10),
        ]
        
        img = Image.open(image_path)
        prompt = "Bu görseldeki tüm metni çıkar. Sadece metni ver, başka bir şey ekleme."
        
        last_error = None
        for model_name, rpm_limit in models_to_try:
            try:
                print(f"Trying OCR with model: {model_name} (RPM limit: {rpm_limit})")
                
                _rate_limit_wait(rpm_limit)
                
                model = genai.GenerativeModel(model_name)
                response = model.generate_content([prompt, img])
                print(f"✓ OCR successful with model: {model_name}")
                return response.text.strip()
            except Exception as e:
                error_msg = str(e)
                print(f"Model {model_name} failed: {error_msg}")
                
                if '429' in error_msg or 'quota' in error_msg.lower():
                    print(f"⚠️ Rate limit hit for {model_name}, trying next model...")
                    last_error = e
                    continue
                
                last_error = e
                continue
        
        raise Exception(f"All OCR models failed. Last error: {str(last_error)}")
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
