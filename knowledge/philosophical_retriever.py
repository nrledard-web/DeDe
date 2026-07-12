"""
DeDe - Philosophical Retriever

Retrieves only the foundational philosophical concepts
relevant to the current user message.

The complete ontology is never injected by default.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from knowledge.philosophical_ontology import (
    PHILOSOPHICAL_ONTOLOGY,
)


class PhilosophicalRetriever:
    """
    Retrieve a compact and relevant subset of DeDe's
    philosophical ontology.
    """

    name = "philosophical_retriever"

    # Fields that may enrich a philosophical node.
    # Unknown fields remain ignored so the ontology can evolve safely.
    CONTENT_FIELDS = [
        "axioms",
        "principles",
        "stages",
        "process",
        "steps",
        "mechanism",
        "examples",
        "counter_examples",
        "misconceptions",
        "confusions",
        "safeguards",
        "ethical_limits",
        "applications",
        "questions",
        "human_stages",
        "ai_stages",
        "checks",
        "standard_closed_loop",
        "anti_coherence_process",
        "well_calibrated_outcomes",
        "poorly_calibrated_outcomes",
    ]

    def retrieve(
        self,
        text: str,
        concept_data: dict[str, Any] | None = None,
        max_nodes: int = 8,
    ) -> dict[str, Any]:
        concept_data = concept_data or {}

        normalized_text = self._normalize(text)

        concepts = concept_data.get(
            "main_concepts",
            [],
        )

        normalized_concepts = {
            self._normalize(str(concept))
            for concept in concepts
            if concept
        }

        scored_nodes: list[tuple[str, float]] = []

        for node_id, node in PHILOSOPHICAL_ONTOLOGY.items():
            score = self._score_node(
                node_id=node_id,
                node=node,
                normalized_text=normalized_text,
                normalized_concepts=normalized_concepts,
            )

            if score > 0:
                scored_nodes.append(
                    (
                        node_id,
                        score,
                    )
                )

        scored_nodes.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        selected_ids = [
            node_id
            for node_id, _score in scored_nodes[:max_nodes]
        ]

        selected_ids = self._expand_relations(
            selected_ids=selected_ids,
            max_nodes=max_nodes,
        )

        selected_nodes = []

        for node_id in selected_ids:
            node = PHILOSOPHICAL_ONTOLOGY.get(
                node_id,
                {},
            )

            if not node:
                continue

            selected_nodes.append(
                self._prepare_node(
                    node_id=node_id,
                    node=node,
                )
            )

        relations = self._collect_relations(
            selected_ids
        )

        prompt_context = self._build_prompt_context(
            selected_nodes=selected_nodes,
            relations=relations,
        )

        return {
            "retriever": self.name,
            "status": (
                "ready"
                if selected_nodes
                else "not_relevant"
            ),
            "query": text,
            "matched_concepts": selected_ids,
            "node_count": len(selected_nodes),
            "nodes": selected_nodes,
            "relations": relations,
            "prompt_context": prompt_context,
            "summary": (
                f"Retrieved {len(selected_nodes)} relevant "
                "foundational philosophical concept(s)."
                if selected_nodes
                else (
                    "No foundational philosophical concept "
                    "was required for this message."
                )
            ),
        }

    def _prepare_node(
        self,
        node_id: str,
        node: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Keep only philosophically useful fields while allowing
        the ontology structure to evolve.
        """

        prepared: dict[str, Any] = {
            "id": node_id,
            "label": node.get(
                "label",
                node_id,
            ),
            "summary": node.get(
                "summary",
                "",
            ),
            "formula": node.get(
                "formula",
            ),
            "relations": node.get(
                "relations",
                [],
            ),
        }

        for field in self.CONTENT_FIELDS:
            value = node.get(field)

            if value:
                prepared[field] = value

        return prepared

    def _score_node(
        self,
        node_id: str,
        node: dict[str, Any],
        normalized_text: str,
        normalized_concepts: set[str],
    ) -> float:
        score = 0.0

        normalized_node_id = self._normalize(
            node_id
        )

        if self._contains_term(
            normalized_text,
            normalized_node_id,
        ):
            score += 3.0

        aliases = node.get(
            "aliases",
            [],
        )

        for alias in aliases:
            normalized_alias = self._normalize(
                str(alias)
            )

            if not normalized_alias:
                continue

            if self._contains_term(
                normalized_text,
                normalized_alias,
            ):
                alias_word_count = len(
                    normalized_alias.split()
                )

                score += (
                    2.5
                    if alias_word_count > 1
                    else 1.5
                )

            if normalized_alias in normalized_concepts:
                score += 1.5

        label = self._normalize(
            str(
                node.get(
                    "label",
                    "",
                )
            )
        )

        if label in normalized_concepts:
            score += 1.5

        return score

    def _contains_term(
        self,
        text: str,
        term: str,
    ) -> bool:
        if not text or not term:
            return False

        if term.isdigit():
            return bool(
                re.search(
                    rf"(?<!\d){re.escape(term)}(?!\d)",
                    text,
                )
            )

        pattern = (
            r"(?<!\w)"
            + re.escape(term)
            + r"(?!\w)"
        )

        return bool(
            re.search(
                pattern,
                text,
            )
        )

    def _expand_relations(
        self,
        selected_ids: list[str],
        max_nodes: int,
    ) -> list[str]:
        expanded = list(
            dict.fromkeys(selected_ids)
        )

        for node_id in list(expanded):
            if len(expanded) >= max_nodes:
                break

            node = PHILOSOPHICAL_ONTOLOGY.get(
                node_id,
                {},
            )

            for relation in node.get(
                "relations",
                [],
            ):
                target = relation.get(
                    "target"
                )

                if (
                    target
                    and target in PHILOSOPHICAL_ONTOLOGY
                    and target not in expanded
                ):
                    expanded.append(target)

                if len(expanded) >= max_nodes:
                    break

        return expanded[:max_nodes]

    def _collect_relations(
        self,
        selected_ids: list[str],
    ) -> list[dict[str, str]]:
        selected_set = set(selected_ids)
        relations = []

        for source_id in selected_ids:
            source = PHILOSOPHICAL_ONTOLOGY.get(
                source_id,
                {},
            )

            for relation in source.get(
                "relations",
                [],
            ):
                target = relation.get(
                    "target",
                    "",
                )

                if target not in selected_set:
                    continue

                relations.append(
                    {
                        "source": source_id,
                        "type": str(
                            relation.get(
                                "type",
                                "related_to",
                            )
                        ),
                        "target": target,
                        "description": str(
                            relation.get(
                                "description",
                                "",
                            )
                        ),
                    }
                )

        return relations

    def _build_prompt_context(
        self,
        selected_nodes: list[dict[str, Any]],
        relations: list[dict[str, str]],
    ) -> str:
        if not selected_nodes:
            return ""

        lines = [
            "DEDE RELEVANT PHILOSOPHICAL CONTEXT",
            "",
            (
                "Use the following as DeDe's official conceptual "
                "framework. Do not replace these definitions with "
                "generic LLM definitions."
            ),
            (
                "When a process, sequence, distinction, example, "
                "misconception or safeguard is supplied, use it "
                "explicitly when it directly answers the question."
            ),
            "",
        ]

        for node in selected_nodes:
            lines.append(
                f'{node["label"]}:'
            )

            summary = str(
                node.get(
                    "summary",
                    "",
                )
                or ""
            ).strip()

            if summary:
                lines.append(
                    f"- definition: {summary}"
                )

            formula = node.get(
                "formula"
            )

            if formula:
                lines.append(
                    f"- formula: {formula}"
                )

            for field in self.CONTENT_FIELDS:
                value = node.get(field)

                if not value:
                    continue

                readable_name = field.replace(
                    "_",
                    " ",
                )

                lines.append(
                    f"- {readable_name}:"
                )

                self._append_value(
                    lines=lines,
                    value=value,
                    indent="  ",
                )

            lines.append("")

        if relations:
            lines.append(
                "Conceptual relations:"
            )

            for relation in relations:
                lines.append(
                    f'- {relation["source"]} '
                    f'--{relation["type"]}--> '
                    f'{relation["target"]}: '
                    f'{relation["description"]}'
                )

            lines.append("")

        lines.extend(
            [
                (
                    "Historical philosophers are conceptual precursors "
                    "or interlocutors unless the source explicitly states "
                    "that they formulated DeDe's concepts."
                ),
                (
                    "Do not claim that Plato, Socrates or another thinker "
                    "invented the term mecroyance."
                ),
                (
                    "Preserve the distinction between a useful reduction "
                    "and a reduction whose limits have been forgotten."
                ),
                (
                    "Memory preserves information. Understanding relates "
                    "information. Continuity of understanding preserves "
                    "the evolution of those relations through time."
                ),
                (
                    "DeDe must accompany thought without replacing its "
                    "author. The person remains responsible for judgment."
                ),
            ]
        )

        return "\n".join(lines)

    def _append_value(
        self,
        lines: list[str],
        value: Any,
        indent: str,
    ) -> None:
        """
        Render strings, lists and dictionaries as compact prompt text.
        """

        if isinstance(value, str):
            lines.append(
                f"{indent}- {value}"
            )
            return

        if isinstance(value, dict):
            for key, item in value.items():
                readable_key = str(key).replace(
                    "_",
                    " ",
                )

                if isinstance(
                    item,
                    (dict, list),
                ):
                    lines.append(
                        f"{indent}- {readable_key}:"
                    )

                    self._append_value(
                        lines=lines,
                        value=item,
                        indent=indent + "  ",
                    )
                else:
                    lines.append(
                        f"{indent}- {readable_key}: {item}"
                    )

            return

        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    rendered_parts = []

                    for key, item_value in item.items():
                        readable_key = str(key).replace(
                            "_",
                            " ",
                        )

                        if not isinstance(
                            item_value,
                            (dict, list),
                        ):
                            rendered_parts.append(
                                f"{readable_key}: {item_value}"
                            )

                    if rendered_parts:
                        lines.append(
                            f"{indent}- "
                            + " | ".join(rendered_parts)
                        )
                    else:
                        self._append_value(
                            lines=lines,
                            value=item,
                            indent=indent,
                        )

                elif isinstance(item, list):
                    self._append_value(
                        lines=lines,
                        value=item,
                        indent=indent,
                    )

                else:
                    lines.append(
                        f"{indent}- {item}"
                    )

            return

        lines.append(
            f"{indent}- {value}"
        )

    def _normalize(
        self,
        value: str,
    ) -> str:
        normalized = unicodedata.normalize(
            "NFKD",
            str(value or ""),
        )

        normalized = "".join(
            character
            for character in normalized
            if not unicodedata.combining(
                character
            )
        )

        normalized = normalized.lower()

        normalized = re.sub(
            r"[^\w\s+=-]",
            " ",
            normalized,
        )

        normalized = re.sub(
            r"\s+",
            " ",
            normalized,
        )

        return normalized.strip()
