"""Sistem metrik toplama modülü.

Staj raporundaki (Metrik Raporu Bölüm 3) hedef değerler:
  avg_inference_ms  : ~857 ms  (LLM çıkarım süresi)
  avg_e2e_seconds   : ~2.5 sn  (uçtan uca komut işleme süresi)
  total_sessions    : Toplam işlenen komut oturumu sayısı
  completed_sessions: Başarıyla tamamlanan oturum sayısı

Kullanım:
    from app.core.metrics import metrics_tracker
    metrics_tracker.record_request(inference_ms=850, e2e_seconds=2.4)
    summary = metrics_tracker.get_summary()
"""
import threading
import time
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MetricsTracker:
    """Thread-safe singleton metrik toplayıcı.

    Her /command isteğinde inference süresi ve uçtan uca süre kaydedilir.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self.total_sessions: int = 0
        self.completed_sessions: int = 0
        self.failed_sessions: int = 0
        self._total_inference_ms: float = 0.0
        self._total_e2e_seconds: float = 0.0
        self._phase_transitions: int = 0
        self._start_time: float = time.time()

    def record_request(
        self,
        inference_ms: float,
        e2e_seconds: float,
        completed: bool = True
    ) -> None:
        """Bir /command isteğinin metriklerini kaydeder.

        Args:
            inference_ms: LLM çıkarım süresi (milisaniye).
            e2e_seconds: Uçtan uca toplam süre (saniye).
            completed: İstek başarıyla tamamlandıysa True.
        """
        with self._lock:
            self.total_sessions += 1
            self._total_inference_ms += inference_ms
            self._total_e2e_seconds += e2e_seconds
            if completed:
                self.completed_sessions += 1
            else:
                self.failed_sessions += 1

        logger.debug(
            f"Metrik kaydedildi — inference: {inference_ms:.1f}ms, "
            f"e2e: {e2e_seconds:.2f}s, completed: {completed}"
        )

    def record_phase_transition(self) -> None:
        """Agent state machine faz geçişini kaydeder."""
        with self._lock:
            self._phase_transitions += 1

    def get_summary(self) -> Dict[str, Any]:
        """Metrik özetini doküman formatında döner.

        Returns:
            Dict with total_sessions, completed_sessions, avg_inference_ms,
            avg_e2e_seconds, success_rate_percent fields.
        """
        with self._lock:
            sessions = self.total_sessions
            completed = self.completed_sessions
            total_inf = self._total_inference_ms
            total_e2e = self._total_e2e_seconds
            phase_trans = self._phase_transitions
            uptime = time.time() - self._start_time

        avg_inference_ms = round(total_inf / sessions, 1) if sessions > 0 else 0.0
        avg_e2e_seconds = round(total_e2e / sessions, 2) if sessions > 0 else 0.0
        success_rate = round((completed / sessions * 100), 1) if sessions > 0 else 0.0

        return {
            "total_sessions": sessions,
            "completed_sessions": completed,
            "failed_sessions": self.failed_sessions,
            "avg_inference_ms": avg_inference_ms,
            "avg_e2e_seconds": avg_e2e_seconds,
            "success_rate_percent": success_rate,
            "phase_transitions": phase_trans,
            "uptime_seconds": round(uptime, 1),
        }

    def reset(self) -> None:
        """Tüm metrikleri sıfırlar (test ortamı için)."""
        with self._lock:
            self.total_sessions = 0
            self.completed_sessions = 0
            self.failed_sessions = 0
            self._total_inference_ms = 0.0
            self._total_e2e_seconds = 0.0
            self._phase_transitions = 0
            self._start_time = time.time()


# Global singleton örnek — tüm modüller bu örneği kullanır
metrics_tracker = MetricsTracker()
