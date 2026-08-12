import io
import os
import base64
import requests

from PIL import Image


class CloudflareReferenceImage:

    name = "cloudflare_reference_image"

    model = (
        "@cf/black-forest-labs/"
        "flux-2-klein-9b"
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

    def _prepare_reference(
        self,
        image_bytes: bytes,
    ) -> bytes:

        image = Image.open(
            io.BytesIO(image_bytes)
        )

        image = image.convert("RGB")

        image.thumbnail(
            (511, 511)
        )

        output = io.BytesIO()

        image.save(
            output,
            format="JPEG",
            quality=92,
        )

        return output.getvalue()

    def generate(
        self,
        prompt: str,
        reference_image: bytes,
        width: int = 1024,
        height: int = 1024,
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

        if not reference_image:
            return {
                "status": "error",
                "error": (
                    "No reference image provided."
                ),
            }

        if not prompt.strip():
            return {
                "status": "error",
                "error": "Prompt is empty.",
            }

        try:

            prepared_image = (
                self._prepare_reference(
                    reference_image
                )
            )

            url = (
                "https://api.cloudflare.com/"
                "client/v4/accounts/"
                f"{self.account_id}/ai/run/"
                f"{self.model}"
            )

            headers = {
                "Authorization": (
                    f"Bearer {self.api_token}"
                ),
            }

            files = {
                "input_image_0": (
                    "reference.jpg",
                    prepared_image,
                    "image/jpeg",
                ),
            }

            data = {
                "prompt": prompt,
                "width": str(width),
                "height": str(height),
            }

            response = requests.post(
                url,
                headers=headers,
                files=files,
                data=data,
                timeout=120,
            )

            result = response.json()

            if response.status_code != 200:

                return {
                    "status": "error",
                    "error": (
                        "Cloudflare Reference Image "
                        f"error {response.status_code}: "
                        f"{result}"
                    ),
                }

            result_data = result.get(
                "result",
                {},
            )

            if (
                isinstance(result_data, dict)
                and isinstance(
                    result_data.get("result"),
                    dict,
                )
            ):
                result_data = (
                    result_data["result"]
                )

            image_base64 = ""

            if isinstance(result_data, dict):

                image_base64 = str(
                    result_data.get(
                        "image",
                        "",
                    )
                    or ""
                )

            if not image_base64:

                return {
                    "status": "error",
                    "error": (
                        "Cloudflare returned no "
                        "generated image. "
                        f"Raw response: {result}"
                    ),
                }

            if "," in image_base64:
                image_base64 = (
                    image_base64.split(
                        ",",
                        1,
                    )[1]
                )

            generated_bytes = (
                base64.b64decode(
                    image_base64
                )
            )

            return {
                "status": "success",
                "provider": "cloudflare",
                "model": self.model,
                "image_bytes": generated_bytes,
                "mime_type": "image/png",
            }

        except Exception as error:

            return {
                "status": "error",
                "error": str(error),
            }
