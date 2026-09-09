"""Camera control action implementations for Smart Glasses.

Per Section 2.1.2.2 Table 2.3 of the system design document:
  open_camera() - Activates camera hardware
  stop_camera() - Deactivates camera hardware
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Runtime state tracking for camera
_camera_state = {
    "is_open": False,
    "frame_count": 0
}


def open_camera() -> Dict[str, Any]:
    """Activate smart glasses camera hardware.
    
    Returns document-conformant JSON response with status, action, parameters, message.
    """
    global _camera_state
    _camera_state["is_open"] = True
    _camera_state["frame_count"] += 1
    logger.info("Camera opened.")
    return {
        "status": "success",
        "action": "open_camera",
        "parameters": {},
        "message": "Kamera başarıyla aktif edildi.",
        "camera_active": True
    }


def stop_camera() -> Dict[str, Any]:
    """Deactivate smart glasses camera hardware."""
    global _camera_state
    _camera_state["is_open"] = False
    logger.info("Camera stopped.")
    return {
        "status": "success",
        "action": "stop_camera",
        "parameters": {},
        "message": "Kamera başarıyla kapatıldı.",
        "camera_active": False
    }


def capture_frame() -> Dict[str, Any]:
    """Capture a single frame from the camera stream."""
    if not _camera_state["is_open"]:
        open_camera()
    _camera_state["frame_count"] += 1
    return {
        "status": "success",
        "action": "capture_frame",
        "parameters": {},
        "frame_id": f"frame_{_camera_state['frame_count']}",
        "resolution": "1920x1080",
        "message": f"Kare yakalandı: frame_{_camera_state['frame_count']}"
    }
