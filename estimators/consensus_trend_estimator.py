"""
DeDe - Consensus Trend Estimator

Measures the degree to which a discourse appears stabilized
by collective agreement, repetition, institutional authority
or ideological convergence.

It does not measure truth.

A high consensus trend means that a claim, representation
or interpretive frame appears strongly supported by collective
alignment.

This may coexist with either strong or weak empirical grounding.
"""

from __future__ import annotations

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class ConsensusTrendEstimator:
    """
    Estimate collective consensus pressure independently
    from truth or empirical grounding.
    """

    name = "consensus_trend"

    def analyze(
        self,
        workspace: CognitiveWorkspace,
    ) -> dict[str, Any]:

        text = str(
            workspace.text or ""
        ).lower().strip()

        if not text:
            result = self._empty_result()

            workspace.set(
                self.name,
                0.0,
                signals=result,
            )

            return result

        # --------------------------------------------------
        # Collective agreement markers
        # --------------------------------------------------

        collective_agreement = self._score_markers(
            text,
            [
                "tout le monde sait",
                "tout le monde pense",
                "tout le monde est d'accord",
                "la majorité pense",
                "la majorité considère",
                "la plupart des gens",
                "consensus",
                "consensus général",
                "opinion générale",
                "opinion dominante",
                "idée dominante",
                "pensée dominante",
                "on sait que",
                "il est admis que",
                "il est reconnu que",
                "communément admis",
                "widely accepted",
                "everyone knows",
                "most people believe",
                "general consensus",
                "widely believed",
                "commonly accepted",
            ],
        )

        # --------------------------------------------------
        # Institutional authority markers
        # --------------------------------------------------

        institutional_authority = self._score_markers(
            text,
            [
                "les experts",
                "les scientifiques",
                "les économistes",
                "les historiens",
                "les autorités",
                "les institutions",
                "les médias",
                "l'université",
                "la communauté scientifique",
                "la communauté internationale",
                "les spécialistes",
                "les professionnels",
                "experts agree",
                "scientists agree",
                "authorities say",
                "academic consensus",
                "scientific consensus",
            ],
        )

        # --------------------------------------------------
        # Social repetition / normalization
        # --------------------------------------------------

        repetition_normalization = self._score_markers(
            text,
            [
                "toujours entendu",
                "on nous dit",
                "on nous répète",
                "depuis toujours",
                "tout le monde répète",
                "c'est connu",
                "c'est normal",
                "c'est évident pour tous",
                "on apprend que",
                "on enseigne que",
                "everyone says",
                "we are told",
                "commonly repeated",
                "always been taught",
            ],
        )

        # --------------------------------------------------
        # Group / ideological identity pressure
        # --------------------------------------------------

        group_alignment = self._score_markers(
            text,
            [
                "nous pensons",
                "nous croyons",
                "notre mouvement",
                "notre parti",
                "notre communauté",
                "notre religion",
                "notre doctrine",
                "notre idéologie",
                "les vrais",
                "ceux qui savent",
                "les gens comme nous",
                "our movement",
                "our party",
                "our community",
                "our ideology",
                "people like us",
            ],
        )

        # --------------------------------------------------
        # Dissent exclusion
        # --------------------------------------------------

        dissent_exclusion = self._score_markers(
            text,
            [
                "personne ne peut nier",
                "seuls les ignorants",
                "seuls les idiots",
                "ceux qui ne sont pas d'accord",
                "aucune personne sérieuse",
                "il n'y a pas de débat",
                "le débat est clos",
                "toute autre opinion est fausse",
                "no serious person",
                "no one can deny",
                "there is no debate",
                "debate is settled",
                "any other view is wrong",
            ],
        )

        # --------------------------------------------------
        # Consensus trend score
        # --------------------------------------------------
        #
        # Consensus is NOT truth.
        #
        # This score measures stabilization by collective
        # agreement and conformity pressure.
        # --------------------------------------------------

        score = (
            collective_agreement * 0.30
            + institutional_authority * 0.20
            + repetition_normalization * 0.15
            + group_alignment * 0.15
            + dissent_exclusion * 0.20
        )

        score = max(
            0.0,
            min(
                1.0,
                score,
            ),
        )

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        if score >= 0.75:
            level = "very_high"

        elif score >= 0.55:
            level = "high"

        elif score >= 0.35:
            level = "moderate"

        elif score >= 0.15:
            level = "low"

        else:
            level = "minimal"

        result = {
            "estimator": self.name,
            "status": "ready",
            "score": round(
                score,
                3,
            ),
            "level": level,
            "components": {
                "collective_agreement": round(
                    collective_agreement,
                    3,
                ),
                "institutional_authority": round(
                    institutional_authority,
                    3,
                ),
                "repetition_normalization": round(
                    repetition_normalization,
                    3,
                ),
                "group_alignment": round(
                    group_alignment,
                    3,
                ),
                "dissent_exclusion": round(
                    dissent_exclusion,
                    3,
                ),
            },
            "principle": (
                "Consensus Trend measures collective stabilization, "
                "not truth. A high consensus score may coexist with "
                "either strong or weak empirical grounding."
            ),
        }

        workspace.set(
            self.name,
            score,
            signals=result,
        )

        return result

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
            len(matches) / 3.0,
        )

    def _empty_result(
        self,
    ) -> dict[str, Any]:

        return {
            "estimator": self.name,
            "status": "empty",
            "score": 0.0,
            "level": "minimal",
            "components": {},
            "principle": (
                "Consensus Trend measures collective stabilization, "
                "not truth."
            ),
        }
