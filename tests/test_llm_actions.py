"""Unit tests for actions and OpenAI Function Calling schemas.

Tests per Section 2.2 (LLM Prompt Tasarımı) and Table 2.3 (Komut Fonksiyonları):
  - Function schemas validated against document spec (PPE + video tools included)
  - Action return values conform to document JSON format
  - LLM Agent fallback mode tested end-to-end
  - PPE compliance detection tested (Metrik Raporu Bölüm 3)
  - Video playback action tested (Metrik Raporu NOT kısmı)
"""
from app.actions.camera_actions import open_camera, stop_camera, capture_frame
from app.actions.analysis_actions import start_analysis, detect_objects, detect_ppe, ocr_read, sensor_analysis
from app.actions.device_actions import check_status, stop_process, get_battery_level
from app.actions.media_actions import play_instruction_video
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
    assert "detect_ppe" in tool_names
    assert "check_status" in tool_names
    assert "stop_process" in tool_names
    assert "play_instruction_video" in tool_names


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


def test_play_instruction_video_schema():
    """Verify play_instruction_video schema has topic enum with correct values."""
    schema = next(t for t in TOOLS_SCHEMA if t["function"]["name"] == "play_instruction_video")
    params = schema["function"]["parameters"]["properties"]
    assert "topic" in params
    topic_enum = set(params["topic"]["enum"])
    assert "trafo_bakim" in topic_enum
    assert "ppe_kullanim" in topic_enum
    assert "pano_montaj" in topic_enum
    assert "genel_tanitim" in topic_enum


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
# PPE Analysis Action Tests (Metrik Raporu Bölüm 3)
# ---------------------------------------------------------------------------

def test_start_analysis_camera_mode():
    """Test start_analysis with type='camera' runs PPE object detection (Section 2.2.3)."""
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


def test_detect_objects_ppe_classes():
    """Verify detect_objects returns YOLOv8 PPE classes with document accuracy metrics.

    Per Metrik Raporu Bölüm 3:
      Kask: %95.2 | Yelek: %90.4 | Eldiven: %86.1 | Maske: %88.2 | Gözlük: %79.3
    """
    res = detect_objects()
    assert res["status"] == "success"
    assert len(res["detected_objects"]) > 0
    assert "confidence" in res["detected_objects"][0]

    # PPE sınıfları kontrol
    labels = [d["label"] for d in res["detected_objects"]]
    assert "hardhat" in labels
    assert "vest" in labels
    assert "mask" in labels

    # Doküman doğruluk metrikleri (±0.01 tolerans)
    hardhat = next(d for d in res["detected_objects"] if d["label"] == "hardhat")
    assert abs(hardhat["confidence"] - 0.952) < 0.01

    vest = next(d for d in res["detected_objects"] if d["label"] == "vest")
    assert abs(vest["confidence"] - 0.904) < 0.01


def test_detect_ppe_compliance():
    """Verify detect_ppe() returns PPE compliance result with violation info."""
    res = detect_ppe()
    assert res["status"] == "success"
    assert res["action"] == "detect_ppe"
    assert "overall_compliant" in res
    assert "violation_count" in res
    assert "violations" in res
    assert isinstance(res["violations"], list)
    assert "message" in res


def test_ocr_read_industrial_label():
    """Verify ocr_read returns industrial equipment label (Trafo-402 pano seri no).

    Per staj raporu Bölüm 2.4 — OCR endüstriyel etiket senaryosu.
    """
    res = ocr_read()
    assert res["status"] == "success"
    assert "extracted_text" in res
    assert res["confidence"] > 0.5
    # Endüstriyel etiket içeriği kontrol
    assert "Trafo" in res["extracted_text"] or "Pano" in res["extracted_text"] or "TR-" in res["extracted_text"]
    assert "equipment_id" in res


# ---------------------------------------------------------------------------
# Media Action Tests (Metrik Raporu NOT kısmı)
# ---------------------------------------------------------------------------

def test_play_instruction_video_trafo():
    """Verify play_instruction_video returns success for trafo_bakim topic."""
    res = play_instruction_video(topic="trafo_bakim")
    assert res["status"] == "success"
    assert res["action"] == "play_instruction_video"
    assert res["parameters"]["topic"] == "trafo_bakim"
    assert "message" in res
    assert "playback_status" in res["parameters"]


def test_play_instruction_video_ppe():
    """Verify play_instruction_video returns success for ppe_kullanim topic."""
    res = play_instruction_video(topic="ppe_kullanim")
    assert res["status"] == "success"
    assert res["parameters"]["topic"] == "ppe_kullanim"


def test_play_instruction_video_pano():
    """Verify play_instruction_video returns success for pano_montaj topic."""
    res = play_instruction_video(topic="pano_montaj")
    assert res["status"] == "success"
    assert res["parameters"]["topic"] == "pano_montaj"


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
    # params may include _phase metadata, check type key
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


def test_llm_agent_ppe_command():
    """Verify LLMAgent fallback routes KKD/PPE command to detect_ppe."""
    agent = LLMAgent()
    status, action, params, actions, message = agent.process_command("kask kontrolü yap")
    assert status == "success"
    assert action == "detect_ppe"
    assert len(actions) == 1
    assert actions[0].action_name == "detect_ppe"


def test_llm_agent_video_command():
    """Verify LLMAgent fallback routes video command to play_instruction_video."""
    agent = LLMAgent()
    status, action, params, actions, message = agent.process_command("trafo bakım tanıtım videosunu aç")
    assert status == "success"
    assert action == "play_instruction_video"
    assert len(actions) == 1
    assert actions[0].action_name == "play_instruction_video"
    assert params.get("topic") == "trafo_bakim"
