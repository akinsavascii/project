# Experiment Report Summarizer - MVP

Bu küçük prototip şu akışı uygular:

- Kullanıcı PDF veya görsel yükler.
- Sunucu OCR (Tesseract) ile metni çıkarır.
- Metin OpenAI (varsa) kullanılarak özetlenir; API anahtarı yoksa basit bir extractive fallback çalışır.
- Özet PDF'e dönüştürülür ve kullanıcıya indirme linki verilir.

Kurulum (macOS):

1. Sanal ortam oluşturun ve aktif edin (önerilir):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Gerekli paketleri yükleyin:

```bash
pip install -r requirements.txt
```

3. Tesseract kurulu değilse yükleyin (macOS/Homebrew):

```bash
brew install tesseract
```

4. `.env` dosyasını oluşturun (isteğe bağlı OpenAI için):

```bash
cp .env.example .env
# .env içinde OPENAI_API_KEY=... ekleyin eğer kullanacaksanız
```

5. Uygulamayı çalıştırın:

```bash
python app.py
```

Ardından tarayıcıda `http://localhost:5000` açın.

Notlar:
- `weasyprint` yerine basit `reportlab` kullandım; system bağımlılıkları daha az.
- Bu bir MVP iskeletidir. Çıktıların doğruluğunu test edip OpenAI ile entegrasyonu `OPENAI_API_KEY` ekleyerek deneyebilirsiniz.
