"""
DeDe - Tool Factory

Builds and registers the tools available to DeDe.

This keeps tool construction outside app.py.
"""

from __future__ import annotations

import os

from tools.media.image_generator import ImageGenerator
from tools.media.cloudflare_image_generator import (
    CloudflareImageGenerator,
)
from tools.documents.pdf_reader import PDFReader
from tools.tool_manager import ToolManager


def build_tool_manager() -> ToolManager:
    """
    Build the default DeDe tool manager.
    """

    tool_manager = ToolManager()

    openai_api_key = os.environ.get(
        "OPENAI_API_KEY"
    )

    cloudflare_account_id = os.environ.get(
        "CLOUDFLARE_ACCOUNT_ID"
    )

    cloudflare_api_token = os.environ.get(
        "CLOUDFLARE_API_TOKEN"
    )

    if openai_api_key:
        tool_manager.register(
            ImageGenerator(
                api_key=openai_api_key,
            )
        )

    if (
        cloudflare_account_id
        and cloudflare_api_token
    ):
        tool_manager.register(
            CloudflareImageGenerator(
                account_id=cloudflare_account_id,
                api_token=cloudflare_api_token,
            )
        )

    tool_manager.register(
        PDFReader()
    )

    return tool_manager
