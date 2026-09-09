"""Unit tests for actions and OpenAI Function Calling schemas.

Tests per Section 2.2 (LLM Prompt Tasarımı) and Table 2.3 (Komut Fonksiyonları):
  - Function schemas validated against document spec
  - Action return values conform to document JSON format
  - LLM Agent fallback mode tested end-to-end
"""
from app.actions.camera_actions import open_camera, stop_camera, capture_frame
from app.actions.analysis_actions import start_analysis, detect_objects, ocr_read, sensor_analysis
from app.actions.device_actions import check_status, stop_process, get_battery_level
from app.actions.schemas import TOOLS_SCHEMA
from app.core.llm_agent import LLMAgent


# ---------------------------------------------------------------------------
# Schema Validation Tests
# ---------------------------------------------------------------------------

def test_tools_schema_structure():
    """Verify OpenAI tools schema matches Table 2.3 function definitions."""
    assert isinstance(TOOLS_SCHEMA, list)
    tool_names = [t["function"]["name"] for t in TOOLS_SCHEMA]
    # Per Table 2.3: open_camera, start_analysis, check_status, stop_process
    assert "open_camera" in tool_names
    assert "stop_camera" in tool_names
    assert "start_analysis" in tool_names
    assert "check_status" in tool_names
    assert "stop_process" in tool_names


def test_start_analysis_schema_type_parameter():
    """Verify start_analysis schema uses 'type' parameter with camera|sensor enum.
    
    Per Section 2.2.2 Function Calling Schema:
        {
            "name": "start_analysis",
            "parameters": {"type": {"enum": ["camera", "sensor"]}}
        }
    """
    schema = next(t for t in TOOLS_SCHEMA if t["function"]["name"] == "start_analysis")
    params = schema["function"]["parameters"]["properties"]
    assert "type" in params
    assert set(params["type"]["enum"]) == {"camera", "sensor"}


# ---------------------------------------------------------------------------
# Camera Action Tests
# ---------------------------------------------------------------------------

def test_open_camera_returns_document_format():
    """Verify open_camera() returns document-spec JSON (status, action, parameters, message)."""
    res = open_camera()
    assert res["status"] == "success"
    assert res["action"] == "open_camera"
    assert "parameters" in res
    assert "message" in res
    assert res["camera_active"] is True


def test_stop_camera_returns_document_format():
    """Verify stop_camera() returns document-spec JSON."""
    res = stop_camera()
    assert res["status"] == "success"
    assert res["action"] == "stop_camera"
    assert res["camera_active"] is False


def test_capture_frame():
    """Verify capture_frame() returns frame data."""
    res = capture_frame()
    assert res["status"] == "success"
    assert "frame_id" in res


# ---------------------------------------------------------------------------
# Analysis Action Tests
# ---------------------------------------------------------------------------

def test_start_analysis_camera_mode():
    """Test start_analysis with type='camera' runs object detection (Section 2.2.3)."""
    res = start_analysis(type="camera")
    assert res["status"] == "success"
    assert res["parameters"]["mode"] == "camera"
    assert "message" in res


def test_start_analysis_sensor_mode():
    """Test start_analysis with type='sensor' runs sensor analysis."""
    res = start_analysis(type="sensor")
    assert res["status"] == "success"
    assert res["parameters"]["mode"] == "sensor"
    assert "sensor_data" in res


def test_detect_objects():
    """Verify detect_objects returns YOLO-style results (Section 2.4)."""
    res = detect_objects()
    assert res["status"] == "success"
    assert len(res["detected_objects"]) > 0
    assert "confidence" in res["detected_objects"][0]


def test_ocr_read():
    """Verify ocr_read returns extracted text (Section 2.4)."""
    res = ocr_read()
    assert res["status"] == "success"
    assert "extracted_text" in res
    assert res["confidence"] > 0.5


# ---------------------------------------------------------------------------
# Device Action Tests
# ---------------------------------------------------------------------------

def test_check_status_all_components():
    """Verify check_status() returns full system info."""
    res = check_status(component="all")
    assert res["status"] == "success"
    assert res["action"] == "check_status"
    assert res["details"]["battery_percentage"] == 85
    assert "message" in res


def test_check_status_battery_component():
    """Verify check_status(battery) returns battery-specific data."""
    res = check_status(component="battery")
    assert res["status"] == "success"
    assert "battery_percentage" in res


def test_get_battery_level():
    """Verify battery helper returns integer value."""
    assert get_battery_level() == 85


def test_stop_process():
    """Verify stop_process returns document-spec JSON."""
    res = stop_process(process_name="analysis")
    assert res["status"] == "success"
    assert res["action"] == "stop_process"
    assert res["stopped_process"] == "analysis"
    assert "message" in res


# ---------------------------------------------------------------------------
# LLM Agent Heuristic Fallback Tests
# ---------------------------------------------------------------------------

def test_llm_agent_open_camera_command():
    """Verify LLMAgent fallback routes 'kamerayı aç' to open_camera."""
    agent = LLMAgent()
    status, action, params, actions, message = agent.process_command("kamerayı aç")
    assert status == "success"
    assert action == "open_camera"
    assert len(actions) == 1
    assert actions[0].action_name == "open_camera"
    assert "Kamera" in message or "aktif" in message


def test_llm_agent_start_analysis_command():
    """Verify LLMAgent fallback routes 'analiz' to start_analysis(type=camera)."""
    agent = LLMAgent()
    status, action, params, actions, message = agent.process_command("analizi başlat")
    assert status == "success"
    assert action == "start_analysis"
    assert params.get("type") == "camera"


def test_llm_agent_check_status_command():
    """Verify LLMAgent fallback routes battery query to check_status."""
    agent = LLMAgent()
    status, action, params, actions, message = agent.process_command("pil durumu ne?")
    assert status == "success"
    assert action == "check_status"
    assert "Batarya" in message or "%" in message


def test_llm_agent_stop_process_command():
    """Verify LLMAgent fallback routes stop command to stop_process."""
    agent = LLMAgent()
    status, action, params, actions, message = agent.process_command("işlemi durdur")
    assert status == "success"
    assert action == "stop_process"
