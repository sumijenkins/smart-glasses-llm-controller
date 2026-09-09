"""Actions package — hardware, analysis, and media control functions.

Per Section 2.1.2.2 Table 2.3 of the system design document:
  open_camera()              - Kamera donanımını etkinleştirir
  start_analysis(type)       - Kamera/sensör analizi çalıştırır
  detect_ppe()               - KKD uyum kontrolü (PPE_CHECK fazı)
  check_status([component])  - Sistem donanım durumu
  stop_process(process_name) - Aktif süreci sonlandırır

Metrik Raporu NOT kısmı (Video özelliği):
  play_instruction_video(topic) - Eğitim/tanıtım videosunu başlatır
"""
from app.actions.camera_actions import open_camera, stop_camera, capture_frame
from app.actions.analysis_actions import (
    start_analysis,
    detect_objects,
    detect_ppe,
    ocr_read,
    sensor_analysis,
)
from app.actions.device_actions import check_status, stop_process, get_battery_level
from app.actions.media_actions import play_instruction_video
from app.actions.schemas import TOOLS_SCHEMA

__all__ = [
    "open_camera",
    "stop_camera",
    "capture_frame",
    "start_analysis",
    "detect_objects",
    "detect_ppe",
    "ocr_read",
    "sensor_analysis",
    "check_status",
    "stop_process",
    "get_battery_level",
    "play_instruction_video",
    "TOOLS_SCHEMA",
]
