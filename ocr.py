import os
import subprocess
import tempfile
from pdf2image import convert_from_path
from PIL import Image
import shutil

def _get_tesseract_path():
    tesseract_path = os.getenv('TESSERACT_PATH')
    if tesseract_path:
        if os.path.exists(tesseract_path):
            return tesseract_path
    
    which_result = shutil.which('tesseract')
    if which_result:
        return which_result
    
    common_paths = [
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
        '/opt/homebrew/bin/tesseract'
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return '/usr/bin/tesseract'

try:
    TESSERACT_PATH = _get_tesseract_path()
except Exception:
    TESSERACT_PATH = '/usr/bin/tesseract'

POPPLER_PATH = os.getenv('POPPLER_PATH', None)

def _tesseract_ocr(image_obj, lang='tur'):
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        image_obj.save(tmp.name)
        tmp_path = tmp.name
    
    try:
        cmd = [TESSERACT_PATH, tmp_path, 'stdout', '-l', lang]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            raise Exception(f"Tesseract error: {result.stderr}")
        return result.stdout.strip()
    except FileNotFoundError:
        raise Exception(f"Tesseract not found at {TESSERACT_PATH}. Please check installation.")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def pdf_to_text(pdf_path, dpi=200):
    poppler_path = POPPLER_PATH if POPPLER_PATH else None
    pages = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)
    texts = []
    for i, page in enumerate(pages):
        text = _tesseract_ocr(page, lang='tur')
        texts.append(text)
    return '\n\n'.join(texts)

def image_to_text(image_path):
    img = Image.open(image_path)
    return _tesseract_ocr(img, lang='tur')
