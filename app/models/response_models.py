"""Response models for Smart Glasses LLM Controller.

Matches the API response specification defined in the system design document:
  {
    'status': 'success',
    'action': 'start_analysis',
    'parameters': {'mode': 'camera'},
    'message': 'Analiz başlatılıyor'
  }
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ExecutedAction(BaseModel):
    """Details of a single action/tool executed by LLM Function Calling."""
    action_name: str = Field(..., description="Name of the executed action function")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters passed to the action")
    result: Dict[str, Any] = Field(default_factory=dict, description="Execution result payload")


class CommandResponse(BaseModel):
    """Response returned to client after LLM agent processes command.
    
    Follows the API response format defined in the system design document.
    Includes HTTP-compatible status field alongside LLM action details.
    """
    status: str = Field(
        ...,
        description="HTTP-aligned status string: 'success', 'error', or 'unavailable'",
        examples=["success", "error"]
    )
    action: Optional[str] = Field(
        default=None,
        description="The primary system function triggered (e.g. 'start_analysis', 'open_camera')"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Parameters passed to the triggered action function"
    )
    message: str = Field(
        ...,
        description="Natural language response message returned to the user (also used for TTS)"
    )
    executed_actions: List[ExecutedAction] = Field(
        default_factory=list,
        description="Full list of all system/hardware actions triggered during the request"
    )


class HealthCheckResponse(BaseModel):
    """System health check status model."""
    status: str = Field("ok", description="Overall health status")
    version: str = Field("1.0.0", description="API version")
    llm_connected: bool = Field(..., description="OpenAI API connectivity state")


class TTSResponse(BaseModel):
    """Response from the /tts endpoint."""
    status: str = Field("success")
    message: str = Field(..., description="Confirmation message")
    text_spoken: str = Field(..., description="The text that was converted to speech")


class ASRResponse(BaseModel):
    """Response from the /asr endpoint."""
    status: str = Field("success")
    transcribed_text: str = Field(..., description="Speech-to-text transcription result")
    language: Optional[str] = Field(default="tr")
