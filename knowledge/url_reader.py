"""
DeDe - URL Reader

Reads a supplied URL and extracts basic page text.
This component does not reason.
It only retrieves and normalizes external page content.
"""

from typing import Any
import requests
from bs4 import BeautifulSoup


class URLReader:

    name = "url_reader"

    def read(
        self,
        url: str,
        timeout: int = 12,
    ) -> dict[str, Any]:

        if not url:
            return {
                "reader": self.name,
                "status": "empty_url",
                "url": url,
                "title": "",
                "text": "",
                "summary": "No URL supplied.",
            }

        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 DeDe Cognitive Daimon URL Reader"
                    )
                },
            )

            if response.status_code >= 400:
                return {
                    "reader": self.name,
                    "status": "http_error",
                    "url": url,
                    "title": "",
                    "text": "",
                    "http_status": response.status_code,
                    "summary": (
                        f"URL returned HTTP status {response.status_code}."
                    ),
                }

            soup = BeautifulSoup(
                response.text,
                "html.parser",
            )

            for tag in soup([
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "aside",
            ]):
                tag.decompose()

            title = ""

            if soup.title and soup.title.string:
                title = soup.title.string.strip()

            paragraphs = [
                p.get_text(" ", strip=True)
                for p in soup.find_all(["p", "h1", "h2", "h3", "li"])
            ]

            text = "\n".join(
                item
                for item in paragraphs
                if item
            )

            text = text[:12000]

            return {
                "reader": self.name,
                "status": "success",
                "url": url,
                "title": title,
                "text": text,
                "char_count": len(text),
                "summary": (
                    f"URL read successfully. Extracted {len(text)} characters."
                ),
            }

        except Exception as error:
            return {
                "reader": self.name,
                "status": "error",
                "url": url,
                "title": "",
                "text": "",
                "error": str(error),
                "summary": "URL reading failed.",
            }
