"""
DeDe / DOXA - Real World Anchor

Measures how strongly a discourse remains constrained by
empirical grounding, reproducibility, falsifiability, limits,
revisability and concrete references.

It does not measure truth.
It measures epistemic anchoring.
"""

from __future__ import annotations

from typing import Any


class RealWorldAnchor:
    """
    Epistemic anchoring estimator.
    """

    name = "real_world_anchor"

    def analyze(
        self,
        text: str,
        source_analysis: dict[str, Any] | None = None,
        search_validation: dict[str, Any] | None = None,
        cognitive_comparison: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Estimate epistemic anchoring from actually available evidence.

        RealWorldAnchor deliberately avoids language-specific
        lexical markers.

        Mentioning words equivalent to "study", "proof", "certain",
        "expert" or "data" must not by itself increase or decrease
        epistemic anchoring.

        When external evidence exists, anchoring is derived primarily
        from source evidence, relevance, independence, validation
        and cognitive comparison.

        When no external evidence exists, the result remains
        deliberately conservative rather than inventing grounding
        from the vocabulary of the discourse.
        """

        source_analysis = (
            source_analysis
            or {}
        )

        search_validation = (
            search_validation
            or {}
        )

        cognitive_comparison = (
            cognitive_comparison
            or {}
        )

        cleaned = str(
            text
            or ""
        ).strip()

        if not cleaned:
            return self._empty_result()

        # --------------------------------------------------
        # External epistemic anchor
        # --------------------------------------------------

        external_anchor = (
            self._compute_external_anchor(
                source_analysis=source_analysis,
                search_validation=search_validation,
                cognitive_comparison=cognitive_comparison,
            )
        )

        external_evidence_available = (
            external_anchor.get(
                "source_count",
                0,
            )
            > 0
        )

        # --------------------------------------------------
        # Language-neutral structural state
        # --------------------------------------------------
        #
        # The current RealWorldAnchor interface does not yet
        # receive the CognitiveWorkspace or SemanticReasoner.
        #
        # Therefore it must NOT invent textual grounding from
        # language-specific expressions.
        #
        # Until semantic signals are explicitly supplied,
        # textual anchoring remains conservative.
        # --------------------------------------------------

        textual_anchor = 0.10

        textual_confidence = 0.10

        # These fields are retained for backward compatibility
        # with dashboards and downstream consumers.
        #
        # They are no longer inferred from French vocabulary.

        components = {
            "empirie": 0.0,
            "reproductibilite": 0.0,
            "falsifiabilite": 0.0,
            "limites": 0.0,
            "revisabilite": 0.0,
            "references_concretes": 0.0,
            "technicite_realiste": 0.0,
            "comparaisons_concretes": 0.0,
            "robustesse_quantitative": 0.0,
        }

        speculation = 0.0
        doxa_pressure = 0.0

        # --------------------------------------------------
        # Final anchor
        # --------------------------------------------------

        if external_evidence_available:

            anchor_score = self._normalize_score(
                external_anchor.get(
                    "score",
                    0.0,
                )
            )

            epistemic_confidence = self._normalize_score(
                external_anchor.get(
                    "confidence",
                    0.0,
                )
            )

        else:

            anchor_score = textual_anchor
            epistemic_confidence = (
                textual_confidence
            )

        anchor_score = max(
            0.0,
            min(
                1.0,
                anchor_score,
            ),
        )

        epistemic_confidence = max(
            0.0,
            min(
                1.0,
                epistemic_confidence,
            ),
        )

        # --------------------------------------------------
        # Hallucination / unsupported-extension risk
        # --------------------------------------------------
        #
        # Without lexical markers, risk is based on the
        # absence or weakness of grounding and on cognitive
        # comparison warnings when they exist.
        # --------------------------------------------------

        comparison_risk = self._normalize_score(
            external_anchor.get(
                "comparison_risk",
                0.0,
            )
        )

        if external_evidence_available:

            hallucination_risk = (
                (1.0 - anchor_score) * 0.65
                + comparison_risk * 0.35
            )

        else:

            # No external grounding means DeDe should remain
            # epistemically cautious, but absence of evidence
            # is not proof that the claim is false.
            hallucination_risk = 0.60

        hallucination_risk = max(
            0.0,
            min(
                1.0,
                hallucination_risk,
            ),
        )

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        label, color, interpretation = (
            self._classify(
                anchor_score
            )
        )

        # --------------------------------------------------
        # Result
        # --------------------------------------------------

        return {
            "profile": self.name,
            "status": "ready",

            "score": round(
                anchor_score,
                3,
            ),

            "label": label,
            "color": color,

            "interpretation": (
                interpretation
            ),

            "components": {
                **components,

                "speculation": (
                    speculation
                ),

                "doxa_pressure": (
                    doxa_pressure
                ),

                "textual_anchor": round(
                    textual_anchor,
                    3,
                ),

                "external_anchor": round(
                    self._normalize_score(
                        external_anchor.get(
                            "score",
                            0.0,
                        )
                    ),
                    3,
                ),

                "source_evidence": round(
                    self._normalize_score(
                        external_anchor.get(
                            "evidence",
                            0.0,
                        )
                    ),
                    3,
                ),

                "source_relevance": round(
                    self._normalize_score(
                        external_anchor.get(
                            "relevance",
                            0.0,
                        )
                    ),
                    3,
                ),

                "source_independence": round(
                    self._normalize_score(
                        external_anchor.get(
                            "independence",
                            0.0,
                        )
                    ),
                    3,
                ),

                "source_quantity": round(
                    self._normalize_score(
                        external_anchor.get(
                            "quantity",
                            0.0,
                        )
                    ),
                    3,
                ),

                "response_alignment": round(
                    self._normalize_score(
                        external_anchor.get(
                            "comparison_score",
                            0.0,
                        )
                    ),
                    3,
                ),

                "language_specific_markers": (
                    False
                ),
            },

            "external_evidence": (
                external_anchor
            ),

            "external_evidence_available": (
                external_evidence_available
            ),

            "epistemic_confidence": round(
                epistemic_confidence,
                3,
            ),

            "hallucination_risk": round(
                hallucination_risk,
                3,
            ),

            "governor_action": (
                self._suggest_governor_action(
                    anchor_score=anchor_score,
                    hallucination_risk=(
                        hallucination_risk
                    ),
                )
            ),

            "warning": (
                "A high score does not mean that a claim is true. "
                "RealWorldAnchor measures available epistemic anchoring. "
                "When external evidence is unavailable, DeDe deliberately "
                "keeps the anchor conservative instead of inferring grounding "
                "from language-specific vocabulary."
            ),
        }

    def _compute_external_anchor(
        self,
        source_analysis: dict[str, Any],
        search_validation: dict[str, Any],
        cognitive_comparison: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Convert the existing source analysis into
        an external epistemic anchoring score.
        """

        sources = source_analysis.get(
            "sources",
            [],
        )

        if not isinstance(sources, list):
            sources = []

        source_count = len(sources)

        evidence_values = []
        relevance_values = []
        independence_values = []
        commercial_pressure_values = []
        ideological_pressure_values = []

        for source in sources:
            if not isinstance(source, dict):
                continue

            analysis = source.get(
                "analysis",
                {},
            )

            if not isinstance(analysis, dict):
                continue

            evidence_values.append(
                self._normalize_score(
                    analysis.get(
                        "evidence_level",
                        0.0,
                    )
                )
            )

            relevance_values.append(
                self._normalize_score(
                    analysis.get(
                        "relevance",
                        0.0,
                    )
                )
            )

            independence_values.append(
                self._normalize_score(
                    analysis.get(
                        "independence",
                        0.0,
                    )
                )
            )

            commercial_pressure_values.append(
                self._normalize_score(
                    analysis.get(
                        "commercial_pressure",
                        0.0,
                    )
                )
            )

            ideological_pressure_values.append(
                self._normalize_score(
                    analysis.get(
                        "ideological_pressure",
                        0.0,
                    )
                )
            )

        evidence = self._average(
            evidence_values
        )

        relevance = self._average(
            relevance_values
        )

        independence = self._average(
            independence_values
        )

        commercial_pressure = self._average(
            commercial_pressure_values
        )

        ideological_pressure = self._average(
            ideological_pressure_values
        )

        if source_count <= 0:
            quantity = 0.0
        elif source_count == 1:
            quantity = 0.30
        elif source_count == 2:
            quantity = 0.50
        elif source_count == 3:
            quantity = 0.70
        elif source_count == 4:
            quantity = 0.85
        else:
            quantity = 1.0

        validation_score = self._validation_score(
            search_validation
        )

        if (
            validation_score == 0.0
            and source_count > 0
        ):
            validation_score = 1.0

        (
            comparison_score,
            comparison_risk,
            warning_count,
        ) = self._comparison_score(
            cognitive_comparison
        )

        quality_score = (
            evidence * 0.30
            + relevance * 0.25
            + independence * 0.20
            + quantity * 0.15
            + validation_score * 0.10
        )

        pressure_penalty = (
            commercial_pressure * 0.40
            + ideological_pressure * 0.40
        )

        score = (
            quality_score
            - pressure_penalty * 0.20
        )

        score = (
            score * 0.90
            + comparison_score * 0.10
        )

        score = max(
            0.0,
            min(1.0, score),
        )

        confidence = (
            evidence * 0.30
            + relevance * 0.20
            + independence * 0.20
            + quantity * 0.10
            + validation_score * 0.10
            + comparison_score * 0.10
        )

        confidence = max(
            0.0,
            min(1.0, confidence),
        )

        return {
            "status": (
                "ready"
                if source_count > 0
                else "unavailable"
            ),
            "score": round(score, 3),
            "confidence": round(
                confidence,
                3,
            ),
            "source_count": source_count,
            "evidence": round(
                evidence,
                3,
            ),
            "relevance": round(
                relevance,
                3,
            ),
            "independence": round(
                independence,
                3,
            ),
            "quantity": round(
                quantity,
                3,
            ),
            "commercial_pressure": round(
                commercial_pressure,
                3,
            ),
            "ideological_pressure": round(
                ideological_pressure,
                3,
            ),
            "validation_score": round(
                validation_score,
                3,
            ),
            "comparison_score": round(
                comparison_score,
                3,
            ),
            "comparison_risk": round(
                comparison_risk,
                3,
            ),
            "warning_count": warning_count,
        }

    def _validation_score(
        self,
        search_validation: dict[str, Any],
    ) -> float:
        if not search_validation:
            return 0.0

        valid = search_validation.get("valid")

        if valid is True:
            return 1.0

        if valid is False:
            return 0.0

        status = str(
            search_validation.get("status", "")
        ).lower()

        if status in {
            "ready",
            "success",
            "valid",
            "validated",
        }:
            return 1.0

        if status in {
            "partial",
            "warning",
            "uncertain",
        }:
            return 0.50

        return 0.25

    def _comparison_score(
        self,
        cognitive_comparison: dict[str, Any],
    ) -> tuple[float, float, int]:
        if not cognitive_comparison:
            return 0.0, 0.50, 0

        warnings = cognitive_comparison.get(
            "warnings",
            [],
        )

        if isinstance(warnings, list):
            warning_count = len(warnings)
        else:
            warning_count = self._safe_int(
                cognitive_comparison.get(
                    "warning_count",
                    0,
                )
            )

        status = str(
            cognitive_comparison.get("status", "")
        ).lower()

        if status == "ready":
            base_score = 1.0
        elif status in {
            "partial",
            "warning",
        }:
            base_score = 0.60
        else:
            base_score = 0.25

        warning_penalty = min(
            1.0,
            warning_count * 0.20,
        )

        score = max(
            0.0,
            base_score - warning_penalty,
        )

        risk = warning_penalty

        return score, risk, warning_count

    def _average(
        self,
        values: list[float],
    ) -> float:
        if not values:
            return 0.0

        return sum(values) / len(values)

    def _normalize_score(
        self,
        value: Any,
    ) -> float:
        """
        Accept either 0–1 values or percentages such as 84.
        """

        try:
            score = float(value)
        except (TypeError, ValueError):
            return 0.0

        if score > 1.0:
            score = score / 100.0

        return max(
            0.0,
            min(1.0, score),
        )

    def _safe_int(
        self,
        value: Any,
    ) -> int:
        if isinstance(value, list):
            return len(value)

        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _compute_epistemic_confidence(
        self,
        anchor_score: float,
        components: dict[str, float],
    ) -> float:
        limits = components.get("limites", 0.0)
        revisability = components.get(
            "revisabilite",
            0.0,
        )
        falsifiability = components.get(
            "falsifiabilite",
            0.0,
        )
        empirical = components.get("empirie", 0.0)

        return max(
            0.0,
            min(
                1.0,
                (
                    anchor_score
                    + limits
                    + revisability
                    + falsifiability
                    + empirical
                )
                / 5,
            ),
        )

    def _compute_hallucination_risk(
        self,
        anchor_score: float,
        doxa_pressure: float,
        speculation: float,
    ) -> float:
        expressive_certainty = max(
            doxa_pressure,
            speculation,
        )

        return max(
            0.0,
            min(
                1.0,
                expressive_certainty * (1 - anchor_score),
            ),
        )

    def _suggest_governor_action(
        self,
        anchor_score: float,
        hallucination_risk: float,
    ) -> str:
        if hallucination_risk >= 0.70:
            return "search_or_block_confident_answer"

        if hallucination_risk >= 0.45:
            return "soften_answer_and_add_limits"

        if anchor_score < 0.30:
            return "add_uncertainty_or_request_verification"

        return "answer_allowed"

    def _classify(
        self,
        score: float,
    ) -> tuple[str, str, str]:
        if score < 0.20:
            return (
                "Très faible",
                "red",
                (
                    "Le discours est très peu contraint "
                    "par l'expérience ou la vérification."
                ),
            )

        if score < 0.40:
            return (
                "Fragile",
                "orange",
                (
                    "Quelques éléments d'ancrage existent, "
                    "mais la spéculation ou l'affirmation dominent."
                ),
            )

        if score < 0.60:
            return (
                "Modéré",
                "yellow",
                (
                    "Le discours présente un ancrage "
                    "partiel au réel."
                ),
            )

        if score < 0.80:
            return (
                "Fort",
                "white",
                (
                    "Le discours est relativement stabilisé "
                    "par l'expérience et les limites reconnues."
                ),
            )

        return (
            "Très fort",
            "blue",
            (
                "Le discours est fortement contraint par "
                "l'expérience, la reproductibilité ou "
                "la falsifiabilité."
            ),
        )

    def _empty_result(self) -> dict[str, Any]:
        return {
            "profile": self.name,
            "status": "empty",
            "score": 0.0,
            "label": "Indéterminé",
            "color": "gray",
            "interpretation": "Aucun texte à analyser.",
            "components": {},
            "external_evidence": {
                "status": "unavailable",
                "score": 0.0,
                "confidence": 0.0,
                "source_count": 0,
            },
            "epistemic_confidence": 0.0,
            "hallucination_risk": 0.0,
            "governor_action": "no_action",
        }
