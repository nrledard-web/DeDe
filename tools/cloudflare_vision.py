import base64
import os
import requests


class CloudflareVision:

    name = "cloudflare_vision"

    model = (
        "@cf/meta/"
        "llama-3.2-11b-vision-instruct"
    )

    def __init__(self):

        self.account_id = os.getenv(
            "CLOUDFLARE_ACCOUNT_ID",
            "",
        )

        self.api_token = os.getenv(
            "CLOUDFLARE_API_TOKEN",
            "",
        )

    def analyze(
        self,
        image_bytes: bytes,
        prompt: str = "",
    ) -> dict:

        if not self.account_id:
            return {
                "status": "error",
                "error": (
                    "Missing CLOUDFLARE_ACCOUNT_ID."
                ),
            }

        if not self.api_token:
            return {
                "status": "error",
                "error": (
                    "Missing CLOUDFLARE_API_TOKEN."
                ),
            }

        if not image_bytes:
            return {
                "status": "error",
                "error": "No image provided.",
            }

        question = (
            prompt.strip()
            if prompt.strip()
            else (
                "Analyze this image carefully. "
                "Describe what is visibly present. "
                "Separate direct observations from "
                "interpretations or uncertain conclusions."
            )
        )

        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        url = (
            "https://api.cloudflare.com/client/v4/"
            f"accounts/{self.account_id}/ai/run/"
            f"{self.model}"
        )

        headers = {
            "Authorization": (
                f"Bearer {self.api_token}"
            ),
            "Content-Type": "application/json",
        }

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": (
                                    "data:image/jpeg;base64,"
                                    + image_base64
                                ),
                            },
                        },
                    ],
                }
            ]
        }

        try:

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60,
            )

            if response.status_code != 200:

                return {
                    "status": "error",
                    "error": (
                        "Cloudflare Vision error "
                        f"{response.status_code}: "
                        f"{response.text[:500]}"
                    ),
                }

            result = response.json()

            result_data = result.get(
                "result",
                {},
            )

            answer = (
                result_data.get("response")
                or result_data.get("text")
                or ""
            )

            return {
                "status": "success",
                "provider": "cloudflare",
                "model": self.model,
                "analysis": str(answer).strip(),
            }

        except Exception as error:

            return {
                "status": "error",
                "error": str(error),
            }
