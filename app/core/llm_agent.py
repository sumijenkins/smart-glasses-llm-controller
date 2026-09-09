"""OpenAI LLM Agent and Function Calling manager.

Implements the Agentic AI pattern described in Section 2.6 of the system design document:
  - Perception: User command received
  - Reasoning: LLM analyzes and selects function
  - Action: Backend executes hardware function
  - Feedback: Result synthesized into natural language response

Also implements the ReAct (Reasoning + Acting) paradigm per Section 2.6.
"""
import json
import logging
from typing import List, Dict, Any, Tuple, Optional


try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from app.config import settings
from app.core.prompts import SYSTEM_PROMPT
from app.actions.schemas import TOOLS_SCHEMA
from app.actions import (
    open_camera,
    stop_camera,
    start_analysis,
    check_status,
    stop_process
)
from app.models.response_models import ExecutedAction

logger = logging.getLogger(__name__)


class LLMAgent:
    """LLM Agent routing user commands to hardware actions via Function Calling.
    
    Implements Agentic AI architecture (Section 2.6):
      Perceive → Reason → Act → Feedback
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.client = OpenAI(api_key=self.api_key) if (OpenAI and self.api_key) else None

        # Action registry: maps OpenAI tool name → Python function
        self.action_registry = {
            "open_camera": open_camera,
            "stop_camera": stop_camera,
            "start_analysis": start_analysis,
            "check_status": check_status,
            "stop_process": stop_process
        }

    def process_command(self, command: str) -> Tuple[str, Optional[str], Dict[str, Any], List[ExecutedAction], str]:

        """Process user natural language command via LLM Function Calling.
        
        Args:
            command: Natural language user command string.
            
        Returns:
            Tuple of (status, action_name, parameters, executed_actions, message)
        """
        executed_actions: List[ExecutedAction] = []

        # Fallback heuristic mode when no OpenAI API key is configured
        if not self.client:
            logger.warning("No OPENAI_API_KEY configured. Running in heuristic simulation mode.")
            return self._heuristic_fallback(command)

        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": command}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=settings.TEMPERATURE
            )

            response_message = response.choices[0].message

            # Tool/Function call execution loop
            if response_message.tool_calls:
                messages.append(response_message)
                primary_action = None
                primary_params = {}

                for tool_call in response_message.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}

                    logger.info(f"LLM triggered function: {fn_name}({fn_args})")

                    if fn_name in self.action_registry:
                        result = self.action_registry[fn_name](**fn_args)
                    else:
                        result = {"status": "error", "message": f"Unknown function: {fn_name}"}

                    # Track primary action for document-spec response format
                    if primary_action is None:
                        primary_action = fn_name
                        primary_params = fn_args

                    executed_actions.append(
                        ExecutedAction(action_name=fn_name, parameters=fn_args, result=result)
                    )

                    # Return tool result to LLM for synthesis
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": fn_name,
                        "content": json.dumps(result, ensure_ascii=False)
                    })

                # Second LLM call to synthesize natural language response
                second_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=settings.TEMPERATURE
                )
                message_text = second_response.choices[0].message.content or "İşlem tamamlandı."
                return "success", primary_action, primary_params, executed_actions, message_text

            # No tool call — pure conversational response
            message_text = response_message.content or "Komutunuz alındı ancak herhangi bir donanım eylemi gerekmedi."
            return "success", None, {}, executed_actions, message_text

        except Exception as e:
            logger.error(f"LLM processing error: {e}", exc_info=True)
            return self._heuristic_fallback(command)

    def _heuristic_fallback(self, command: str) -> Tuple[str, str, Dict[str, Any], List[ExecutedAction], str]:
        """Keyword-based simulation when OpenAI API is unavailable (demo/offline mode)."""
        text = command.lower()
        executed_actions = []

        if "kamera" in text and ("aç" in text or "başlat" in text or "aktif" in text):
            res = open_camera()
            executed_actions.append(ExecutedAction(action_name="open_camera", parameters={}, result=res))
            return "success", "open_camera", {}, executed_actions, res["message"]

        elif "kamera" in text and ("kapat" in text or "durdur" in text):
            res = stop_camera()
            executed_actions.append(ExecutedAction(action_name="stop_camera", parameters={}, result=res))
            return "success", "stop_camera", {}, executed_actions, res["message"]

        elif "analiz" in text or "tanı" in text or "nesne" in text or "bak" in text:
            res = start_analysis(type="camera")
            executed_actions.append(ExecutedAction(action_name="start_analysis", parameters={"type": "camera"}, result=res))
            return "success", "start_analysis", {"type": "camera"}, executed_actions, res["message"]

        elif "sensör" in text or "veri" in text:
            res = start_analysis(type="sensor")
            executed_actions.append(ExecutedAction(action_name="start_analysis", parameters={"type": "sensor"}, result=res))
            return "success", "start_analysis", {"type": "sensor"}, executed_actions, res["message"]

        elif "durum" in text or "pil" in text or "batarya" in text or "şarj" in text:
            res = check_status(component="all")
            executed_actions.append(ExecutedAction(action_name="check_status", parameters={"component": "all"}, result=res))
            return "success", "check_status", {"component": "all"}, executed_actions, res["message"]

        elif "durdur" in text or "iptal" in text or "dur" in text:
            res = stop_process(process_name="all")
            executed_actions.append(ExecutedAction(action_name="stop_process", parameters={"process_name": "all"}, result=res))
            return "success", "stop_process", {"process_name": "all"}, executed_actions, res["message"]

        message = f"Komutunuz alındı: '{command}'. Herhangi bir donanım eylemi tetiklenmedi."
        return "success", None, {}, executed_actions, message
