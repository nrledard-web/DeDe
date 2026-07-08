"""
DeDe - URL Reader

Reads supplied URLs and extracts page text.
"""

from typing import Any
import re
import requests
from bs4 import BeautifulSoup


class URLReader:

    name = "url_reader"

    def extract_urls(
        self,
        text: str,
    ) -> list[str]:

        urls = re.findall(
            r"https?://[^\s]+",
            text,
        )

        return [
            url.rstrip(".,);]")
            for url in urls
        ]

    def read_first_url(
        self,
        text: str,
    ) -> dict[str, Any]:

        urls = self.extract_urls(text)

        if not urls:
            return {
                "reader": self.name,
                "status": "no_url",
                "url": "",
                "title": "",
                "text": "",
                "summary": "No URL detected.",
            }

        return self.read(urls[0])

    def read(
        self,
        url: str,
        timeout: int = 15,
    ) -> dict[str, Any]:

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
                    "summary": f"URL returned HTTP {response.status_code}.",
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
                "noscript",
            ]):
                tag.decompose()

            title = ""

            if soup.title and soup.title.string:
                title = soup.title.string.strip()

            parts = []

            for tag in soup.find_all(["h1", "h2", "h3", "p", "li"]):
                content = tag.get_text(" ", strip=True)

                if content:
                    parts.append(content)

            page_text = "\n".join(parts)

            page_text = page_text[:18000]

            return {
                "reader": self.name,
                "status": "success",
                "url": url,
                "title": title,
                "text": page_text,
                "char_count": len(page_text),
                "summary": (
                    f"URL read successfully. Extracted {len(page_text)} characters."
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
