"""Agent State Machine — Saha Denetim Süreci Faz Yöneticisi.

Staj raporunda (Bölüm 2.6 — Agentic AI Mimarisi) tanımlanan denetim sürecini
aşağıdaki fazlara böler:

  START → PPE_CHECK → EQUIPMENT_INSPECTION → COMPLETED

Kullanım:
    from app.core.agent_state import AgentStateManager, InspectionPhase

    manager = AgentStateManager()
    manager.advance()  # START → PPE_CHECK
    manager.advance()  # PPE_CHECK → EQUIPMENT_INSPECTION
    manager.complete() # → COMPLETED
"""
import logging
from enum import Enum
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class InspectionPhase(str, Enum):
    """Saha denetim süreci fazları."""
    START = "START"
    PPE_CHECK = "PPE_CHECK"
    EQUIPMENT_INSPECTION = "EQUIPMENT_INSPECTION"
    COMPLETED = "COMPLETED"


# Faz geçiş tablosu
_PHASE_TRANSITIONS = {
    InspectionPhase.START: InspectionPhase.PPE_CHECK,
    InspectionPhase.PPE_CHECK: InspectionPhase.EQUIPMENT_INSPECTION,
    InspectionPhase.EQUIPMENT_INSPECTION: InspectionPhase.COMPLETED,
    InspectionPhase.COMPLETED: InspectionPhase.COMPLETED,  # terminal
}

# Faz açıklamaları (Türkçe, kullanıcı arayüzü için)
PHASE_LABELS = {
    InspectionPhase.START: "Başlangıç — Denetim hazır",
    InspectionPhase.PPE_CHECK: "KKD Kontrolü — Kişisel koruyucu donanım denetimi",
    InspectionPhase.EQUIPMENT_INSPECTION: "Ekipman Denetimi — Pano/Trafo kontrolü",
    InspectionPhase.COMPLETED: "Tamamlandı — Denetim süreci başarıyla sonlandırıldı",
}


class AgentStateManager:
    """Saha denetim sürecinin fazlarını yöneten durum makinesi.

    Her komut işleme döngüsünde mevcut faza göre
    hangi aksiyonların öncelikli tetikleneceğini belirler.
    """

    def __init__(self):
        self.current_phase: InspectionPhase = InspectionPhase.START
        self.phase_history: list = [InspectionPhase.START]
        self.phase_accuracies: Dict[str, float] = {}

    @property
    def label(self) -> str:
        """Mevcut fazın Türkçe açıklaması."""
        return PHASE_LABELS[self.current_phase]

    @property
    def is_completed(self) -> bool:
        """Denetim süreci tamamlandıysa True."""
        return self.current_phase == InspectionPhase.COMPLETED

    def advance(self) -> InspectionPhase:
        """Bir sonraki faza geçer ve yeni fazı döner."""
        next_phase = _PHASE_TRANSITIONS[self.current_phase]
        if next_phase != self.current_phase:
            logger.info(f"Faz geçişi: {self.current_phase.value} → {next_phase.value}")
            self.current_phase = next_phase
            self.phase_history.append(next_phase)
        return self.current_phase

    def complete(self) -> None:
        """Denetim sürecini doğrudan COMPLETED fazına alır."""
        self.current_phase = InspectionPhase.COMPLETED
        if InspectionPhase.COMPLETED not in self.phase_history:
            self.phase_history.append(InspectionPhase.COMPLETED)
        logger.info("Denetim süreci tamamlandı (COMPLETED).")

    def record_phase_accuracy(self, accuracy: float) -> None:
        """Mevcut faz için doğruluk metriği kaydeder."""
        self.phase_accuracies[self.current_phase.value] = accuracy

    def get_context(self) -> Dict[str, Any]:
        """Mevcut durum makinesinin bağlamını metadata olarak döner.

        LLM agent yanıtına `parameters` içinde eklenebilir.
        """
        return {
            "current_phase": self.current_phase.value,
            "phase_label": self.label,
            "phase_history": [p.value for p in self.phase_history],
            "is_completed": self.is_completed,
            "phase_accuracies": self.phase_accuracies,
        }

    def reset(self) -> None:
        """Yeni bir denetim oturumu için fazı sıfırlar."""
        self.current_phase = InspectionPhase.START
        self.phase_history = [InspectionPhase.START]
        self.phase_accuracies = {}
        logger.info("AgentStateManager sıfırlandı — yeni denetim oturumu.")

    def suggest_action_for_phase(self) -> Optional[str]:
        """Mevcut faza göre önerilen aksiyon adını döner (heuristic yardımcı)."""
        suggestions = {
            InspectionPhase.START: None,
            InspectionPhase.PPE_CHECK: "detect_ppe",
            InspectionPhase.EQUIPMENT_INSPECTION: "ocr_read",
            InspectionPhase.COMPLETED: None,
        }
        return suggestions.get(self.current_phase)
