"""
DeDe - Tool Registry

Stores the tools currently available to DeDe.
"""

from __future__ import annotations

from typing import Any


class ToolRegistry:
    """
    Register and retrieve callable DeDe tools.
    """

    def __init__(self) -> None:
        self._tools: dict[str, Any] = {}

    def register(
        self,
        tool: Any,
    ) -> None:
        tool_name = str(
            getattr(
                tool,
                "name",
                "",
            )
        ).strip()

        if not tool_name:
            raise ValueError(
                "A registered tool must define a non-empty name."
            )

        if not callable(
            getattr(
                tool,
                "run",
                None,
            )
        ):
            raise ValueError(
                f"Tool '{tool_name}' must define a callable run() method."
            )

        self._tools[tool_name] = tool

    def get(
        self,
        tool_name: str,
    ) -> Any | None:
        return self._tools.get(
            str(tool_name or "").strip()
        )

    def has(
        self,
        tool_name: str,
    ) -> bool:
        return self.get(tool_name) is not None

    def list_tools(
        self,
    ) -> list[dict[str, Any]]:
        result = []

        for tool_name, tool in self._tools.items():
            result.append(
                {
                    "name": tool_name,
                    "description": getattr(
                        tool,
                        "description",
                        "",
                    ),
                    "input_schema": getattr(
                        tool,
                        "input_schema",
                        {},
                    ),
                }
            )

        return result
