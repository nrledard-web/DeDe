"""
DeDe - Visual Prompt Compiler

Builds provider-facing image prompts while preserving the
user's request verbatim and making its priority explicit.
"""

from __future__ import annotations


class VisualPromptCompiler:
    """
    Compile stable prompts for DeDe image generators.
    """

    @staticmethod
    def _clean(
        value: str | None,
    ) -> str:
        """
        Normalize one optional prompt component.
        """

        return str(
            value or ""
        ).strip()

    def compile_generation(
        self,
        user_request: str,
        routed_prompt: str | None = None,
    ) -> str:
        """
        Preserve the current request as the source of truth.
        """

        request = self._clean(
            user_request
        )

        routed = self._clean(
            routed_prompt
        )

        if not request:
            return routed

        parts = [
            (
                "CURRENT USER IMAGE REQUEST "
                "— HIGHEST PRIORITY:"
            ),
            request,
            "",
            "EXECUTION RULES:",
            (
                "- Preserve every explicit subject, "
                "action, spatial relationship, visual "
                "constraint and prohibition."
            ),
            (
                "- Do not replace the requested "
                "composition with a portrait or "
                "close-up unless explicitly requested."
            ),
            (
                "- When instructions compete, follow "
                "the current user request above."
            ),
        ]

        # A routed reformulation is useful only when
        # the current request is genuinely elliptical.
        # For an explicit request, adding a second
        # wording could introduce contradictory scene
        # instructions and weaken prompt adherence.

        request_is_elliptical = (
            len(
                request.split()
            )
            <= 5
        )

        if (
            routed
            and routed != request
            and request_is_elliptical
        ):
            parts.extend(
                [
                    "",
                    "OPTIONAL ROUTER DETAILS:",
                    (
                        "Use these only when compatible "
                        "with the current user request:"
                    ),
                    routed,
                ]
            )

        return "\n".join(
            parts
        )

    def compile_reference_generation(
        self,
        user_request: str,
        visual_analysis: str | None = None,
        conversation_context: str | None = None,
    ) -> str:
        """
        Build a reference-image prompt with explicit
        priorities.
        """

        request = self._clean(
            user_request
        )

        analysis = self._clean(
            visual_analysis
        )

        context = self._clean(
            conversation_context
        )

        parts = [
            (
                "CURRENT USER IMAGE REQUEST "
                "— HIGHEST PRIORITY:"
            ),
            request,
            "",
            "REFERENCE IMAGE RULES:",
            (
                "- Use the supplied image as the visual "
                "identity reference."
            ),
            (
                "- Preserve the relevant person's "
                "recognizable facial characteristics "
                "as closely as the reference allows."
            ),
            (
                "- Preserve every explicit action, "
                "pose, spatial relationship, "
                "composition and prohibition in the "
                "current request."
            ),
            (
                "- Do not copy the original background "
                "unless requested."
            ),
            (
                "- Do not turn a requested full scene "
                "into a portrait or close-up."
            ),
        ]

        if analysis:
            parts.extend(
                [
                    "",
                    (
                        "REFERENCE DESCRIPTION "
                        "— IDENTITY SUPPORT ONLY:"
                    ),
                    analysis,
                ]
            )

        if context:
            parts.extend(
                [
                    "",
                    (
                        "RECENT CONTEXT — USE ONLY TO "
                        "RESOLVE AN ELLIPTICAL REQUEST:"
                    ),
                    context,
                ]
            )

        return "\n".join(
            parts
        )
