"""
Base Agent class providing common LLM execution, logging, and error recovery.
"""
from typing import Dict, Any, Optional
from utils.llm_client import UnifiedLLMClient

class BaseAgent:
    def __init__(self, name: str, role: str, llm_client: Optional[UnifiedLLMClient] = None):
        self.name = name
        self.role = role
        self.llm = llm_client or UnifiedLLMClient()
        self.logs = []

    def log(self, message: str):
        entry = f"[{self.name}] {message}"
        self.logs.append(entry)
        print(entry)

    def execute_structured_prompt(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> Dict[str, Any]:
        """
        Executes a prompt requesting JSON and safely parses the output.
        """
        self.log(f"Executing reasoning task with {self.llm.provider} ({self.llm.model})...")
        full_system = f"{system_prompt}\nCRITICAL: Respond ONLY with valid, RFC 8259 compliant JSON. Do not prepend conversational text or markdown code fences outside JSON."
        raw_output = self.llm.generate(full_system, user_prompt, temperature=temperature)
        parsed = self.llm.extract_json(raw_output)
        return parsed
