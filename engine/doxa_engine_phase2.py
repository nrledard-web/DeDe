"""
DeDe - DOXA Engine Phase 2

Phase 2 engine based on the CognitiveWorkspace architecture.

This engine does not use CognitiveState.

Pipeline:
Text
↓
CognitiveWorkspace
↓
EstimatorEngine
↓
Cognitive Agents
↓
Workspace Snapshot
↓
Report
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace

from estimators.estimator_engine import EstimatorEngine

from agents.nous_agent import NousAgent
from agents.doxa_agent import DoxaAgent
from agents.reduction_agent import ReductionAgent
from agents.nouscope_agent import NOUSCOPEAgent
from agents.cognitive_therapy_agent import CognitiveTherapyAgent


class DoxaEnginePhase2:
    """
    Phase 2 cognitive engine.

    The engine creates a CognitiveWorkspace, runs estimators,
    then asks agents to interpret the shared cognitive state.
    """

    def __init__(self):
        self.estimator_engine = EstimatorEngine()

        self.agents = [
            NousAgent(),
            DoxaAgent(),
            ReductionAgent(),
            NOUSCOPEAgent(),
            CognitiveTherapyAgent(),
        ]

    def analyze(self, text: str) -> dict[str, Any]:
        """
        Run a full Phase 2 cognitive analysis.
        """

        workspace = CognitiveWorkspace(text=text)

        workspace = self.estimator_engine.run(workspace)

        agent_results = {}

        for agent in self.agents:
            result = agent.analyze(workspace)
            agent_results[agent.name] = result

        report = {
            "phase": "phase_2_cognitive_mechanics",
            "text": text,
            "workspace": workspace.snapshot(),
            "agent_results": agent_results,
            "summary": self._build_summary(workspace, agent_results),
        }

        return report

    def _build_summary(
        self,
        workspace: CognitiveWorkspace,
        agent_results: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build a first simple Phase 2 summary.
        """

        grounding = workspace.get("grounding")
        integration = workspace.get("integration")
        closure = workspace.get("closure")
        reduction = workspace.get("reduction")

        cognitive_balance = (grounding + integration) - (closure + reduction)

        if cognitive_balance >= 0.30:
            diagnosis = "Grounding and integration exceed closure and reduction."
        elif cognitive_balance >= 0.0:
            diagnosis = "Cognitive structure appears moderately balanced."
        else:
            diagnosis = "Closure and reduction may exceed grounding and integration."

        return {
            "grounding": grounding,
            "integration": integration,
            "closure": closure,
            "reduction": reduction,
            "cognitive_balance": cognitive_balance,
            "diagnosis": diagnosis,
            "agent_count": len(agent_results),
        }
