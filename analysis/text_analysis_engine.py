"""
DeDe - Universal Text Analysis Engine

Provides one common cognitive-analysis interface for text originating from:
- the user;
- web search results;
- documents;
- memory;
- LLM responses;
- DeDe's final answer.

This version is language-neutral.

It no longer uses the legacy lexical DetectorEngine.

Cognitive analysis is derived from DeDe's existing semantic pipeline:

Text
    ↓
ConceptExtractor
    ↓
SemanticEngine
    ↓
SemanticReasoner
    ↓
EstimatorEngine
    ↓
Cognitive Vector

The public output structure remains compatible with:
- CognitiveComparator
- dashboards
- source analysis
- existing DeDe reports
"""

from __future__ import annotations

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace

from knowledge.concept_extractor import ConceptExtractor

from semantic.semantic_engine import SemanticEngine
from semantic.semantic_reasoner import SemanticReasoner

from estimators.estimator_engine import EstimatorEngine

from formulas.doxa_formula_engine import DoxaFormulaEngine

from processing.text_preprocessor import TextPreprocessor


class TextAnalysisEngine:
    """
    Universal language-neutral entry point for cognitive text analysis.

    This engine deliberately avoids language-specific lexical markers.

    Gnosis, Nous, Doxa, Reduction and Revisability are mapped from
    DeDe's semantic cognitive variables:

        Gnosis        ← Grounding
        Nous          ← Integration
        Doxa          ← Closure
        Reduction     ← Reduction
        Revisability  ← derived cognitive mechanics

    These names are preserved for backward compatibility with the
    CognitiveComparator and existing dashboards.
    """

    name = "text_analysis_engine"

    def __init__(
        self,
    ) -> None:

        self.preprocessor = (
            TextPreprocessor()
        )

        self.concept_extractor = (
            ConceptExtractor()
        )

        self.semantic_engine = (
            SemanticEngine()
        )

        self.semantic_reasoner = (
            SemanticReasoner()
        )

        self.estimator_engine = (
            EstimatorEngine()
        )

        self.formula_engine = (
            DoxaFormulaEngine()
        )

    # ======================================================
    # Single Text Analysis
    # ======================================================

    def analyze(
        self,
        text: str,
        source_type: str = "unknown",
        provenance: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze one text while preserving provenance.

        No lexical marker lists are used.

        Parameters
        ----------
        text:
            Text to analyze.

        source_type:
            Origin of the text:
            user, web, document, memory,
            llm, final_response, etc.

        provenance:
            Information about the source:
            URL, provider, title, model,
            document name, etc.

        context:
            Optional structured context.
        """

        provenance = (
            provenance
            or {}
        )

        context = (
            context
            or {}
        )

        normalized_source_type = (
            str(
                source_type
                or "unknown"
            )
            .strip()
            .lower()
        )

        cleaned_text = str(
            text
            or ""
        ).strip()

        if not cleaned_text:

            return self._empty_result(
                source_type=(
                    normalized_source_type
                ),
                provenance=provenance,
            )

        # --------------------------------------------------
        # Structural text processing
        # --------------------------------------------------

        processed = (
            self.preprocessor.process(
                cleaned_text
            )
        )

        # --------------------------------------------------
        # Independent cognitive workspace
        # --------------------------------------------------

        workspace = CognitiveWorkspace(
            text=cleaned_text
        )

        workspace.add_interpretation(
            "analysis_context",
            {
                "source_type": (
                    normalized_source_type
                ),
                "provenance": provenance,
                "context": context,
            },
        )

        # --------------------------------------------------
        # Optional supplied knowledge
        # --------------------------------------------------
        #
        # TextAnalysisEngine may be called independently of
        # the main DeDe knowledge pipeline.
        #
        # If structured knowledge has explicitly been supplied
        # through context, preserve it.
        #
        # Otherwise use a neutral empty knowledge state.
        #
        # Crucially, do not infer evidence from words such as
        # "study", "proof", "source", "data", etc.
        # --------------------------------------------------

        supplied_knowledge = context.get(
            "knowledge",
            {},
        )

        if not isinstance(
            supplied_knowledge,
            dict,
        ):
            supplied_knowledge = {}

        if supplied_knowledge:

            workspace.add_interpretation(
                "knowledge",
                supplied_knowledge,
            )

        else:

            workspace.add_interpretation(
                "knowledge",
                {
                    "found": False,
                    "answer": "",
                    "sources": [],
                    "confidence": 0.0,
                    "status": "not_supplied",
                },
            )

        # --------------------------------------------------
        # Optional supplied source analysis
        # --------------------------------------------------

        supplied_source_analysis = (
            context.get(
                "source_analysis",
                {},
            )
        )

        if isinstance(
            supplied_source_analysis,
            dict,
        ) and supplied_source_analysis:

            workspace.add_interpretation(
                "source_analysis",
                supplied_source_analysis,
            )

        # --------------------------------------------------
        # Language-neutral semantic pipeline
        # --------------------------------------------------

        workspace = (
            self.concept_extractor.run(
                workspace
            )
        )

        workspace = (
            self.semantic_engine.run(
                workspace
            )
        )

        workspace = (
            self.semantic_reasoner.run(
                workspace
            )
        )

        # --------------------------------------------------
        # Cognitive estimators
        # --------------------------------------------------

        workspace = (
            self.estimator_engine.run(
                workspace
            )
        )

        # --------------------------------------------------
        # Secondary cognitive mechanics
        # --------------------------------------------------

        formula_result = (
            self.formula_engine.compute(
                workspace
            )
        )

        # --------------------------------------------------
        # Universal cognitive variables
        # --------------------------------------------------

        grounding = self._safe_level(
            workspace.get(
                "grounding"
            )
        )

        integration = self._safe_level(
            workspace.get(
                "integration"
            )
        )

        closure = self._safe_level(
            workspace.get(
                "closure"
            )
        )

        reduction = self._safe_level(
            workspace.get(
                "reduction"
            )
        )

        formula_core = (
            formula_result.get(
                "core",
                {},
            )
        )

        if not isinstance(
            formula_core,
            dict,
        ):
            formula_core = {}

        revisability = self._safe_level(
            formula_core.get(
                "revisability",
                0.0,
            )
        )

        # --------------------------------------------------
        # Backward-compatible cognitive vector
        # --------------------------------------------------
        #
        # These historical names remain because other
        # components already consume them.
        #
        # They no longer come from lexical English markers.
        # --------------------------------------------------

        cognitive_vector = {
            "gnosis": grounding,
            "nous": integration,
            "doxa": closure,
            "reduction": reduction,
            "revisability": revisability,
        }

        # --------------------------------------------------
        # Mécroyance compatibility layer
        # --------------------------------------------------
        #
        # This is descriptive only.
        #
        # The canonical Mécroyance model used by DeDe remains
        # inside CognitiveTherapyAgent.
        # --------------------------------------------------

        mecroyance_raw = (
            grounding
            + integration
            - closure
        )

        mecroyance_risk = max(
            0.0,
            min(
                1.0,
                (
                    closure
                    + reduction
                    - grounding
                    - integration
                    + 1.0
                )
                / 2.0,
            ),
        )

        mecroyance = {
            "scores": {
                "gnosis": grounding,
                "nous": integration,
                "doxa": closure,
                "reduction": reduction,
                "revisability": (
                    revisability
                ),
                "mecroyance_raw": (
                    mecroyance_raw
                ),
                "mecroyance_risk": (
                    mecroyance_risk
                ),
            },
            "summary": (
                "Language-neutral cognitive position "
                "derived from DeDe's semantic estimators."
            ),
            "canonical": False,
        }

        # --------------------------------------------------
        # Compatibility aliases
        # --------------------------------------------------

        balance = {
            "grounding": grounding,
            "integration": integration,
            "closure": closure,
            "reduction": reduction,
            "revisability": revisability,
            "cognitive_balance": (
                formula_core.get(
                    "cognitive_balance",
                    0.0,
                )
            ),
            "closure_risk": (
                formula_core.get(
                    "closure_risk",
                    0.0,
                )
            ),
        }

        metrics = {
            "core": formula_core,
            "derived": (
                formula_result.get(
                    "derived",
                    {},
                )
            ),
        }

        # --------------------------------------------------
        # Semantic information
        # --------------------------------------------------

        semantic = (
            workspace.interpretations.get(
                "semantic",
                {},
            )
        )

        semantic_reasoning = (
            workspace.interpretations.get(
                "semantic_reasoner",
                {},
            )
        )

        concepts = (
            workspace.interpretations.get(
                "concepts",
                {},
            )
        )

        # --------------------------------------------------
        # Detector-compatible analysis package
        # --------------------------------------------------

        detector_results = {
            "processed_text": {
                "char_count": (
                    processed.char_count
                ),
                "word_count": (
                    processed.word_count
                ),
                "sentence_count": (
                    processed.sentence_count
                ),
                "paragraph_count": (
                    processed.paragraph_count
                ),
                "unique_word_count": (
                    processed.unique_word_count
                ),
                "lexical_diversity": (
                    processed.lexical_diversity
                ),
            },

            "cognitive_vector": (
                cognitive_vector
            ),

            "certainty": {
                "certainty_score": closure,
                "closure_risk": (
                    closure >= 0.75
                ),
                "source": (
                    "semantic_closure_estimator"
                ),
                "language_specific_markers": (
                    False
                ),
            },

            "gnosis": {
                "gnosis_score": grounding,
                "source": (
                    "semantic_grounding_estimator"
                ),
                "language_specific_markers": (
                    False
                ),
            },

            "nous": {
                "nous_score": integration,
                "source": (
                    "semantic_integration_estimator"
                ),
                "language_specific_markers": (
                    False
                ),
            },

            "reduction": {
                "reduction_score": reduction,
                "source": (
                    "semantic_reduction_estimator"
                ),
                "language_specific_markers": (
                    False
                ),
            },

            "revisability": {
                "revisability_score": (
                    revisability
                ),
                "source": (
                    "semantic_formula_engine"
                ),
                "language_specific_markers": (
                    False
                ),
            },

            "mecroyance": mecroyance,

            "balance": balance,

            "metrics": metrics,

            "formulas": {
                "phase2": (
                    formula_result
                )
            },

            "semantic": semantic,

            "semantic_reasoning": (
                semantic_reasoning
            ),

            "concepts": concepts,

            "workspace": (
                workspace.snapshot()
            ),

            "analysis_method": (
                "language_neutral_semantic_pipeline"
            ),

            "language_specific_markers": (
                False
            ),
        }

        summary = self._build_summary(
            detector_results
        )

        return {
            "engine": self.name,
            "status": "ready",

            "source_type": (
                normalized_source_type
            ),

            "provenance": provenance,

            "text": cleaned_text,

            "text_preview": (
                self._build_preview(
                    cleaned_text
                )
            ),

            "analysis": detector_results,

            "summary": summary,

            "analysis_method": (
                "language_neutral_semantic_pipeline"
            ),

            "language_specific_markers": (
                False
            ),
        }

    # ======================================================
    # Multiple Text Analysis
    # ======================================================

    def analyze_many(
        self,
        items: list[dict[str, Any]],
        source_type: str = "unknown",
        shared_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze several text items independently.

        Each item may contain:
        - text
        - provenance
        - context
        - source_type
        """

        shared_context = (
            shared_context
            or {}
        )

        analyses = []

        for index, item in enumerate(
            items
        ):

            if not isinstance(
                item,
                dict,
            ):
                continue

            item_text = str(
                item.get(
                    "text",
                    "",
                )
                or ""
            ).strip()

            if not item_text:
                continue

            item_source_type = (
                item.get(
                    "source_type",
                    source_type,
                )
            )

            item_provenance = {
                "index": index,
                **(
                    item.get(
                        "provenance",
                        {},
                    )
                    or {}
                ),
            }

            item_context = {
                **shared_context,
                **(
                    item.get(
                        "context",
                        {},
                    )
                    or {}
                ),
            }

            analyses.append(
                self.analyze(
                    text=item_text,
                    source_type=(
                        item_source_type
                    ),
                    provenance=(
                        item_provenance
                    ),
                    context=(
                        item_context
                    ),
                )
            )

        return {
            "engine": self.name,

            "status": (
                "ready"
                if analyses
                else "empty"
            ),

            "source_type": source_type,

            "item_count": len(
                analyses
            ),

            "items": analyses,

            "aggregate": (
                self._aggregate(
                    analyses
                )
            ),

            "analysis_method": (
                "language_neutral_semantic_pipeline"
            ),

            "language_specific_markers": (
                False
            ),
        }

    # ======================================================
    # Summary
    # ======================================================

    def _build_summary(
        self,
        detector_results: dict[str, Any],
    ) -> dict[str, Any]:

        vector = (
            detector_results.get(
                "cognitive_vector",
                {},
            )
        )

        metrics = (
            detector_results.get(
                "metrics",
                {},
            )
        )

        formulas = (
            detector_results.get(
                "formulas",
                {},
            )
        )

        balance = (
            detector_results.get(
                "balance",
                {},
            )
        )

        mecroyance = (
            detector_results.get(
                "mecroyance",
                {},
            )
        )

        return {
            "gnosis": (
                vector.get(
                    "gnosis"
                )
            ),

            "nous": (
                vector.get(
                    "nous"
                )
            ),

            "doxa": (
                vector.get(
                    "doxa"
                )
            ),

            "reduction": (
                vector.get(
                    "reduction"
                )
            ),

            "revisability": (
                vector.get(
                    "revisability"
                )
            ),

            "balance": balance,

            "mecroyance": mecroyance,

            "metrics": metrics,

            "formulas": formulas,

            "analysis_method": (
                "language_neutral_semantic_pipeline"
            ),
        }

    # ======================================================
    # Aggregation
    # ======================================================

    def _aggregate(
        self,
        analyses: list[
            dict[str, Any]
        ],
    ) -> dict[str, Any]:

        vector_keys = [
            "gnosis",
            "nous",
            "doxa",
            "reduction",
            "revisability",
        ]

        values = {
            key: []
            for key in vector_keys
        }

        for analysis_result in analyses:

            cognitive_vector = (
                analysis_result
                .get(
                    "analysis",
                    {},
                )
                .get(
                    "cognitive_vector",
                    {},
                )
            )

            for key in vector_keys:

                value = (
                    cognitive_vector.get(
                        key
                    )
                )

                if isinstance(
                    value,
                    (
                        int,
                        float,
                    ),
                ):

                    values[
                        key
                    ].append(
                        float(
                            value
                        )
                    )

        averages = {}

        for (
            key,
            collected,
        ) in values.items():

            averages[key] = (
                sum(
                    collected
                )
                / len(
                    collected
                )
                if collected
                else None
            )

        return {
            "analyzed_item_count": (
                len(
                    analyses
                )
            ),

            "average_cognitive_vector": (
                averages
            ),
        }

    # ======================================================
    # Helpers
    # ======================================================

    def _build_preview(
        self,
        text: str,
        max_length: int = 280,
    ) -> str:

        if len(
            text
        ) <= max_length:
            return text

        return (
            text[
                :max_length
            ].rstrip()
            + "..."
        )

    @staticmethod
    def _safe_level(
        value: Any,
    ) -> float:

        try:
            level = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):
            return 0.0

        if level > 1.0:
            level = (
                level
                / 100.0
            )

        return max(
            0.0,
            min(
                1.0,
                level,
            ),
        )

    def _empty_result(
        self,
        source_type: str,
        provenance: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "engine": self.name,
            "status": "empty",
            "source_type": source_type,
            "provenance": provenance,
            "text": "",
            "text_preview": "",
            "analysis": {},
            "summary": {},
            "analysis_method": (
                "language_neutral_semantic_pipeline"
            ),
            "language_specific_markers": (
                False
            ),
        }
