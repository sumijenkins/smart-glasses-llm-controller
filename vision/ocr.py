"""OCR metin tanıma modülü — endüstriyel saha etiketleri için.

Staj raporunda (Bölüm 2.4) belirtilen kullanım senaryosuna göre:
  Trafo etiketi, pano bilgisi, cihaz seri numarası gibi endüstriyel
  etiketleri okumak üzere yapılandırılmıştır.

Örnek hedef etiket: "Trafo-402 Pano Seri No: TR-8921"
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Simülasyon modunda dönecek örnek endüstriyel etiket verileri
SAMPLE_EQUIPMENT_LABELS = [
    {
        "text": "Trafo-402 Pano Seri No: TR-8921",
        "label_type": "equipment_tag",
        "equipment_id": "TR-8921",
        "equipment_name": "Trafo-402",
        "confidence": 0.94,
        "line_count": 1
    },
    {
        "text": "UYARI: Yüksek Gerilim — Yetkisiz Giriş Yasaktır",
        "label_type": "warning_sign",
        "equipment_id": None,
        "equipment_name": None,
        "confidence": 0.97,
        "line_count": 1
    },
    {
        "text": "Pano-07 Bakım Tarihi: 15.06.2026 Teknisyen: A.Yıldız",
        "label_type": "maintenance_log",
        "equipment_id": "Pano-07",
        "equipment_name": "Dağıtım Panosu 07",
        "confidence": 0.91,
        "line_count": 2
    }
]


class TextRecognizer:
    """Endüstriyel saha etiketleri için OCR pipeline.

    Trafo, dağıtım panosu, cihaz seri numarası ve
    uyarı levhalarını tanımak üzere yapılandırılmıştır.
    """

    def __init__(self, language: str = "tur+eng"):
        self.language = language
        self._label_index = 0  # Demo için döngüsel örnek seçici

    def extract_text(self, image_source: Any = None) -> Dict[str, Any]:
        """Kamera karesinden endüstriyel etiket metnini çıkarır.

        Simülasyon modunda Trafo-402 etiket çıktısı döner.
        Gerçek ortamda Tesseract/PaddleOCR pipeline'ı burada çalışır.
        """
        logger.info(f"Endüstriyel etiket OCR çalışıyor (dil: {self.language})...")

        # Varsayılan simülasyon: Trafo-402 etiketi (doküman örneği)
        sample = SAMPLE_EQUIPMENT_LABELS[0]
        return {
            "text": sample["text"],
            "label_type": sample["label_type"],
            "equipment_id": sample["equipment_id"],
            "equipment_name": sample["equipment_name"],
            "confidence": sample["confidence"],
            "line_count": sample["line_count"],
        }

    def extract_text_cyclic(self, image_source: Any = None) -> Dict[str, Any]:
        """Test/demo için farklı etiket örneklerini döngüsel olarak döner."""
        sample = SAMPLE_EQUIPMENT_LABELS[self._label_index % len(SAMPLE_EQUIPMENT_LABELS)]
        self._label_index += 1
        return {
            "text": sample["text"],
            "label_type": sample["label_type"],
            "equipment_id": sample["equipment_id"],
            "equipment_name": sample["equipment_name"],
            "confidence": sample["confidence"],
            "line_count": sample["line_count"],
        }
