# Render ile Deployment Rehberi

## Ön Hazırlık

1. **GitHub'a Push Yapın:**
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

2. **Render Hesabı Oluşturun:**
   - [render.com](https://render.com) adresine gidin
   - "Get Started for Free" ile GitHub hesabınızla giriş yapın

## Deployment Adımları

### 1. Yeni Web Service Oluşturun

1. Render Dashboard'da **"New +"** butonuna tıklayın
2. **"Web Service"** seçin
3. GitHub repository'nizi bağlayın (akinsavascii/project)

### 2. Ayarları Yapılandırın

**Temel Ayarlar:**
- **Name:** experiment-report-summarizer
- **Region:** Frankfurt (veya size yakın bir bölge)
- **Branch:** main
- **Runtime:** Python 3
- **Build Command:** 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command:** 
  ```bash
  gunicorn --config gunicorn_config.py app:app
  ```

**Instance Type:**
- **Free** seçin (ilk başta test için)

### 3. Environment Variables (Çevre Değişkenleri)

Dashboard'da **"Environment"** sekmesine gidin ve şunları ekleyin:

```
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
UPLOAD_FOLDER=/tmp/uploads
SUMMARY_FOLDER=/tmp/summaries
TESSERACT_PATH=/usr/bin/tesseract
POPPLER_PATH=/usr/bin
```

### 4. Deploy Edin

1. **"Create Web Service"** butonuna tıklayın
2. Render otomatik olarak deployment'ı başlatacak
3. İlk deployment 5-10 dakika sürebilir
4. Deploy tamamlandığında size bir URL verilecek (örn: `https://experiment-report-summarizer.onrender.com`)

## Önemli Notlar

⚠️ **Free Plan Sınırlamaları:**
- 15 dakika hareketsizlikten sonra uygulama uyur
- İlk istek 30-60 saniye sürebilir (uyanma süresi)
- 750 saat/ay ücretsiz çalışma hakkı

⚠️ **Dosya Depolama:**
- Free plan'da `/tmp` klasörü geçicidir
- Upload edilen dosyalar yeniden başlatmada silinir
- Kalıcı depolama için Render Disk veya S3 gerekir

⚠️ **Tesseract ve Poppler:**
- Render'ın Ubuntu tabanlı sistemi kullanılıyor
- `Aptfile` dosyasıyla otomatik olarak yükleniyor
- Türkçe dil paketi (`tesseract-ocr-tur`) dahil
- Aptfile'da şu paketler tanımlı: `tesseract-ocr`, `tesseract-ocr-tur`, `poppler-utils`

## Test Etme

Deploy tamamlandıktan sonra:
1. Render'ın verdiği URL'i açın
2. Bir PDF veya görsel yükleyin
3. Özet oluşturulmasını test edin

## Sorun Giderme

**Build Hatası:**
- Logs sekmesinden hata mesajlarını kontrol edin
- `requirements.txt` dosyasını kontrol edin

**Runtime Hatası:**
- Environment variables'ların doğru girildiğinden emin olun
- API anahtarlarının geçerli olduğunu kontrol edin

**Yavaş Yanıt:**
- İlk istek sonrası uygulama uyanır (normal)
- Cron-job.org ile 14 dakikada bir ping atabilirsiniz (uyku modunu engeller)

## Auto-Deploy

Render, GitHub'a her push yaptığınızda otomatik olarak yeniden deploy eder.

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Render otomatik olarak değişiklikleri algılayıp deploy eder.

## Maliyet

- **Free Plan:** $0/ay, 750 saat/ay, 512 MB RAM
- **Starter Plan:** $7/ay, her zaman aktif, 512 MB RAM
- **Pro Plan:** $25/ay, 2 GB RAM, daha fazla kaynak

## API Anahtarları

- **Gemini API:** [Google AI Studio](https://makersuite.google.com/app/apikey)
- **OpenAI API:** [OpenAI Platform](https://platform.openai.com/api-keys)
