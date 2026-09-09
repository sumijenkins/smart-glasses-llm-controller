# Smart Glasses LLM Controller

Akıllı gözlük sistemleri için tasarlanmış **FastAPI**, **OpenAI Function Calling (Tools)**, **ASR (Speech-to-Text)**, **TTS (Text-to-Speech)** ve **Vision (Nesne Tespiti / OCR)** entegrasyonlu modüler LLM kontrolcü mimarisi.

---

## Proje Mimarisi

```text
smart-glasses-llm-controller/
│
├── .env.example               # Çevre değişkenleri şablonu (API anahtarları, portlar vb.)
├── .gitignore
├── requirements.txt           # Gerekli Python kütüphaneleri (FastAPI, OpenAI, Whisper vb.)
├── README.md                  # Kurulum, mimari ve çalıştırma adımları
│
├── app/                       # Ana Backend Uygulama Katmanı (FastAPI)
│   ├── __init__.py
│   ├── main.py                # FastAPI başlatıcı ve endpoint yönlendiricileri (/command, /health)
│   ├── config.py              # Uygulama ve model ayarları
│   │
│   ├── core/                  # LLM ve Karar/Ajan Mekanizmaları
│   │   ├── __init__.py
│   │   ├── llm_agent.py       # OpenAI / LLM istemcisi ve Function Calling yönetimi
│   │   └── prompts.py         # System prompt ve ReAct/Ajan yönergeleri
│   │
│   ├── actions/               # Tetiklenen Sistem/Donanım Fonksiyonları
│   │   ├── __init__.py
│   │   ├── camera_actions.py  # open_camera, stop_camera vb.
│   │   ├── analysis_actions.py# start_analysis, nesne tespiti/sensör işleri
│   │   ├── device_actions.py  # check_status, stop_process vb.
│   │   └── schemas.py         # LLM Function Calling JSON şemaları (Tools)
│   │
│   └── models/                # Pydantic Veri Modelleri (Girdi/Çıktı Şemaları)
│       ├── __init__.py
│       ├── request_models.py  # Gelen istek modelleri (CommandRequest vb.)
│       └── response_models.py # Dönen yanıt modelleri (CommandResponse vb.)
│
├── client/                    # Etkileşim Katmanı / İstemci (Ses & Cihaz Arayüzü)
│   ├── __init__.py
│   ├── client_runner.py       # Mikrofon döngüsü ve backend ile haberleşme ana dosyası
│   ├── asr_service.py         # Whisper tabanlı ses-metin dönüşümü (Speech-to-Text)
│   └── tts_service.py         # pyttsx3 tabanlı metin-ses dönüşümü (Text-to-Speech)
│
├── vision/                    # (Opsiyonel) Görüntü İşleme / Edge AI Modülleri
│   ├── __init__.py
│   ├── detector.py            # YOLO / OpenCV nesne tespiti pipeline'ı
│   └── ocr.py                 # Metin okuma / OCR modülü
│
└── tests/                     # Test Dosyaları
    ├── __init__.py
    ├── test_api.py            # Endpoint testleri
    └── test_llm_actions.py    # Function calling eşleme testleri
```

---

## Kurulum ve Çalıştırma

### 1. Sanal Ortam Oluşturma ve Bağımlılıklar

```bash
# Sanal ortam oluşturun
python -m venv venv

# Aktifleştirin (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### 2. Çevre Değişkenleri (`.env`)

`.env.example` dosyasını kopyalayarak `.env` oluşturun:

```bash
copy .env.example .env
```

`.env` dosyası içerisindeki `OPENAI_API_KEY` alanına kendi OpenAI API anahtarınızı girin. (API anahtarı girilmediğinde sistem güvenli simülasyon modunda yanıt verir).

---

## Sunucu ve İstemciyi Başlatma

### Backend (FastAPI Sunucusu)

```bash
uvicorn app.main:app --reload --port 8000
```
- Swagger UI (Dokümantasyon): `http://localhost:8000/docs`
- Sağlık Kontrolü: `http://localhost:8000/health`

### İstemci (Client Runner)

```bash
python -m client.client_runner
```

---

## Testleri Çalıştırma

```bash
pytest -v
```

---

## Desteklenen LLM Fonksiyonları (Tools)

- `open_camera`: Kamerayı başlatır / kare yakalamaya başlar.
- `stop_camera`: Kamerayı durdurur.
- `start_analysis`: Nesne tespiti, sahne analizi veya OCR başlatır.
- `check_status`: Akıllı gözlük batarya, bellek ve sistem durumunu sorgular.
- `stop_process`: Çalışan aktif bir arka plan işlemini sonlandırır.
