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

    def analyze(self, text: str) -> dict[str, Any]:
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

        positive_anchor = sum(positive_values) / len(positive_values)

        penalty = (speculation * 0.65) + (doxa_pressure * 0.35)

        anchor_score = max(
            0.0,
            min(
                1.0,
                positive_anchor - (penalty * 0.45),
            ),
        )

        epistemic_confidence = self._compute_epistemic_confidence(
            anchor_score=anchor_score,
            components=components,
        )

        hallucination_risk = self._compute_hallucination_risk(
            anchor_score=anchor_score,
            doxa_pressure=doxa_pressure,
            speculation=speculation,
        )

        label, color, interpretation = self._classify(anchor_score)

        return {
            "profile": self.name,
            "status": "ready",
            "score": round(anchor_score, 3),
            "label": label,
            "color": color,
            "interpretation": interpretation,
            "components": {
                **{k: round(v, 3) for k, v in components.items()},
                "speculation": round(speculation, 3),
                "doxa_pressure": round(doxa_pressure, 3),
            },
            "epistemic_confidence": round(epistemic_confidence, 3),
            "hallucination_risk": round(hallucination_risk, 3),
            "governor_action": self._suggest_governor_action(
                anchor_score=anchor_score,
                hallucination_risk=hallucination_risk,
            ),
            "warning": (
                "Un score élevé ne signifie pas que le texte est vrai. "
                "Il indique seulement que le discours semble davantage "
                "contraint par l'expérience, la vérifiabilité et la "
                "reconnaissance de ses limites."
            ),
        }

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

        # Soft saturation: a few markers are enough to raise the signal,
        # but repetition does not inflate the score indefinitely.
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
        revisability = components.get("revisabilite", 0.0)
        falsifiability = components.get("falsifiabilite", 0.0)
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
                "Le discours est très peu contraint par l'expérience ou la vérification.",
            )

        if score < 0.40:
            return (
                "Fragile",
                "orange",
                "Quelques éléments d'ancrage existent, mais la spéculation ou l'affirmation dominent.",
            )

        if score < 0.60:
            return (
                "Modéré",
                "yellow",
                "Le discours présente un ancrage partiel au réel.",
            )

        if score < 0.80:
            return (
                "Fort",
                "white",
                "Le discours est relativement stabilisé par l'expérience et les limites reconnues.",
            )

        return (
            "Très fort",
            "blue",
            "Le discours est fortement contraint par l'expérience, la reproductibilité ou la falsifiabilité.",
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
            "epistemic_confidence": 0.0,
            "hallucination_risk": 0.0,
            "governor_action": "no_action",
        }
