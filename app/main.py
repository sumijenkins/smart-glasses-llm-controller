"""FastAPI main application entrypoint for Smart Glasses LLM Controller.

Implements all REST API endpoints defined in Section 2.1.2.1 Table 2.2:
  POST /command  - Process natural language command via LLM Function Calling
  GET  /health   - System health check
  POST /tts      - Text-to-Speech synthesis
  POST /asr      - Speech-to-Text transcription
  
HTTP status codes per Table 2.4:
  200 OK                  - Command processed successfully
  400 Bad Request         - Invalid command format
  500 Internal Error      - Server-side failure
  503 Service Unavailable - LLM service unreachable
"""
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.request_models import CommandRequest, TTSRequest, ASRRequest
from app.models.response_models import (
    CommandResponse,
    HealthCheckResponse,
    TTSResponse,
    ASRResponse
)
from app.core.llm_agent import LLMAgent

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("smart_glasses_api")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Smart Glasses LLM Controller REST API. "
        "Controls smart glasses hardware via OpenAI Function Calling (Agentic AI). "
        "See Section 2.1.2 of the system design document for full API specification."
    )
)

# CORS — allows communication from smart glasses client and web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM Agent (Agentic AI per Section 2.6)
agent = LLMAgent()


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------
@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="System health check"
)
def health_check():
    """Health check endpoint — verifies server status and LLM API connectivity.
    
    Returns 200 OK with LLM connection status per Table 2.4.
    """
    return HealthCheckResponse(
        status="ok",
        version=settings.VERSION,
        llm_connected=bool(settings.OPENAI_API_KEY)
    )


# ---------------------------------------------------------------------------
# POST /command  (Main endpoint — Section 2.1.2.1 Table 2.2)
# ---------------------------------------------------------------------------
@app.post(
    "/command",
    response_model=CommandResponse,
    tags=["Command Processing"],
    summary="Process natural language voice/text command"
)
def process_command(request: CommandRequest):
    """Main command endpoint for Smart Glasses LLM Controller.
    
    Accepts natural language commands from smart glasses client,
    passes them to the LLM agent (Function Calling / Agentic AI),
    and returns a structured JSON response with action and system feedback.
    
    Request format (Section 2.1.2.3):
        {
            "command": "kamerayı aç ve analizi başlat",
            "language": "tr",
            "timestamp": "2026-08-06T20:15:30"
        }
        
    Response format (Section 2.1.2.3):
        {
            "status": "success",
            "action": "start_analysis",
            "parameters": {"type": "camera"},
            "message": "Analiz başlatılıyor"
        }
    
    HTTP Status codes per Table 2.4:
        200 - OK
        400 - Bad Request (empty or invalid command)
        500 - Internal Server Error
        503 - LLM Service Unavailable
    """
    logger.info(f"[/command] Received: '{request.command}' (lang={request.language})")

    if not request.command or not request.command.strip():
        raise HTTPException(status_code=400, detail="Geçersiz komut formatı: Komut boş olamaz.")

    try:
        status, action, parameters, executed_actions, message = agent.process_command(request.command)

        return CommandResponse(
            status=status,
            action=action,
            parameters=parameters,
            message=message,
            executed_actions=executed_actions
        )

    except ConnectionError as e:
        logger.error(f"LLM service connection error: {e}")
        raise HTTPException(status_code=503, detail="LLM servisi şu anda erişilemez durumda.")

    except Exception as e:
        logger.error(f"Unhandled error in /command: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Sunucu hatası: {str(e)}")


# ---------------------------------------------------------------------------
# POST /tts  (Section 2.1.2.1 Table 2.2)
# ---------------------------------------------------------------------------
@app.post(
    "/tts",
    response_model=TTSResponse,
    tags=["Speech"],
    summary="Text-to-Speech synthesis"
)
def text_to_speech(request: TTSRequest):
    """Convert text to speech audio output via pyttsx3.
    
    Used by smart glasses client to play audio feedback without calling /command.
    Suitable for direct TTS synthesis from pre-processed text strings.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Metin boş olamaz.")

    try:
        from client.tts_service import TTSService
        tts = TTSService()
        tts.speak(request.text)
        return TTSResponse(
            status="success",
            message="Ses çıktısı başarıyla üretildi.",
            text_spoken=request.text
        )
    except Exception as e:
        logger.error(f"TTS error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"TTS hatası: {str(e)}")


# ---------------------------------------------------------------------------
# POST /asr  (Section 2.1.2.1 Table 2.2)
# ---------------------------------------------------------------------------
@app.post(
    "/asr",
    response_model=ASRResponse,
    tags=["Speech"],
    summary="Automatic Speech Recognition (Speech-to-Text)"
)
def speech_to_text(request: ASRRequest):
    """Transcribe audio input to text using OpenAI Whisper (Section 2.1.3).
    
    Accepts audio file path and returns transcribed text.
    Used when smart glasses sends raw audio to backend for processing.
    """
    if not request.audio_file.strip():
        raise HTTPException(status_code=400, detail="Ses dosyası yolu boş olamaz.")

    try:
        from client.asr_service import ASRService
        asr = ASRService()
        transcribed = asr.transcribe_audio(request.audio_file)
        return ASRResponse(
            status="success",
            transcribed_text=transcribed,
            language=request.language
        )
    except Exception as e:
        logger.error(f"ASR error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"ASR hatası: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
