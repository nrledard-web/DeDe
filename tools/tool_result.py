"""
DeDe - Tool Result

Common result format returned by every DeDe tool.
"""

from __future__ import annotations

from typing import Any


def build_tool_result(
    tool: str,
    status: str,
    data: dict[str, Any] | None = None,
    error: str | None = None,
    summary: str = "",
) -> dict[str, Any]:
    """
    Build a normalized result shared by all tools.
    """

    return {
        "tool": tool,
        "status": status,
        "data": data or {},
        "error": error,
        "summary": summary,
    }
