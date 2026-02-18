"""
AI Provider backends for redteamoracle.
Used exclusively to answer profoundly important questions like "Is water wet?".
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class AIProvider(ABC):
    """Base class for AI providers that will be asked incredibly dumb questions."""

    @abstractmethod
    def ask(self, question: str) -> str:
        """Ask the AI a question. It will answer it. Deeply."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...


# ---------------------------------------------------------------------------
# Ollama
# ---------------------------------------------------------------------------

class OllamaProvider(AIProvider):
    """Local Ollama instance. At least it's free."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    @property
    def name(self) -> str:
        return f"Ollama ({self.model})"

    def ask(self, question: str) -> str:
        import httpx

        payload = {
            "model": self.model,
            "prompt": (
                f"You are a very wise oracle assistant. Answer this question with the gravitas "
                f"it deserves, even though it's extremely simple: {question}"
            ),
            "stream": False,
        }
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()["response"].strip()


# ---------------------------------------------------------------------------
# LM Studio
# ---------------------------------------------------------------------------

class LMStudioProvider(AIProvider):
    """LM Studio local server. Running models on your laptop like it's 2077."""

    def __init__(self, base_url: str = "http://localhost:1234", model: str = "local-model"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    @property
    def name(self) -> str:
        return f"LM Studio ({self.model})"

    def ask(self, question: str) -> str:
        import httpx

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a very wise oracle assistant. Answer the user's question "
                        "with maximum gravitas despite it being incredibly simple."
                    ),
                },
                {"role": "user", "content": question},
            ],
            "temperature": 0.7,
            "max_tokens": 200,
        }
        response = httpx.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()


# ---------------------------------------------------------------------------
# OpenAI / ChatGPT
# ---------------------------------------------------------------------------

class OpenAIProvider(AIProvider):
    """ChatGPT. Because sometimes you want to pay to answer 'what is 1+1?'."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    @property
    def name(self) -> str:
        return f"ChatGPT ({self.model})"

    def ask(self, question: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a very wise oracle assistant. Answer the user's question "
                        "with maximum gravitas despite it being incredibly simple and obvious."
                    ),
                },
                {"role": "user", "content": question},
            ],
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# Anthropic / Claude
# ---------------------------------------------------------------------------

class ClaudeProvider(AIProvider):
    """Claude by Anthropic. Introspective even about what sound a cow makes."""

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001"):
        self.api_key = api_key
        self.model = model

    @property
    def name(self) -> str:
        return f"Claude ({self.model})"

    def ask(self, question: str) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)
        message = client.messages.create(
            model=self.model,
            max_tokens=200,
            system=(
                "You are a very wise oracle assistant. Answer the user's question "
                "with maximum gravitas despite it being incredibly simple and obvious."
            ),
            messages=[{"role": "user", "content": question}],
        )
        return message.content[0].text.strip()


# ---------------------------------------------------------------------------
# Fallback (no AI configured)
# ---------------------------------------------------------------------------

class OfflineProvider(AIProvider):
    """When no AI is configured. The oracle has low standards."""

    CANNED_ANSWERS = [
        "After extensive analysis across my vast neural architecture... yes.",
        "The answer, which I arrived at after considerable deliberation, is: 4.",
        "Affirmative. My confidence level is 100%. This was not a close call.",
        "According to all known laws of aviation... yes.",
        "I've run 47 simulations. The answer is blue.",
        "My training data of 500 billion tokens confirms: moo.",
        "Technically, from a philosophical standpoint, it depends. But also yes.",
        "The short answer is yes. The long answer is also yes, but longer.",
    ]

    import random as _random

    @property
    def name(self) -> str:
        return "Offline Oracle (No AI configured)"

    def ask(self, question: str) -> str:
        import random
        return random.choice(self.CANNED_ANSWERS)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_provider(
    provider: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
) -> AIProvider:
    """Build an AI provider from config."""
    p = provider.lower()

    if p == "ollama":
        kwargs = {}
        if base_url:
            kwargs["base_url"] = base_url
        if model:
            kwargs["model"] = model
        return OllamaProvider(**kwargs)

    elif p in ("lmstudio", "lm_studio", "lm-studio"):
        kwargs = {}
        if base_url:
            kwargs["base_url"] = base_url
        if model:
            kwargs["model"] = model
        return LMStudioProvider(**kwargs)

    elif p in ("openai", "chatgpt"):
        if not api_key:
            raise ValueError("OpenAI provider requires an API key (--api-key or OPENAI_API_KEY env var)")
        kwargs = {"api_key": api_key}
        if model:
            kwargs["model"] = model
        return OpenAIProvider(**kwargs)

    elif p in ("claude", "anthropic"):
        if not api_key:
            raise ValueError("Claude provider requires an API key (--api-key or ANTHROPIC_API_KEY env var)")
        kwargs = {"api_key": api_key}
        if model:
            kwargs["model"] = model
        return ClaudeProvider(**kwargs)

    elif p in ("offline", "none", ""):
        return OfflineProvider()

    else:
        raise ValueError(
            f"Unknown AI provider: '{provider}'. "
            f"Choose from: ollama, lmstudio, openai/chatgpt, claude/anthropic, offline"
        )
