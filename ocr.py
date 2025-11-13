import os
import subprocess
import tempfile
from pdf2image import convert_from_path
from PIL import Image

TESSERACT_PATH = '/opt/homebrew/bin/tesseract'

def _tesseract_ocr(image_obj, lang='tur'):
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        image_obj.save(tmp.name)
        tmp_path = tmp.name
    
    try:
        result = subprocess.run(
            [TESSERACT_PATH, tmp_path, 'stdout', '-l', lang],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            raise Exception(f"Tesseract error: {result.stderr}")
        return result.stdout.strip()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def pdf_to_text(pdf_path, dpi=200):
    pages = convert_from_path(pdf_path, dpi=dpi, poppler_path='/opt/homebrew/bin')
    texts = []
    for i, page in enumerate(pages):
        text = _tesseract_ocr(page, lang='tur')
        texts.append(text)
    return '\n\n'.join(texts)

def image_to_text(image_path):
    img = Image.open(image_path)
    return _tesseract_ocr(img, lang='tur')
