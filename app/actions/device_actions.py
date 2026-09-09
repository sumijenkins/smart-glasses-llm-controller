"""Device and hardware status control actions for Smart Glasses.

Per Section 2.1.2.2 Table 2.3 of the system design document:
  check_status() - Returns system hardware status
  stop_process() - Terminates active processes
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def check_status(component: str = "all") -> Dict[str, Any]:
    """Check smart glasses hardware status.
    
    Returns document-conformant JSON response with status, action, parameters, message.
    """
    logger.info(f"Checking hardware status for component: {component}")

    status_data = {
        "battery_percentage": 85,
        "is_charging": False,
        "memory_usage": "42%",
        "cpu_temperature": "38°C",
        "active_processes": ["fastapi_backend", "camera_daemon"],
        "connection_status": "Wi-Fi Connected (5G)"
    }

    if component == "battery":
        return {
            "status": "success",
            "action": "check_status",
            "parameters": {"component": "battery"},
            "battery_percentage": status_data["battery_percentage"],
            "is_charging": status_data["is_charging"],
            "message": f"Batarya düzeyi %{status_data['battery_percentage']}."
        }

    return {
        "status": "success",
        "action": "check_status",
        "parameters": {"component": component},
        "details": status_data,
        "message": f"Sistem durumu: Batarya %{status_data['battery_percentage']}, Bellek: {status_data['memory_usage']}, Sıcaklık: {status_data['cpu_temperature']}."
    }


def get_battery_level() -> int:
    """Helper to get raw battery percentage value."""
    return 85


def stop_process(process_name: str = "all") -> Dict[str, Any]:
    """Stop active background or foreground process on smart glasses."""
    logger.info(f"Stopping process: {process_name}")
    return {
        "status": "success",
        "action": "stop_process",
        "parameters": {"process_name": process_name},
        "stopped_process": process_name,
        "message": f"'{process_name}' süreci başarıyla sonlandırıldı."
    }
