"""
Unified LLM Client supporting Groq, Google Gemini, OpenAI, and smart heuristic fallback.
"""
import os
import json
import re
from typing import Dict, Any, Optional

class UnifiedLLMClient:
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None, api_key: Optional[str] = None):
        self.provider = provider or "auto"
        self.model = model
        self.api_key = api_key
        self._init_client()

    def _init_client(self):
        # Auto-detect provider if auto
        if self.provider == "auto":
            if self.api_key or os.getenv("GROQ_API_KEY"):
                self.provider = "groq"
            elif os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
                self.provider = "gemini"
            elif os.getenv("OPENAI_API_KEY"):
                self.provider = "openai"
            else:
                self.provider = "heuristic"

        # Set default models
        if not self.model:
            if self.provider == "groq":
                self.model = "llama-3.3-70b-versatile"
            elif self.provider == "gemini":
                self.model = "gemini-1.5-flash"
            elif self.provider == "openai":
                self.model = "gpt-4o-mini"
            else:
                self.model = "heuristic-v1"

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.4, max_tokens: int = 2500) -> str:
        """
        Dispatches prompt to the active provider.
        """
        # Try primary provider
        try:
            if self.provider == "groq":
                return self._call_groq(system_prompt, user_prompt, temperature, max_tokens)
            elif self.provider == "gemini":
                return self._call_gemini(system_prompt, user_prompt, temperature, max_tokens)
            elif self.provider == "openai":
                return self._call_openai(system_prompt, user_prompt, temperature, max_tokens)
        except Exception as e:
            # Fall back gracefully to other providers or heuristic
            print(f"[LLM Client Warning] Provider {self.provider} failed: {e}. Attempting fallback...")

        # If primary failed or provider was heuristic
        return self._call_heuristic(system_prompt, user_prompt)

    def _call_groq(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
        from groq import Groq
        key = self.api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("No Groq API key available")
        client = Groq(api_key=key)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=self.model or "llama-3.3-70b-versatile",
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content or ""

    def _call_gemini(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
        import google.generativeai as genai
        key = self.api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not key:
            raise ValueError("No Gemini API key available")
        genai.configure(api_key=key)
        model = genai.GenerativeModel(
            model_name=self.model or "gemini-1.5-flash",
            system_instruction=system_prompt,
            generation_config={"temperature": temperature, "max_output_tokens": max_tokens}
        )
        response = model.generate_content(user_prompt)
        return response.text or ""

    def _call_openai(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
        import requests
        key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("No OpenAI API key available")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model or "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        res = requests.post(url, json=payload, headers=headers, timeout=40)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]

    def _call_heuristic(self, system_prompt: str, user_prompt: str) -> str:
        """
        Smart fallback that generates structured JSON responses when offline or keys missing.
        """
        from utils.heuristic_engine import generate_heuristic_response
        return generate_heuristic_response(system_prompt, user_prompt)

    @staticmethod
    def extract_json(text: str) -> Dict[str, Any]:
        """
        Robust JSON parser that strips markdown code fences and cleans trailing commas.
        """
        text = text.strip()
        # Remove markdown code blocks if wrapped
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in text:
            text = text.split("```", 1)[1].split("```", 1)[0].strip()

        # Find first '{' and last '}'
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            json_str = text[start:end+1]
            # Replace trailing commas before closing braces/brackets
            json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
            try:
                return json.loads(json_str)
            except Exception:
                pass

        try:
            return json.loads(text)
        except Exception as e:
            return {"raw_text": text, "error": f"JSON parsing failed: {e}"}
