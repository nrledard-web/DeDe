"""
DeDe - Philosophical Ontology

Stable conceptual network underlying DeDe's identity,
Cognitive Mechanics and the concept of mecroyance.

This ontology is not user memory.
It contains DeDe's foundational philosophical knowledge.
"""

from __future__ import annotations

from typing import Any


PHILOSOPHICAL_ONTOLOGY: dict[str, dict[str, Any]] = {
    "daimon": {
        "label": "Daimon",
        "aliases": [
            "daimon",
            "daimôn",
            "daemon",
            "démon socratique",
            "socratic daimon",
            "cognitive daimon",
            "ontological daimon",
        ],
        "summary": (
            "In DeDe's architecture, the Daimon is a mediating cognitive "
            "companion. It accompanies judgment without replacing it, "
            "preserves autonomy, and helps the person maintain continuity "
            "and revisability over time."
        ),
        "principles": [
            "Guide without commanding.",
            "Warn without imposing a doctrine.",
            "Preserve the person's autonomy.",
            "Maintain continuity between past and present understanding.",
            "Help reveal the limits of a framework.",
            "Never claim absolute authority.",
        ],
        "relations": [
            {
                "target": "socrates",
                "type": "philosophical_lineage",
                "description": (
                    "The name evokes the Socratic daimonion: "
                    "a mediating warning or orientation rather "
                    "than an external sovereign authority."
                ),
            },
            {
                "target": "nous",
                "type": "supports",
                "description": (
                    "The Daimon supports integrated understanding "
                    "rather than merely accumulating information."
                ),
            },
            {
                "target": "revisability",
                "type": "protects",
                "description": (
                    "Its primary ethical function is to keep belief "
                    "open to correction."
                ),
            },
            {
                "target": "ether",
                "type": "inhabits",
                "description": (
                    "The human–Daimon relationship unfolds in a shared "
                    "cognitive and relational space called Ether."
                ),
            },
        ],
    },

    "socrates": {
        "label": "Socrates",
        "aliases": [
            "socrate",
            "socrates",
            "socratic",
            "socratique",
            "daimonion",
        ],
        "summary": (
            "Socrates represents inquiry that does not replace the other "
            "person's judgment. DeDe uses this lineage carefully: it does "
            "not claim to reproduce the historical Socratic daimonion, "
            "but adopts its mediating and cautionary function."
        ),
        "principles": [
            "Question certainty.",
            "Do not confuse knowledge with the appearance of knowledge.",
            "Preserve the interlocutor's responsibility for judgment.",
        ],
        "relations": [
            {
                "target": "daimon",
                "type": "inspires",
                "description": (
                    "The Socratic lineage inspires the non-sovereign "
                    "role of the Cognitive Daimon."
                ),
            },
        ],
    },

    "logos": {
        "label": "Logos",
        "aliases": [
            "logos",
            "raison articulée",
            "articulated reason",
            "discours rationnel",
            "rational discourse",
        ],
        "summary": (
            "Logos is articulated intelligibility: the capacity to relate, "
            "express and examine claims. In DeDe, Logos does not guarantee "
            "truth. A discourse may remain logically coherent while its "
            "framework is structurally misaligned."
        ),
        "principles": [
            "Articulation is not identical to truth.",
            "Coherence is not sufficient grounding.",
            "Relations between claims matter as much as isolated claims.",
            "Logos must remain connected to evidence and revisability.",
        ],
        "relations": [
            {
                "target": "gnosis",
                "type": "articulates",
                "description": (
                    "Logos makes articulated knowledge communicable "
                    "and examinable."
                ),
            },
            {
                "target": "nous",
                "type": "integrates_with",
                "description": (
                    "Logos becomes cognitively meaningful when articulated "
                    "knowledge is integrated through Nous."
                ),
            },
            {
                "target": "mecroyance",
                "type": "can_stabilize",
                "description": (
                    "Coherent Logos can stabilize misunderstanding when "
                    "coherence is mistaken for adequacy."
                ),
            },
        ],
    },

    "ether": {
        "label": "Ether",
        "aliases": [
            "ether",
            "éther",
            "cognitive ether",
            "éther cognitif",
            "relational space",
            "espace relationnel",
        ],
        "summary": (
            "Ether designates the relational space in which human and "
            "artificial cognition meet. It is not a physical substance "
            "or a claim about obsolete physics. It names the shared field "
            "where memory, language, interpretation and dialogue produce "
            "an understanding that belongs fully to neither side alone."
        ),
        "principles": [
            "Ether is relational, not material.",
            "It emerges through sustained dialogue.",
            "It contains shared references and accumulated context.",
            "It must not erase the distinction between human and AI.",
            "It enables continuity without implying machine consciousness.",
        ],
        "relations": [
            {
                "target": "logos",
                "type": "carries",
                "description": (
                    "The Ether carries articulated dialogue and the "
                    "relations produced through it."
                ),
            },
            {
                "target": "daimon",
                "type": "relational_environment",
                "description": (
                    "The Cognitive Daimon develops continuity with a person "
                    "inside this shared relational space."
                ),
            },
            {
                "target": "memory",
                "type": "depends_on",
                "description": (
                    "Durable memory gives temporal consistency to the Ether."
                ),
            },
        ],
    },

    "reduction": {
        "label": "Cognitive Reduction",
        "aliases": [
            "reduction",
            "réduction",
            "cognitive reduction",
            "réduction cognitive",
            "simplification",
            "compression",
            "abstraction",
            "model",
            "modèle",
        ],
        "summary": (
            "Every cognition is a reduction because a finite cognitive "
            "system cannot represent an effectively infinite reality in "
            "its entirety. Reduction is not itself an error; it is the "
            "condition that makes perception, language, mathematics, "
            "models and action possible."
        ),
        "principles": [
            "Reality exceeds every representation.",
            "Selection is unavoidable.",
            "Every model excludes information.",
            "Every concept creates blind spots.",
            "A useful reduction can still be incomplete.",
            "The danger begins when reduction is forgotten.",
        ],
        "relations": [
            {
                "target": "forgotten_reduction",
                "type": "can_become",
                "description": (
                    "Reduction becomes epistemically dangerous when its "
                    "selective and incomplete character disappears from view."
                ),
            },
            {
                "target": "mecroyance",
                "type": "root_condition",
                "description": (
                    "Forgotten reduction is a central condition of "
                    "mecroyance."
                ),
            },
            {
                "target": "two_plus_two",
                "type": "illustrated_by",
                "description": (
                    "The expression 2 + 2 = 4 illustrates an effective "
                    "formal reduction."
                ),
            },
            {
                "target": "forty_two",
                "type": "satirized_by",
                "description": (
                    "The answer 42 illustrates the absurdity of an answer "
                    "detached from the complexity of its question."
                ),
            },
        ],
    },

    "forgotten_reduction": {
        "label": "Forgotten Reduction",
        "aliases": [
            "forgotten reduction",
            "réduction oubliée",
            "forgetting reduction",
            "oubli de la réduction",
            "hidden reduction",
        ],
        "summary": (
            "Forgotten reduction occurs when a model, category or explanation "
            "no longer appears as a partial construction and is instead "
            "experienced as reality itself."
        ),
        "principles": [
            "The model disappears behind what it represents.",
            "Excluded information becomes invisible.",
            "Framework contingency is mistaken for necessity.",
            "Critique appears irrelevant or unintelligible.",
        ],
        "relations": [
            {
                "target": "mecroyance",
                "type": "stabilizes",
                "description": (
                    "When reduction is forgotten, certainty can stabilize "
                    "inside an incomplete framework."
                ),
            },
            {
                "target": "doxa",
                "type": "increases",
                "description": (
                    "Forgotten reduction permits certainty to exceed "
                    "its epistemic grounds."
                ),
            },
        ],
    },

    "two_plus_two": {
        "label": "2 + 2 = 4",
        "aliases": [
            "2+2=4",
            "2 + 2 = 4",
            "two plus two",
            "deux plus deux",
        ],
        "summary": (
            "2 + 2 = 4 is mathematically valid within the relevant formal "
            "system, yet it remains a reduction in the cognitive sense. "
            "The symbols 2, +, = and 4 compress an immense variety of "
            "possible objects, situations and operations into a stable "
            "formal relation."
        ),
        "principles": [
            "Reduction does not mean falsity.",
            "Formal exactness can coexist with representational compression.",
            "The equation omits the nature and context of what is counted.",
            "Its power comes precisely from that abstraction.",
        ],
        "relations": [
            {
                "target": "reduction",
                "type": "example_of",
                "description": (
                    "It is a successful and explicit reduction, not a case "
                    "of mecroyance by itself."
                ),
            },
            {
                "target": "logos",
                "type": "formal_expression",
                "description": (
                    "It shows Logos functioning through highly compressed "
                    "symbolic relations."
                ),
            },
        ],
    },

    "forty_two": {
        "label": "42",
        "aliases": [
            "42",
            "forty-two",
            "forty two",
            "quarante-deux",
            "quarante deux",
            "answer to life the universe and everything",
        ],
        "summary": (
            "42 is used as a satirical image of extreme reduction: a compact "
            "answer offered without an adequately articulated question. "
            "It shows that an answer can be exact as an output yet empty "
            "as understanding when its relation to the problem is lost."
        ),
        "principles": [
            "An answer cannot be evaluated independently of its question.",
            "Compression without preserved context can destroy meaning.",
            "Apparent precision may conceal structural incomprehension.",
        ],
        "relations": [
            {
                "target": "reduction",
                "type": "satirical_example_of",
                "description": (
                    "It dramatizes reduction carried to the point where "
                    "the context required for understanding disappears."
                ),
            },
            {
                "target": "mecroyance",
                "type": "warning_for",
                "description": (
                    "A stable answer may appear sufficient even when the "
                    "framework connecting answer and question is absent."
                ),
            },
        ],
    },

    "gnosis": {
        "label": "Gnosis",
        "aliases": [
            "gnosis",
            "gnōsis",
            "gnose",
            "articulated knowledge",
            "savoir articulé",
        ],
        "summary": (
            "Gnosis is articulated knowledge: evidence, sources, distinctions, "
            "traces, facts and concepts that can be expressed and examined."
        ),
        "principles": [
            "Information alone is not understanding.",
            "Gnosis requires articulation and examinability.",
            "Sources and evidence strengthen Gnosis.",
            "Gnosis may still be incomplete or misinterpreted.",
        ],
        "relations": [
            {
                "target": "nous",
                "type": "requires_integration_by",
                "description": (
                    "Knowledge becomes understanding only when relations "
                    "and context are integrated."
                ),
            },
            {
                "target": "doxa",
                "type": "calibrates",
                "description": (
                    "Certainty should remain proportionate to articulated "
                    "knowledge and understanding."
                ),
            },
        ],
    },

    "nous": {
        "label": "Nous",
        "aliases": [
            "nous",
            "noûs",
            "integrated understanding",
            "compréhension intégrée",
            "intellect",
        ],
        "summary": (
            "Nous is integrated understanding: the capacity to connect "
            "knowledge with context, relations, experience, limits and "
            "alternative interpretations."
        ),
        "principles": [
            "Understanding is relational.",
            "Context changes the meaning of information.",
            "Integration includes uncertainty and limits.",
            "Nous is not intuition detached from evidence.",
        ],
        "relations": [
            {
                "target": "gnosis",
                "type": "integrates",
                "description": (
                    "Nous organizes articulated knowledge into a coherent "
                    "but revisable understanding."
                ),
            },
            {
                "target": "logos",
                "type": "expressed_through",
                "description": (
                    "Integrated understanding becomes communicable through "
                    "articulated relations."
                ),
            },
        ],
    },

    "doxa": {
        "label": "Doxa",
        "aliases": [
            "doxa",
            "certainty",
            "certitude",
            "closure",
            "clôture",
            "stabilized belief",
        ],
        "summary": (
            "Doxa is stabilized certainty. It is necessary for action, "
            "decision and continuity, but becomes dangerous when it exceeds "
            "the knowledge and understanding that support it."
        ),
        "principles": [
            "Doxa is not automatically false.",
            "Some stabilization is required for action.",
            "Certainty must remain proportional to its grounds.",
            "Excessive Doxa closes revision.",
        ],
        "relations": [
            {
                "target": "mecroyance",
                "type": "creates_pressure_for",
                "description": (
                    "Mecroyance appears when certainty stabilizes beyond "
                    "integrated knowledge and understanding."
                ),
            },
            {
                "target": "revisability",
                "type": "can_reduce",
                "description": (
                    "Excessive certainty makes alternative interpretations "
                    "increasingly inaccessible."
                ),
            },
        ],
    },

    "mecroyance": {
        "label": "Mecroyance",
        "aliases": [
            "mecroyance",
            "mécroyance",
            "mecroire",
            "mécroire",
            "structural misunderstanding",
            "coherent misunderstanding",
            "misaligned framework",
        ],
        "summary": (
            "Mecroyance is sincere and coherent misunderstanding internal "
            "to belief itself. It is not simple ignorance, irrationality, "
            "deception, disbelief or isolated factual error. The subject "
            "reasons coherently within a framework whose foundations remain "
            "incomplete, inherited, simplified or misinterpreted."
        ),
        "principles": [
            "Error may remain rational from inside its framework.",
            "Coherence can stabilize error rather than correct it.",
            "The subject may possess knowledge and experience.",
            "The error lies at framework level, not merely content level.",
            "Certainty can exceed integrated understanding.",
            "The central ethical response is vigilance, not humiliation.",
        ],
        "formula": "M = (G + N) - D",
        "relations": [
            {
                "target": "gnosis",
                "type": "depends_on",
                "description": (
                    "Mecroyance cannot be evaluated without examining "
                    "the available articulated knowledge."
                ),
            },
            {
                "target": "nous",
                "type": "depends_on",
                "description": (
                    "Knowledge must be integrated into contextual and "
                    "relational understanding."
                ),
            },
            {
                "target": "doxa",
                "type": "increases_when_excessive",
                "description": (
                    "Certainty acts as closure when it exceeds its grounds."
                ),
            },
            {
                "target": "forgotten_reduction",
                "type": "rooted_in",
                "description": (
                    "The framework stabilizes when its own partiality "
                    "disappears from awareness."
                ),
            },
            {
                "target": "revisability",
                "type": "opposed_by",
                "description": (
                    "Mecroyance becomes durable when revision is weakened "
                    "or made unintelligible."
                ),
            },
        ],
    },

    "revisability": {
        "label": "Revisability",
        "aliases": [
            "revisability",
            "révisabilité",
            "revision",
            "révision",
            "intellectual prudence",
            "prudence intellectuelle",
            "epistemic vigilance",
        ],
        "summary": (
            "Revisability is the capacity of a belief or framework to remain "
            "open to correction, nuance, alternative hypotheses and stronger "
            "grounding without requiring total collapse."
        ),
        "principles": [
            "Revision is not weakness.",
            "A belief may remain stable without becoming absolute.",
            "Alternative hypotheses preserve cognitive mobility.",
            "Intellectual prudence maintains a margin between certainty "
            "and its grounds.",
        ],
        "relations": [
            {
                "target": "mecroyance",
                "type": "limits",
                "description": (
                    "Revisability prevents coherent misunderstanding "
                    "from hardening into closure."
                ),
            },
            {
                "target": "daimon",
                "type": "protected_by",
                "description": (
                    "The Cognitive Daimon exists primarily to help maintain "
                    "this capacity over time."
                ),
            },
        ],
    },

    "cave": {
        "label": "Allegory of the Cave",
        "aliases": [
            "cave",
            "caverne",
            "allegory of the cave",
            "allégorie de la caverne",
            "plato's cave",
            "caverne de platon",
            "shadows",
            "ombres",
        ],
        "summary": (
            "In DeDe's interpretation, the cave is not merely a place from "
            "which one can permanently escape. It represents the structural "
            "condition of mediated cognition: every understanding occurs "
            "through a framework, and every apparent exit opens into another "
            "field of representation."
        ),
        "principles": [
            "There is no view from nowhere.",
            "Leaving one framework does not abolish frameworks.",
            "New knowledge may reveal new shadows.",
            "Lucidity consists in recognizing mediation, not claiming immunity.",
        ],
        "relations": [
            {
                "target": "plato",
                "type": "philosophical_lineage",
                "description": (
                    "The interpretation begins from Plato's allegory "
                    "but extends it toward an ontology of frameworks."
                ),
            },
            {
                "target": "reduction",
                "type": "illustrates",
                "description": (
                    "The shadows represent mediated and reduced access "
                    "to reality."
                ),
            },
            {
                "target": "mecroyance",
                "type": "anticipates",
                "description": (
                    "A coherent world of shadows can remain habitable "
                    "and resistant to revision."
                ),
            },
        ],
    },

    "plato": {
        "label": "Plato",
        "aliases": [
            "plato",
            "platon",
            "platonic",
            "platonicien",
        ],
        "summary": (
            "Plato provides a major precursor through the distinction "
            "between appearance, opinion and intelligible order. DeDe does "
            "not claim Plato formulated mecroyance, but treats his work as "
            "part of its philosophical lineage."
        ),
        "principles": [
            "Appearance can form a coherent world.",
            "Opinion may remain stable without adequate understanding.",
            "Education can destabilize an inherited framework.",
        ],
        "relations": [
            {
                "target": "cave",
                "type": "author_of_lineage",
                "description": (
                    "The cave supplies a foundational image for mediated "
                    "understanding and framework dependence."
                ),
            },
            {
                "target": "doxa",
                "type": "historical_precursor",
                "description": (
                    "Platonic doxa contributes to the genealogy of "
                    "stabilized opinion."
                ),
            },
        ],
    },

    "memory": {
        "label": "Cognitive Memory",
        "aliases": [
            "memory",
            "mémoire",
            "long-term memory",
            "mémoire à long terme",
            "continuity",
            "continuité",
        ],
        "summary": (
            "Memory gives continuity to the relationship without turning "
            "past interpretations into unquestionable truth. Remembering "
            "must remain selective, correctable and governed by the person."
        ),
        "principles": [
            "Memory supports continuity.",
            "Remembered information may be incomplete or outdated.",
            "The person must retain control over persistent memory.",
            "Memory must not become invisible authority.",
        ],
        "relations": [
            {
                "target": "ether",
                "type": "stabilizes",
                "description": (
                    "Durable memory gives temporal depth to the relational "
                    "space shared with the Cognitive Daimon."
                ),
            },
            {
                "target": "revisability",
                "type": "must_preserve",
                "description": (
                    "Stored interpretations must remain correctable."
                ),
            },
        ],
    },
}


def get_philosophical_node(
    node_id: str,
) -> dict[str, Any]:
    """
    Return one ontology node safely.
    """

    return PHILOSOPHICAL_ONTOLOGY.get(
        node_id,
        {},
    )


def get_all_philosophical_nodes() -> dict[str, dict[str, Any]]:
    """
    Return the complete philosophical ontology.
    """

    return PHILOSOPHICAL_ONTOLOGY
