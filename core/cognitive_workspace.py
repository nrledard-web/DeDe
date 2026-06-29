"""
DeDe - Cognitive Workspace

Central shared cognitive bus of the DeDe architecture.

The CognitiveWorkspace is the single source of truth for all
cognitive variables produced during an analysis.

Language-dependent estimators write cognitive variables into
the workspace.

Cognitive agents no longer compute these variables themselves.
Instead, they read, interpret and enrich the shared workspace.

This architectural separation makes the cognitive mechanics
independent from the language, detection method or future AI
models used to estimate the variables.

Current foundational variables
------------------------------
- Grounding
- Integration
- Closure
- Reduction

Future variables may include:

- Consensus
- Ambiguity
- Coherence
- Novelty
- Context
- Evidence
- Calibration

without requiring changes to the overall architecture.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CognitiveWorkspace:
    """
    Shared cognitive state exchanged between estimators,
    cognitive agents and the committee.

    Responsibilities
    ----------------
    • Estimators measure cognitive variables.
    • Agents interpret shared variables.
    • Committee synthesizes agent interpretations.
    • DOXA formulas operate from the shared workspace.

    The workspace is therefore the single source of truth
    for every cognitive analysis.
    """

    # =====================================================
    # Input
    # =====================================================

    text: str

    # =====================================================
    # Foundational Cognitive Variables
    # =====================================================

    grounding: float = 0.0
    integration: float = 0.0
    closure: float = 0.0
    reduction: float = 0.0

    # =====================================================
    # Future Cognitive Variables
    # =====================================================

    values: dict[str, Any] = field(default_factory=dict)

    # =====================================================
    # Raw estimator outputs
    # =====================================================

    signals: dict[str, Any] = field(default_factory=dict)

    # =====================================================
    # Agent interpretations
    # =====================================================

    interpretations: dict[str, Any] = field(default_factory=dict)

    # =====================================================
    # Committee observations
    # =====================================================

    observations: list[dict[str, Any]] = field(default_factory=list)

    # =====================================================
    # Debug history
    # =====================================================

    history: list[str] = field(default_factory=list)

    # =====================================================
    # Public API
    # =====================================================

    def set(self, name: str, value: float, signals: Any = None) -> None:
        """
        Store a cognitive variable inside the workspace.
        """

        value = max(0.0, min(1.0, float(value)))

        if hasattr(self, name):
            setattr(self, name, value)

        self.values[name] = value

        if signals is not None:
            self.signals[name] = signals

        self.history.append(f"SET {name}={value:.3f}")

    def set_raw(self, name: str, value: Any, signals: Any = None) -> None:
        """
        Store a raw value inside the workspace without normalization.

        Use this for counters, lists, strings or structured values.
        """

        self.values[name] = value

        if signals is not None:
            self.signals[name] = signals

        self.history.append(f"SET RAW {name}={value}")

    def get(self, name: str, default: float = 0.0) -> float:
        """
        Retrieve a cognitive variable.
        """

        if hasattr(self, name):
            return getattr(self, name)

        return self.values.get(name, default)

    def add_interpretation(self, agent: str, data: Any) -> None:
        """
        Register an agent interpretation.
        """

        self.interpretations[agent] = data
        self.history.append(f"INTERPRETATION {agent}")

    def add_observation(self, observation: dict[str, Any]) -> None:
        """
        Register a committee observation.
        """

        self.observations.append(observation)
        self.history.append("COMMITTEE OBSERVATION")

    def snapshot(self) -> dict[str, Any]:
        """
        Return the complete cognitive state.
        """

        return {
            "variables": {
                "grounding": self.grounding,
                "integration": self.integration,
                "closure": self.closure,
                "reduction": self.reduction,
                **self.values,
            },
            "signals": self.signals,
            "interpretations": self.interpretations,
            "observations": self.observations,
            "history": self.history,
        }
