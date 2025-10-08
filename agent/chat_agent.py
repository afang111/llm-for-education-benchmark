from abc import ABC
from typing import Any, List
import os
from dotenv import load_dotenv
import anthropic
from base import BaseAgent

class ChatAgent(BaseAgent, ABC):
    """
    A lightweight conversational agent built on Anthropic (Claude) SDK.
    It uses a shared message bus and a private message history.
    """

    def __init__(self, name: str, bus, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.bus = bus
        self.model = "claude-sonnet-4-5-20250929"
        self.history: List[dict] = []

        
    def reset(self, *args: Any, **kwargs: Any) -> None:
        """Clears the agent's personal history and sets the system prompt."""
        self.history = [{"role": "system", "content": self.system_prompt}]

    def step(self, user_input: str, *args: Any, **kwargs: Any) -> str:
        context = self.bus.get_context()

        user_message = (
            f"{context}\n\n"
            f"{self.name}, please continue the discussion.\n"
        )

        client = anthropic.Anthropic()
        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.7,
                system=self.system_prompt,
                messages=[
                {"role": "user", "content": user_message}
            ],
            )
        except Exception as e:
            print(f"⚠️ Error calling Claude API: {e}")
            return f"(Error: {e})"

        if not response.content or not response.content[0].text:
            reply = "(No response from model)"
        else:
            reply = response.content[0].text.strip()

        self.history.append({"role": "assistant", "content": reply})
        self.bus.post(self.name, reply)

        return reply
