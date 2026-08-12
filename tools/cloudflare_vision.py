import base64
import os
import requests


class CloudflareVision:

    name = "cloudflare_vision"

    model = (
        "@cf/moondream/"
        "moondream3.1-9B-A2B"
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

        user_question = (
            prompt.strip()
            if prompt.strip()
            else "Describe this image."
        )
        
        question = (
            "Analyze the supplied image carefully.\n\n"
            f"User request: {user_question}\n\n"
            "Rules:\n"
            "- Describe only information actually visible "
            "in the image.\n"
            "- Never invent text, numbers, names, objects, "
            "or relationships that cannot be read clearly.\n"
            "- If text is unclear, incomplete, or too small, "
            "say that it cannot be read reliably.\n"
            "- Do not reconstruct missing text from context.\n"
            "- Distinguish visible observations from "
            "interpretation.\n"
            "- When reading text, preserve the original "
            "wording as closely as possible.\n"
            "- Avoid repetition.\n"
            "- Answer in the same language as the user's "
            "request whenever possible.\n\n"
            "Return a concise, factual visual analysis."
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
            "task": "query",
            "image": image_data,
            "question": question,
            "reasoning": False,
            "temperature": 0.2,
            "max_tokens": 800,
            "stream": False,
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
                result,
            )
            
            if (
                isinstance(result_data, dict)
                and isinstance(
                    result_data.get("result"),
                    dict,
                )
            ):
                result_data = result_data["result"]
            
            answer = ""
            
            if isinstance(result_data, dict):
            
                answer = str(
                    result_data.get(
                        "answer",
                        "",
                    )
                    or result_data.get(
                        "caption",
                        "",
                    )
                    or result_data.get(
                        "response",
                        "",
                    )
                    or ""
                ).strip()
            
            elif isinstance(result_data, str):
            
                answer = result_data.strip()
            
            
            if not answer:
            
                return {
                    "status": "error",
                    "error": (
                        "Cloudflare Vision returned "
                        "no visual analysis. "
                        f"Raw response: {result}"
                    ),
                }

            return {
                "status": "success",
                "provider": "cloudflare",
                "model": self.model,
                "analysis": answer,
            }

        except Exception as error:

            return {
                "status": "error",
                "error": str(error),
            }
