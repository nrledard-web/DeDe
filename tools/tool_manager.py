"""
DeDe - Tool Manager

Executes tools through a common registry and returns
normalized results.
"""

from __future__ import annotations

from typing import Any

from tools.tool_registry import ToolRegistry
from tools.tool_result import build_tool_result


class ToolManager:
    """
    Central execution layer for DeDe tools.
    """

    name = "tool_manager"

    def __init__(
        self,
        registry: ToolRegistry | None = None,
    ) -> None:
        self.registry = registry or ToolRegistry()

    def register(
        self,
        tool: Any,
    ) -> None:
        self.registry.register(tool)

    def run(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        cleaned_tool_name = str(
            tool_name or ""
        ).strip()

        arguments = arguments or {}

        if not cleaned_tool_name:
            return build_tool_result(
                tool="unknown",
                status="invalid_request",
                error="No tool name was provided.",
                summary="Tool execution could not start.",
            )

        tool = self.registry.get(
            cleaned_tool_name
        )

        if tool is None:
            return build_tool_result(
                tool=cleaned_tool_name,
                status="not_found",
                error=(
                    f"Tool '{cleaned_tool_name}' "
                    "is not registered."
                ),
                summary="Requested tool is unavailable.",
            )

        try:
            raw_result = tool.run(
                **arguments
            )

        except TypeError as error:
            return build_tool_result(
                tool=cleaned_tool_name,
                status="invalid_arguments",
                error=str(error),
                summary=(
                    "The tool received invalid arguments."
                ),
            )

        except Exception as error:
            return build_tool_result(
                tool=cleaned_tool_name,
                status="error",
                error=str(error),
                summary="Tool execution failed.",
            )

        if not isinstance(
            raw_result,
            dict,
        ):
            return build_tool_result(
                tool=cleaned_tool_name,
                status="invalid_result",
                error=(
                    "The tool returned an unsupported "
                    "result format."
                ),
                summary="Tool result could not be normalized.",
            )

        status = str(
            raw_result.get(
                "status",
                "success",
            )
        )

        error = raw_result.get(
            "error"
        )

        data = {
            key: value
            for key, value in raw_result.items()
            if key not in {
                "tool",
                "status",
                "error",
                "summary",
            }
        }

        return build_tool_result(
            tool=cleaned_tool_name,
            status=status,
            data=data,
            error=error,
            summary=str(
                raw_result.get(
                    "summary",
                    "",
                )
            ),
        )

    def available_tools(
        self,
    ) -> list[dict[str, Any]]:
        return self.registry.list_tools()
