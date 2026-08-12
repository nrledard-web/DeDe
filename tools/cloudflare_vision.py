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
        mime_type: str = "image/jpeg",
    ) -> dict:

        if not self.account_id:
            return {
                "status": "error",
                "error": "Missing CLOUDFLARE_ACCOUNT_ID.",
            }

        if not self.api_token:
            return {
                "status": "error",
                "error": "Missing CLOUDFLARE_API_TOKEN.",
            }

        if not image_bytes:
            return {
                "status": "error",
                "error": "No image provided.",
            }

        question = (
            prompt.strip()
            if prompt.strip()
            else "Describe this image carefully."
        )

        encoded_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        image_data = (
            f"data:{mime_type};base64,"
            f"{encoded_image}"
        )

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
                    "role": "system",
                    "content": (
                        "You are DeDe Vision. "
                        "Analyze only what is visible "
                        "in the supplied image. "
                        "Separate observations from "
                        "interpretations and uncertainty."
                    ),
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            "image": image_data,
            "max_tokens": 700,
            "temperature": 0.2,
        }

        try:

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60,
            )

            result = response.json()

            if response.status_code != 200:
                return {
                    "status": "error",
                    "error": (
                        "Cloudflare Vision error "
                        f"{response.status_code}: "
                        f"{result}"
                    ),
                }

            result_data = result.get(
                "result",
                {},
            )

            if isinstance(result_data, dict):
                answer = result_data.get(
                    "response",
                    "",
                )
            else:
                answer = str(result_data)

            if not answer:
                return {
                    "status": "error",
                    "error": (
                        "Cloudflare Vision returned "
                        "an empty response."
                    ),
                }

            return {
                "status": "success",
                "provider": "cloudflare",
                "model": self.model,
                "analysis": answer.strip(),
            }

        except Exception as error:
            return {
                "status": "error",
                "error": str(error),
            }
