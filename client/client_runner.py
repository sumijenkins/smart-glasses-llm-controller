"""Client runner script for recording mic audio / input and contacting backend API."""
import os
import sys
import logging
import requests
from client.asr_service import ASRService
from client.tts_service import TTSService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("client_runner")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class ClientRunner:
    """Smart Glasses Client application runner."""

    def __init__(self):
        self.asr = ASRService()
        self.tts = TTSService()
        self.backend_url = BACKEND_URL

    def send_command_to_backend(self, command_text: str):
        """Send command request payload to backend FastAPI server."""
        endpoint = f"{self.backend_url}/command"
        payload = {
            "command": command_text,
            "language": "tr",
            "context": {"device": "SmartGlasses_v1"}
        }

        try:
            logger.info(f"Sending payload to backend: {payload}")
            response = requests.post(endpoint, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("message", "İşlem yapıldı.")
                actions = data.get("executed_actions", [])

                if actions:
                    logger.info(f"Executed Actions Count: {len(actions)}")
                    for act in actions:
                        logger.info(f" -> Action: {act['action_name']} | Result: {act['result'].get('summary', act['result'])}")

                # Speak back response text via TTS
                self.tts.speak(response_text)
            else:
                error_msg = f"Sunucu hatası ({response.status_code}): {response.text}"
                logger.error(error_msg)
                self.tts.speak("Üzgünüm, sunucu tarafında bir hata oluştu.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Cannot connect to backend server at {self.backend_url}: {e}")
            print(f"\n[!] Backend sunucusuna ulaşılamadı ({self.backend_url}). Lütfen 'uvicorn app.main:app' komutunu çalıştırın.\n")
            self.tts.speak("Bağlantı hatası. Backend sunucusu çalışmıyor.")

    def run_interactive_loop(self):
        """Interactive console loop for smart glasses voice/text commands."""
        print("=" * 60)
        print("👓 Smart Glasses LLM Controller Client Interactive Mode")
        print("Komut girmek için yazın, çıkmak için 'exit' veya 'q' yazın.")
        print("=" * 60)

        while True:
            try:
                user_input = input("\n[👓 Komut Girin (örn: 'Kamerayı aç ve nesne tespiti yap')]: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "q", "quit"]:
                    print("İstemci kapatılıyor...")
                    break

                self.send_command_to_backend(user_input)

            except KeyboardInterrupt:
                print("\nİstemci sonlandırıldı.")
                break


if __name__ == "__main__":
    client = ClientRunner()
    client.run_interactive_loop()
