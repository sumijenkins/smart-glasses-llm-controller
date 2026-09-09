"""Medya oynatma aksiyonları — eğitim/tanıtım video yönetimi.

Staj Metrik Raporundaki NOT kısmında belirtildiği üzere:
  "Son dönem içerisinde LLM tarafından, yapılacak işle ilgili
   video tanıtımı sürece eklenecektir."

Bu modül, LLM tarafından tetiklenen video oynatma aksiyonunu
akıllı gözlük ekranı veya bağlı monitörde başlatır.

Desteklenen konular:
  trafo_bakim   — Trafo bakım ve güvenlik eğitimi
  ppe_kullanim  — İSG kuralları ve KKD kullanım rehberi
  pano_montaj   — Dağıtım panosu montaj ve bağlantı prosedürü
  genel_tanitim — Genel sistem tanıtımı
"""
import os
import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Video konu haritası — konu adı → dosya yolu
VIDEO_MAP: Dict[str, str] = {
    "trafo_bakim":  "assets/videos/trafo_bakim_egitimi.mp4",
    "ppe_kullanim": "assets/videos/isg_kurallari.mp4",
    "pano_montaj":  "assets/videos/pano_montaj.mp4",
    "genel_tanitim": "assets/videos/genel_tanitim.mp4",
}

# Türkçe konu etiketleri (TTS geri bildirimi için)
VIDEO_TOPIC_LABELS: Dict[str, str] = {
    "trafo_bakim":  "Trafo Bakım Eğitimi",
    "ppe_kullanim": "İSG Kuralları ve KKD Kullanımı",
    "pano_montaj":  "Pano Montaj Prosedürü",
    "genel_tanitim": "Genel Sistem Tanıtımı",
}


def play_instruction_video(topic: str) -> Dict[str, Any]:
    """Kullanıcının talep ettiği eğitim/talimat videosunu başlatır.

    LLM tarafından Function Calling aracılığıyla tetiklenir.
    Gerçek akıllı gözlük ortamında varsayılan medya oynatıcı veya
    OpenCV tabanlı overlay player başlatılır.

    Simülasyon modunda (video dosyası yoksa) başarı yanıtı döner.

    Args:
        topic: Oynatılacak videonun konusu.
               Geçerli değerler: 'trafo_bakim', 'ppe_kullanim',
                                 'pano_montaj', 'genel_tanitim'

    Returns:
        Dict with status, action, parameters, message fields.
    """
    video_path = VIDEO_MAP.get(topic, VIDEO_MAP["genel_tanitim"])
    topic_label = VIDEO_TOPIC_LABELS.get(topic, "Eğitim Videosu")

    logger.info(f"Video oynatma isteği: topic='{topic}', path='{video_path}'")

    # Gerçek ortamda dosya varsa sistem oynatıcısını başlat
    if os.path.exists(video_path):
        try:
            _launch_video_player(video_path)
            playback_status = "playing"
        except Exception as e:
            logger.warning(f"Video oynatıcı başlatılamadı: {e}")
            playback_status = "simulated"
    else:
        # Simülasyon modu — dosya henüz yüklü değil
        logger.info(f"Video dosyası bulunamadı ({video_path}). Simülasyon modu aktif.")
        playback_status = "simulated"

    message = f"'{topic_label}' konulu tanıtım videosu ekrana yansıtılıyor."

    return {
        "status": "success",
        "action": "play_instruction_video",
        "parameters": {
            "topic": topic,
            "topic_label": topic_label,
            "video_path": video_path,
            "playback_status": playback_status,
        },
        "message": message,
    }


def _launch_video_player(video_path: str) -> None:
    """Platformun varsayılan video oynatıcısını başlatır.

    Windows: start komutu
    Linux/Mac: xdg-open / open
    """
    import platform
    system = platform.system()

    if system == "Windows":
        os.startfile(os.path.abspath(video_path))
    elif system == "Darwin":
        subprocess.Popen(["open", video_path])
    else:
        subprocess.Popen(["xdg-open", video_path])

    logger.info(f"Video oynatıcı başlatıldı: {video_path}")
