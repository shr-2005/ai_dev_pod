"""
LLM Client - Meta Llama 3 8B Instruct via Groq API (OpenAI-compatible).
Fast, free tier with generous daily limits. No model access request needed.
"""
import os
from typing import Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class LlamaClient:
    """
    Client for Meta Llama 3 8B Instruct via Groq.
    Uses Groq's OpenAI-compatible chat completions API.
    """

    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY", ""),
        )
        self.model = "llama-3.3-70b-versatile"
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2048"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_new_tokens: int = None,
        temperature: float = None,
    ) -> str:
        """Generate text using Llama 3 8B via Groq."""
        max_new_tokens = max_new_tokens or self.max_tokens
        temperature = temperature or self.temperature

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_new_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            err = str(e)
            if "401" in err or "invalid_api_key" in err.lower():
                return "Error: Invalid Groq API key. Check GROQ_API_KEY in your .env file."
            if "429" in err or "rate_limit" in err.lower():
                return "Error: Groq rate limit reached. Please wait a moment and try again."
            if "503" in err or "unavailable" in err.lower():
                return "Error: Groq service temporarily unavailable. Please retry."
            return f"Error generating response: {err}"

    def chat(self, conversation_history: list, user_message: str) -> str:
        """Multi-turn chat with full conversation history."""
        system_prompt = """You are the AI Project Lead of a Virtual Development Pod.
You oversee a team of AI agents: Business Analyst, Design Agent, Developer Agent, and Testing Agent.
You help the Project Manager check status, quality, and details of all project artifacts.
Be concise, professional, and helpful. Reference specific artifacts when relevant."""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=512,
                temperature=0.6,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Chat error: {str(e)}"
