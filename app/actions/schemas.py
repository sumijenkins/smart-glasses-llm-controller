"""OpenAI Function Calling schemas (Tools definitions).

Function schemas per Section 2.2.2 and Table 2.3 of the system design document.
These map exactly to the hardware control functions defined in the API specification.

Video oynatma aracı (play_instruction_video) Metrik Raporu NOT kısmında
belirtilen "LLM tarafından video tanıtımı" özelliği için eklenmiştir.
"""

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "open_camera",
            "description": "Akıllı gözlük kamera donanımını etkinleştirir ve kare yakalamaya başlar.",
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
            "description": "Aktif kamera akışını durdurur ve kamera donanımını devre dışı bırakır.",
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
            "description": (
                "Mevcut kamera karesi veya sensör verisi üzerinde analiz başlatır. "
                "PPE/KKD nesne tespiti (YOLOv8), OCR metin okuma ve sahne açıklaması desteklenir."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["camera", "sensor"],
                        "description": "Analiz girdi türü: 'camera' görsel analiz, 'sensor' cihaz sensör verileri"
                    }
                },
                "required": ["type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "detect_ppe",
            "description": (
                "Saha personelinin KKD (Kişisel Koruyucu Donanım) uyum kontrolünü yapar. "
                "Kask, yelek, eldiven, maske ve koruyucu gözlük varlığını tespit eder. "
                "PPE_CHECK fazında kullanılır."
            ),
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
            "name": "check_status",
            "description": "Akıllı gözlük donanım durumunu kontrol eder: batarya, bellek, CPU sıcaklığı ve aktif süreçler.",
            "parameters": {
                "type": "object",
                "properties": {
                    "component": {
                        "type": "string",
                        "enum": ["all", "battery", "memory", "camera"],
                        "description": "Sorgulanacak donanım bileşeni"
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
            "description": "Akıllı gözlükte çalışan bir arka plan veya ön plan sürecini durdurur.",
            "parameters": {
                "type": "object",
                "properties": {
                    "process_name": {
                        "type": "string",
                        "description": "Sonlandırılacak sürecin adı (örn: 'analysis', 'camera', 'all')"
                    }
                },
                "required": ["process_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "play_instruction_video",
            "description": (
                "Saha işlemi veya ekipman kullanımı ile ilgili eğitim/tanıtım videosunu başlatır. "
                "Kullanıcı 'trafo bakımı videosu', 'İSG eğitimi', 'pano montajını göster' "
                "gibi bir komut verdiğinde bu fonksiyon tetiklenir."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": ["trafo_bakim", "ppe_kullanim", "pano_montaj", "genel_tanitim"],
                        "description": (
                            "Oynatılacak videonun konusu: "
                            "'trafo_bakim' Trafo bakım eğitimi, "
                            "'ppe_kullanim' İSG/KKD kullanım rehberi, "
                            "'pano_montaj' Dağıtım panosu montaj prosedürü, "
                            "'genel_tanitim' Genel sistem tanıtımı"
                        )
                    }
                },
                "required": ["topic"]
            }
        }
    }
]
