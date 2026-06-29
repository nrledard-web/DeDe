"""
DeDe - DOXA Engine Phase 2

Phase 2 engine based on the CognitiveWorkspace architecture.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace
from estimators.estimator_engine import EstimatorEngine
from formulas.doxa_formula_engine import DoxaFormulaEngine
from committee.cognitive_committee import CognitiveCommittee

from agents.nous_agent import NousAgent
from agents.doxa_agent import DoxaAgent
from agents.reduction_agent import ReductionAgent
from agents.nouscope_agent import NOUSCOPEAgent
from agents.cognitive_therapy_agent import CognitiveTherapyAgent


class DoxaEnginePhase2:

    def __init__(self):
        self.estimator_engine = EstimatorEngine()
        self.formula_engine = DoxaFormulaEngine()
        self.committee = CognitiveCommittee()

        self.agents = [
            NousAgent(),
            DoxaAgent(),
            ReductionAgent(),
            NOUSCOPEAgent(),
            CognitiveTherapyAgent(),
        ]

    def analyze(self, text: str) -> dict[str, Any]:
        workspace = CognitiveWorkspace(text=text)

        workspace = self.estimator_engine.run(workspace)

        agent_results = {}

        for agent in self.agents:
            result = agent.analyze(workspace)
            agent_results[agent.name] = result

        committee_result = self.committee.synthesize(workspace)

        formulas = self.formula_engine.compute(workspace)

        report = {
            "phase": "phase_2_cognitive_mechanics",
            "text": text,
            "workspace": workspace.snapshot(),
            "agent_results": agent_results,
            "committee": committee_result,
            "formulas": formulas,
            "summary": self._build_summary(
                workspace,
                agent_results,
                committee_result,
                formulas,
            ),
        }

        return report

    def _build_summary(
        self,
        workspace: CognitiveWorkspace,
        agent_results: dict[str, Any],
        committee_result: dict[str, Any],
        formulas: dict[str, Any],
    ) -> dict[str, Any]:

        core = formulas["core"]
        derived = formulas["derived"]

        return {
            "grounding": workspace.get("grounding"),
            "integration": workspace.get("integration"),
            "closure": workspace.get("closure"),
            "reduction": workspace.get("reduction"),
            "cognitive_balance": core["cognitive_balance"],
            "mecroyance_pressure": core["mecroyance_pressure"],
            "mecroyance_risk": core["mecroyance_risk"],
            "revisability": core["revisability"],
            "surconfidence": derived["surconfidence"],
            "cognitive_closure": derived["cognitive_closure"],
            "forgotten_reduction_pressure": derived["forgotten_reduction_pressure"],
            "committee_diagnosis": committee_result["diagnosis"],
            "committee_confidence": committee_result["confidence"],
            "committee_orientation": committee_result["dominant_orientation"],
            "diagnosis": formulas["diagnosis"],
            "agent_count": len(agent_results),
        }
