"""
DeDe - OpenAI Bridge

OpenAI provider implementation for the generic LLM Bridge.

Requires:
- openai Python package
- OPENAI_API_KEY environment variable
"""

from typing import Any


class OpenAIBridge:
    """
    Sends DeDe's LLM package to OpenAI through the Responses API.
    """

    name = "openai_bridge"

    def __init__(
        self,
        model: str = "gpt-5.5",
    ):
        self.model = model

    def ask(
        self,
        llm_package: dict[str, Any],
    ) -> dict[str, Any]:

        try:
            from openai import OpenAI
        except ImportError:
            return {
                "bridge": self.name,
                "status": "error",
                "provider": "openai",
                "model": self.model,
                "response": None,
                "error": (
                    "OpenAI package is not installed. "
                    "Install it with: pip install openai"
                ),
            }

        try:
            client = OpenAI()

            response = client.responses.create(
                model=self.model,
                instructions=llm_package.get("system_prompt", ""),
                input=llm_package.get("full_prompt", ""),
            )

            output_text = getattr(response, "output_text", None)

            if not output_text:
                output_text = str(response)

            return {
                "bridge": self.name,
                "status": "success",
                "provider": "openai",
                "model": self.model,
                "response": output_text,
                "raw_response": response.model_dump()
                if hasattr(response, "model_dump")
                else str(response),
                "summary": "OpenAI response received successfully.",
            }

        except Exception as error:
            return {
                "bridge": self.name,
                "status": "error",
                "provider": "openai",
                "model": self.model,
                "response": None,
                "error": str(error),
                "summary": "OpenAI call failed.",
            }
