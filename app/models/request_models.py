"""Request models for Smart Glasses LLM Controller."""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    """Voice or text command request sent from client to backend.
    
    Structure matches the API specification defined in the system design document.
    Accepts natural language commands with optional language and timestamp metadata.
    """
    command: str = Field(
        ...,
        description="The natural language command from the user",
        examples=["kamerayı aç ve analizi başlat", "sistem durumunu kontrol et"]
    )
    language: Optional[str] = Field(
        default="tr",
        description="Language code for ASR/TTS processing (e.g. 'tr', 'en')"
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp of the command (e.g. '2026-08-06T20:15:30')"
    )
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional additional context (device stats, location, active mode)"
    )


class TTSRequest(BaseModel):
    """Text-to-Speech synthesis request."""
    text: str = Field(..., description="Text to convert to speech output")
    language: Optional[str] = Field(default="tr", description="Language for TTS synthesis")


class ASRRequest(BaseModel):
    """ASR (Speech-to-Text) processing request metadata."""
    audio_file: str = Field(..., description="Path or base64 encoded audio data")
    language: Optional[str] = Field(default="tr", description="Expected speech language")
