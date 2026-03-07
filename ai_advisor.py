#!/usr/bin/env python3
"""
ArchonX AI Advisor v1.0
Provides secure secret management recommendations using:
1. HuggingFace Inference API (Mistral-7B) - Primary
2. Groq API (fallback 1)
3. Google Gemini API (fallback 2)
4. Offline mode (fallback 3)
"""

import json
import os
import sys
from typing import Any, Dict, Optional


class AIAdvisor:
    """Multi-backend AI advisor for vault recommendations."""

    def __init__(self):
        self.hf_token = os.getenv("HF_API_KEY")
        self.groq_token = os.getenv("GROQ_API_KEY")
        self.google_token = os.getenv("GOOGLE_API_KEY")
        self.backend = self._detect_backend()

    def _detect_backend(self) -> str:
        """Detect which backend is available."""
        if self.hf_token:
            return "huggingface"
        if self.groq_token:
            return "groq"
        if self.google_token:
            return "gemini"
        return "offline"

    def _query_huggingface(self, prompt: str) -> str:
        """Query HuggingFace Inference API with Mistral-7B."""
        try:
            import requests
        except ImportError:
            print("ERROR: requests not installed")
            return self._query_offline(prompt)

        api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
        headers = {"Authorization": f"Bearer {self.hf_token}"}

        try:
            response = requests.post(
                api_url,
                headers=headers,
                json={"inputs": prompt, "parameters": {"max_new_tokens": 500}}
            )
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
            return self._query_groq(prompt) if self.groq_token else self._query_offline(prompt)
        except Exception as e:
            print(f"HuggingFace error: {e}")
            return self._query_groq(prompt) if self.groq_token else self._query_offline(prompt)

    def _query_groq(self, prompt: str) -> str:
        """Query Groq API as fallback 1."""
        try:
            import requests
        except ImportError:
            return self._query_offline(prompt)

        try:
            # Groq API endpoint (as of March 2026)
            api_url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "mixtral-8x7b-32768",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500
            }
            response = requests.post(api_url, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return self._query_gemini(prompt) if self.google_token else self._query_offline(prompt)
        except Exception as e:
            print(f"Groq error: {e}")
            return self._query_gemini(prompt) if self.google_token else self._query_offline(prompt)

    def _query_gemini(self, prompt: str) -> str:
        """Query Google Gemini API as fallback 2."""
        try:
            import requests
        except ImportError:
            return self._query_offline(prompt)

        try:
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.google_token}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 500}
            }
            response = requests.post(api_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                candidates = result.get("candidates", [])
                if candidates:
                    return candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return self._query_offline(prompt)
        except Exception as e:
            print(f"Gemini error: {e}")
            return self._query_offline(prompt)

    def _query_offline(self, prompt: str) -> str:
        """Fallback 3: Offline static recommendations (always works)."""
        keywords = {
            "rotation": "Rotate secrets immediately. Use automated rotation policies with 30-day intervals.",
            "critical": "This is a CRITICAL-level secret. Move to dedicated vault (HashiCorp Vault, AWS Secrets Manager).",
            "password": "Generate strong passwords (16+ chars, mixed case, numbers, symbols). Use password manager.",
            "api key": "Revoke old keys. Generate new one. Store only in secrets manager, never in code.",
            "database": "Use database-specific vault (AWS RDS, Azure Database). Enable encryption at rest.",
            "token": "Tokens expire. Implement token refresh logic. Store securely with TTL.",
            "default": "Follow principle of least privilege. Audit access logs. Rotate quarterly."
        }

        prompt_lower = prompt.lower()
        for keyword, recommendation in keywords.items():
            if keyword in prompt_lower:
                return recommendation

        return keywords["default"]

    def get_advice(self, secret_key: str, classification: str, risk_level: str) -> str:
        """Get AI-powered advice for a specific secret."""
        prompt = f"""
As a security expert, provide a brief 1-2 sentence recommendation for securing this secret:
- Key Name: {secret_key}
- Type: {classification}
- Risk Level: {risk_level}

Focus on: rotation frequency, storage location, and access controls.
"""

        if self.backend == "huggingface":
            return self._query_huggingface(prompt)
        elif self.backend == "groq":
            return self._query_groq(prompt)
        elif self.backend == "gemini":
            return self._query_gemini(prompt)
        else:
            return self._query_offline(prompt)

    def get_status(self) -> Dict[str, Any]:
        """Return advisor status and available backends."""
        return {
            "active_backend": self.backend,
            "huggingface_available": bool(self.hf_token),
            "groq_available": bool(self.groq_token),
            "gemini_available": bool(self.google_token),
            "offline_fallback": True
        }


def main():
    """Test the advisor."""
    advisor = AIAdvisor()

    print("="*60)
    print("ArchonX AI Advisor Status")
    print("="*60)
    status = advisor.get_status()
    print(json.dumps(status, indent=2))

    # Test query
    print("\n" + "="*60)
    print("Sample Advice")
    print("="*60)
    advice = advisor.get_advice(
        "DATABASE_PASSWORD",
        "PASSWORD",
        "CRITICAL"
    )
    print(f"Backend: {advisor.backend}")
    print(f"Advice: {advice}")


if __name__ == "__main__":
    main()
