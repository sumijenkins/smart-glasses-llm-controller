"""FastAPI endpoint unit and integration tests.

Tests cover all 4 endpoints from Section 2.1.2.1 Table 2.2:
  POST /command  - Main LLM command processing
  GET  /health   - System health check
  POST /tts      - Text-to-Speech
  POST /asr      - Speech-to-Text

Request/response formats tested per Sections 2.1.2.3 and Table 2.4.

Note: TTS and ASR are mocked to prevent real audio output during tests.
"""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)



def test_health_check_endpoint():
    """Test /health endpoint returns 200 OK and expected JSON schema."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "llm_connected" in data


def test_command_endpoint_open_camera():
    """Test /command endpoint processes camera activation command.
    
    Request format per Section 2.1.2.3:
        {"command": "kamerayı aç", "language": "tr"}
    """
    payload = {
        "command": "kamerayı aç",
        "language": "tr",
        "timestamp": "2026-08-06T20:15:30"
    }
    response = client.post("/command", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Validate document-spec response structure
    assert data["status"] == "success"
    assert "action" in data
    assert "parameters" in data
    assert "message" in data
    assert isinstance(data["executed_actions"], list)
    assert len(data["executed_actions"]) > 0
    assert data["executed_actions"][0]["action_name"] == "open_camera"


def test_command_endpoint_start_analysis():
    """Test /command endpoint processes start_analysis command.
    
    Expected LLM output per Section 2.2.3:
        {"name": "start_analysis", "arguments": {"type": "camera"}}
    """
    payload = {
        "command": "analizi başlat",
        "language": "tr"
    }
    response = client.post("/command", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["action"] == "start_analysis"
    assert "message" in data


def test_command_endpoint_check_status():
    """Test /command endpoint processes system status check command."""
    payload = {"command": "pil durumunu kontrol et", "language": "tr"}
    response = client.post("/command", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["action"] == "check_status"
    assert "Batarya" in data["message"] or "%" in data["message"]


def test_command_endpoint_empty_input():
    """Test /command endpoint returns HTTP 400 for empty commands (Table 2.4)."""
    payload = {"command": "   ", "language": "tr"}
    response = client.post("/command", json=payload)
    assert response.status_code == 400


def test_command_endpoint_stop_process():
    """Test /command endpoint processes stop process command."""
    payload = {"command": "işlemi durdur", "language": "tr"}
    response = client.post("/command", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["action"] == "stop_process"


@patch("client.tts_service.TTSService.speak")  # ← sesi susturur, gerçek konuşma olmaz
def test_tts_endpoint(mock_speak):
    """Test /tts endpoint converts text to speech (Table 2.2).
    
    TTS motoru mock'lanır — test sırasında ses çıkışı olmaz.
    """
    payload = {"text": "Kamera başarıyla açıldı.", "language": "tr"}
    response = client.post("/tts", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["text_spoken"] == "Kamera başarıyla açıldı."
    mock_speak.assert_called_once_with("Kamera başarıyla açıldı.")  # gerçekten çağrıldı mı?


def test_tts_endpoint_empty_text():
    """Test /tts returns 400 for empty text."""
    payload = {"text": "   "}
    response = client.post("/tts", json=payload)
    assert response.status_code == 400


@patch("client.asr_service.ASRService.transcribe_audio", return_value="Kamerayı aç")  # ← whisper yüklemez
def test_asr_endpoint(mock_transcribe):
    """Test /asr endpoint returns transcription result (Table 2.2).
    
    Whisper modeli mock'lanır — ağır model yüklenmez.
    """
    payload = {"audio_file": "mock_audio.wav", "language": "tr"}
    response = client.post("/asr", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["transcribed_text"] == "Kamerayı aç"
    mock_transcribe.assert_called_once_with("mock_audio.wav")
