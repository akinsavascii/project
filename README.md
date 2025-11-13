# Experiment Report Summarizer - MVP

Bu küçük prototip şu akışı uygular:

- Kullanıcı PDF veya görsel yükler.
- Sunucu OCR (Tesseract) ile metni çıkarır.
- Metin Gemini veya OpenAI (varsa) kullanılarak özetlenir; API anahtarı yoksa basit bir extractive fallback çalışır.
- Özet PDF'e dönüştürülür ve kullanıcıya indirme linki verilir.

## Kurulum

### macOS

1. Sanal ortam oluşturun ve aktif edin (önerilir):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Gerekli paketleri yükleyin:

```bash
pip install -r requirements.txt
```

3. Tesseract kurulu değilse yükleyin (Homebrew):

```bash
brew install tesseract tesseract-lang
brew install poppler
```

4. `.env` dosyasını oluşturun:

```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin ve API anahtarlarınızı ekleyin:
```
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

5. Uygulamayı çalıştırın:

```bash
python app.py
```

Ardından tarayıcıda `http://localhost:5001` açın.

### Windows

1. Python 3.9+ kurulu olduğundan emin olun:

```powershell
python --version
```

2. Sanal ortam oluşturun ve aktif edin:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

3. Gerekli paketleri yükleyin:

```powershell
pip install -r requirements.txt
```

4. Tesseract OCR kurulumu:
   - [Tesseract GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki) sayfasından Windows installer'ı indirin
   - Kurulum sırasında "Additional language data" bölümünden **Turkish** dilini seçin
   - Kurulum yolunu not alın (örn: `C:\Program Files\Tesseract-OCR\tesseract.exe`)

5. Poppler kurulumu (PDF işleme için):
   - [Poppler Windows](https://github.com/oschwartz10612/poppler-windows/releases/) sayfasından son sürümü indirin
   - ZIP dosyasını çıkarın (örn: `C:\poppler\`)
   - `bin` klasörünü sistem PATH'ine ekleyin veya `ocr.py` dosyasında yolu belirtin

6. `ocr.py` dosyasını Windows için düzenleyin:

```python
# Windows için Tesseract yolu
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# pdf_to_text fonksiyonunda poppler yolunu belirtin:
pages = convert_from_path(pdf_path, dpi=dpi, poppler_path=r'C:\poppler\Library\bin')
```

7. `.env` dosyasını oluşturun:

```powershell
copy .env.example .env
```

`.env` dosyasını düzenleyin ve API anahtarlarınızı ekleyin:
```
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

8. Uygulamayı çalıştırın:

```powershell
python app.py
```

Ardından tarayıcıda `http://localhost:5001` açın.

## Notlar
- Gemini API öncelikli olarak kullanılır (ücretsiz model: `gemini-2.5-flash-live`)
- Gemini başarısız olursa OpenAI GPT-3.5-turbo denenir
- Her iki API de yoksa basit extractive özet oluşturulur
- API anahtarları için: [Google AI Studio](https://makersuite.google.com/app/apikey) ve [OpenAI Platform](https://platform.openai.com/api-keys)
