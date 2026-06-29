"""
DeDe - DOXA Engine Phase 2

Phase 2 cognitive engine.

Pipeline

Text
    ↓
Knowledge
    ↓
Estimators
    ↓
Cognitive Workspace
    ↓
Agents
    ↓
Committee
    ↓
Formula Engine
    ↓
Report
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace

from knowledge.knowledge_agent import KnowledgeAgent

from estimators.estimator_engine import EstimatorEngine

from committee.cognitive_committee import CognitiveCommittee

from formulas.doxa_formula_engine import DoxaFormulaEngine

from agents.nous_agent import NousAgent
from agents.doxa_agent import DoxaAgent
from agents.reduction_agent import ReductionAgent
from agents.nouscope_agent import NOUSCOPEAgent
from agents.cognitive_therapy_agent import CognitiveTherapyAgent


class DoxaEnginePhase2:
    """
    Main Phase 2 engine.

    Coordinates the complete cognitive mechanics pipeline.
    """

    def __init__(self):

        self.knowledge = KnowledgeAgent()

        self.estimator_engine = EstimatorEngine()

        self.committee = CognitiveCommittee()

        self.formula_engine = DoxaFormulaEngine()

        self.agents = [
            NousAgent(),
            DoxaAgent(),
            ReductionAgent(),
            NOUSCOPEAgent(),
            CognitiveTherapyAgent(),
        ]

    def analyze(self, text: str) -> dict[str, Any]:

        workspace = CognitiveWorkspace(text=text)

        # -------------------------------------------------
        # Knowledge
        # -------------------------------------------------

        knowledge_result = self.knowledge.analyze(
            workspace
        )

        # -------------------------------------------------
        # Estimation layer
        # -------------------------------------------------

        workspace = self.estimator_engine.run(
            workspace
        )

        # -------------------------------------------------
        # Cognitive agents
        # -------------------------------------------------

        agent_results = {}

        for agent in self.agents:

            result = agent.analyze(
                workspace
            )

            agent_results[
                agent.name
            ] = result

        # -------------------------------------------------
        # Committee
        # -------------------------------------------------

        committee_result = self.committee.synthesize(
            workspace
        )

        # -------------------------------------------------
        # Formula engine
        # -------------------------------------------------

        formulas = self.formula_engine.compute(
            workspace
        )

        # -------------------------------------------------
        # Report
        # -------------------------------------------------

        report = {

            "phase": "phase_2_cognitive_mechanics",

            "text": text,

            "knowledge": knowledge_result,

            "workspace": workspace.snapshot(),

            "agent_results": agent_results,

            "committee": committee_result,

            "formulas": formulas,

            "summary": self._build_summary(
                workspace,
                committee_result,
                formulas,
            ),
        }

        return report

    def _build_summary(
        self,
        workspace: CognitiveWorkspace,
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

            "cognitive_balance":
                core["cognitive_balance"],

            "mecroyance_pressure":
                core["mecroyance_pressure"],

            "mecroyance_risk":
                core["mecroyance_risk"],

            "revisability":
                core["revisability"],

            "surconfidence":
                derived["surconfidence"],

            "cognitive_closure":
                derived["cognitive_closure"],

            "forgotten_reduction_pressure":
                derived["forgotten_reduction_pressure"],

            "committee_diagnosis":
                committee_result["diagnosis"],

            "committee_confidence":
                committee_result["confidence"],

            "committee_orientation":
                committee_result["dominant_orientation"],

            "diagnosis":
                formulas["diagnosis"],
        }
