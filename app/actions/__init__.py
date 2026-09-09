"""Actions package — hardware and system control functions.

Per Section 2.1.2.2 Table 2.3 of the system design document:
  open_camera()              - Activates camera hardware
  start_analysis(type)       - Runs camera/sensor analysis
  check_status([component])  - Returns system hardware status
  stop_process(process_name) - Terminates active process
"""
from app.actions.camera_actions import open_camera, stop_camera, capture_frame
from app.actions.analysis_actions import start_analysis, detect_objects, ocr_read, sensor_analysis
from app.actions.device_actions import check_status, stop_process, get_battery_level
from app.actions.schemas import TOOLS_SCHEMA

__all__ = [
    "open_camera",
    "stop_camera",
    "capture_frame",
    "start_analysis",
    "detect_objects",
    "ocr_read",
    "sensor_analysis",
    "check_status",
    "stop_process",
    "get_battery_level",
    "TOOLS_SCHEMA"
]

