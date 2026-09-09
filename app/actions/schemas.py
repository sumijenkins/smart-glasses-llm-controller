"""OpenAI Function Calling schemas (Tools definitions).

Function schemas per Section 2.2.2 and Table 2.3 of the system design document.
These map exactly to the hardware control functions defined in the API specification.
"""

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "open_camera",
            "description": "Activates the smart glasses camera hardware and begins frame capture.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "stop_camera",
            "description": "Stops the active camera stream and deactivates camera hardware.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "start_analysis",
            "description": "Starts analysis process on the current camera frame or sensor data. Supports object detection (YOLO), OCR text reading, and scene description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["camera", "sensor"],
                        "description": "Analysis input type: 'camera' for visual analysis, 'sensor' for device sensor data"
                    }
                },
                "required": ["type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_status",
            "description": "Checks the smart glasses hardware status including battery level, memory usage, CPU temperature, and active processes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "component": {
                        "type": "string",
                        "enum": ["all", "battery", "memory", "camera"],
                        "description": "The specific hardware component to query"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "stop_process",
            "description": "Stops a running background or foreground process on the smart glasses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "process_name": {
                        "type": "string",
                        "description": "Name of the process to terminate (e.g. 'analysis', 'camera', 'all')"
                    }
                },
                "required": ["process_name"]
            }
        }
    }
]
