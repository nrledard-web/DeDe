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
        Analyze linguistic anchoring and, when available,
        anchoring supplied by external sources.
        """

        source_analysis = source_analysis or {}
        search_validation = search_validation or {}
        cognitive_comparison = cognitive_comparison or {}

        cleaned = text.lower().strip()

        if not cleaned:
            return self._empty_result()

        components = {
            "empirie": self._score_markers(
                cleaned,
                [
                    "étude",
                    "rapport",
                    "données",
                    "chiffres",
                    "mesure",
                    "observation",
                    "expérience",
                    "selon",
                    "analyse",
                    "résultat",
                ],
            ),
            "reproductibilite": self._score_markers(
                cleaned,
                [
                    "reproductible",
                    "réplicable",
                    "répété",
                    "confirmé par",
                    "testé plusieurs fois",
                    "même résultat",
                ],
            ),
            "falsifiabilite": self._score_markers(
                cleaned,
                [
                    "falsifiable",
                    "réfutable",
                    "vérifiable",
                    "peut être testé",
                    "hypothèse testable",
                    "preuve contraire",
                ],
            ),
            "limites": self._score_markers(
                cleaned,
                [
                    "limite",
                    "limites",
                    "incertain",
                    "incertitude",
                    "nous ne savons pas",
                    "il manque",
                    "reste à vérifier",
                    "prudence",
                    "à confirmer",
                ],
            ),
            "revisabilite": self._score_markers(
                cleaned,
                [
                    "pourrait",
                    "pourraient",
                    "semble",
                    "il faut nuancer",
                    "nuancer",
                    "cependant",
                    "certains",
                    "dans l'état actuel",
                    "révisable",
                    "hypothèse",
                ],
            ),
            "references_concretes": self._score_markers(
                cleaned,
                [
                    "institution",
                    "université",
                    "chercheurs",
                    "experts",
                    "économistes",
                    "laboratoire",
                    "revue",
                    "publication",
                    "source",
                    "référence",
                ],
            ),
            "technicite_realiste": self._score_markers(
                cleaned,
                [
                    "méthode",
                    "protocole",
                    "échantillon",
                    "variable",
                    "modèle",
                    "marge d'erreur",
                    "intervalle",
                    "corrélation",
                    "causalité",
                ],
            ),
            "comparaisons_concretes": self._score_markers(
                cleaned,
                [
                    "comparé à",
                    "par rapport à",
                    "en moyenne",
                    "pourcentage",
                    "%",
                    "fois plus",
                    "fois moins",
                    "avant/après",
                ],
            ),
            "robustesse_quantitative": self._score_markers(
                cleaned,
                [
                    "statistique",
                    "quantitatif",
                    "échantillon",
                    "population",
                    "taux",
                    "médiane",
                    "moyenne",
                    "écart-type",
                    "intervalle de confiance",
                ],
            ),
        }

        speculation = self._score_markers(
            cleaned,
            [
                "va remplacer",
                "il est absolument certain",
                "sans aucun doute",
                "crise sociale majeure",
                "si rien n'est fait immédiatement",
                "révolution sans précédent",
                "étude choc",
                "tout le monde sait",
                "preuve définitive",
                "inévitable",
            ],
        )

        doxa_pressure = self._score_markers(
            cleaned,
            [
                "évident",
                "indiscutable",
                "certain",
                "forcément",
                "jamais",
                "toujours",
                "personne ne peut nier",
                "la vérité est",
            ],
        )

        positive_values = list(components.values())

        positive_anchor = (
            sum(positive_values) / len(positive_values)
            if positive_values
            else 0.0
        )

        penalty = (
            speculation * 0.65
            + doxa_pressure * 0.35
        )

        textual_anchor = max(
            0.0,
            min(
                1.0,
                positive_anchor - (penalty * 0.45),
            ),
        )

        external_anchor = self._compute_external_anchor(
            source_analysis=source_analysis,
            search_validation=search_validation,
            cognitive_comparison=cognitive_comparison,
        )

        external_evidence_available = (
            external_anchor["source_count"] > 0
        )

        if external_evidence_available:
            anchor_score = external_anchor["score"]
            
        else:
            anchor_score = textual_anchor

        anchor_score = max(
            0.0,
            min(1.0, anchor_score),
        )

        epistemic_confidence = (
            self._compute_epistemic_confidence(
                anchor_score=anchor_score,
                components=components,
            )
        )

        if external_evidence_available:
            epistemic_confidence = (
                epistemic_confidence * 0.40
                + external_anchor["confidence"] * 0.60
            )

        epistemic_confidence = max(
            0.0,
            min(1.0, epistemic_confidence),
        )

        hallucination_risk = (
            self._compute_hallucination_risk(
                anchor_score=anchor_score,
                doxa_pressure=doxa_pressure,
                speculation=speculation,
            )
        )

        if external_evidence_available:
            hallucination_risk = (
                hallucination_risk * 0.50
                + external_anchor["comparison_risk"] * 0.50
            )

        hallucination_risk = max(
            0.0,
            min(1.0, hallucination_risk),
        )

        label, color, interpretation = self._classify(
            anchor_score
        )

        return {
            "profile": self.name,
            "status": "ready",
            "score": round(anchor_score, 3),
            "label": label,
            "color": color,
            "interpretation": interpretation,
            "components": {
                **{
                    key: round(value, 3)
                    for key, value in components.items()
                },
                "speculation": round(speculation, 3),
                "doxa_pressure": round(doxa_pressure, 3),
                "textual_anchor": round(
                    textual_anchor,
                    3,
                ),
                "external_anchor": round(
                    external_anchor["score"],
                    3,
                ),
                "source_evidence": round(
                    external_anchor["evidence"],
                    3,
                ),
                "source_relevance": round(
                    external_anchor["relevance"],
                    3,
                ),
                "source_quantity": round(
                    external_anchor["quantity"],
                    3,
                ),
                "response_alignment": round(
                    external_anchor["comparison_score"],
                    3,
                ),
            },
            "external_evidence": external_anchor,
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
                    hallucination_risk=hallucination_risk,
                )
            ),
            "warning": (
                "Un score élevé ne signifie pas que le texte est vrai. "
                "Il indique seulement que le discours semble davantage "
                "contraint par l'expérience, la vérifiabilité et la "
                "reconnaissance de ses limites."
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

    def _score_markers(
        self,
        text: str,
        markers: list[str],
    ) -> float:
        matches = [
            marker
            for marker in markers
            if marker in text
        ]

        if not markers:
            return 0.0

        return min(
            1.0,
            len(matches) / 4,
        )

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
