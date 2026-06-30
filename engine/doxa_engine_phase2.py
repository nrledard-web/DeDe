"""
DeDe - DOXA Engine Phase 2

Phase 2 cognitive engine.

Pipeline

Text
    ↓
Knowledge
    ↓
Concept Extraction
    ↓
Semantic Engine
    ↓
Semantic Reasoner
    ↓
Semantic Graph
    ↓
Estimators
    ↓
Cognitive Workspace
    ↓
Agents
    ↓
Cognitive Graph Enrichment
    ↓
Graph Query Engine
    ↓
Inference Engine
    ↓
Cognitive Compiler
    ↓
Cognitive Reasoner
    ↓
LLM Connector
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
from knowledge.concept_extractor import ConceptExtractor

from semantic.semantic_engine import SemanticEngine
from semantic.semantic_reasoner import SemanticReasoner
from semantic.semantic_graph import SemanticGraph
from semantic.graph_query_engine import GraphQueryEngine

from reasoning.inference_engine import InferenceEngine
from reasoning.cognitive_compiler import CognitiveCompiler
from reasoning.cognitive_reasoner import CognitiveReasoner

from llm.llm_connector import LLMConnector

from estimators.estimator_engine import EstimatorEngine

from committee.cognitive_committee import CognitiveCommittee

from formulas.doxa_formula_engine import DoxaFormulaEngine

from agents.nous_agent import NousAgent
from agents.doxa_agent import DoxaAgent
from agents.reduction_agent import ReductionAgent
from agents.nouscope_agent import NOUSCOPEAgent
from agents.cognitive_therapy_agent import CognitiveTherapyAgent


class DoxaEnginePhase2:

    def __init__(self):
        self.knowledge = KnowledgeAgent()
        self.concept_extractor = ConceptExtractor()
        self.semantic_engine = SemanticEngine()
        self.semantic_reasoner = SemanticReasoner()
        self.semantic_graph = SemanticGraph()
        self.graph_query_engine = GraphQueryEngine()
        self.inference_engine = InferenceEngine()
        self.cognitive_compiler = CognitiveCompiler()
        self.cognitive_reasoner = CognitiveReasoner()
        self.llm_connector = LLMConnector()

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

        knowledge_result = self.knowledge.analyze(workspace)

        workspace = self.concept_extractor.run(workspace)
        workspace = self.semantic_engine.run(workspace)
        workspace = self.semantic_reasoner.run(workspace)

        # --------------------------------------------------
        # Phase 4.1
        # Initial Semantic Graph
        # --------------------------------------------------
        workspace = self.semantic_graph.run(workspace)

        workspace = self.estimator_engine.run(workspace)

        agent_results = {}

        for agent in self.agents:
            result = agent.analyze(workspace)
            agent_results[agent.name] = result

        # --------------------------------------------------
        # Phase 4.2
        # Cognitive Graph Enrichment
        # --------------------------------------------------
        workspace = self.semantic_graph.enrich_from_agents(
            workspace,
            agent_results,
        )

        # --------------------------------------------------
        # Phase 4.3
        # Graph Query Engine
        # --------------------------------------------------
        graph_queries = self.graph_query_engine.analyze(
            workspace.interpretations.get(
                "semantic_graph",
                {},
            )
        )

        workspace.add_interpretation(
            "graph_queries",
            graph_queries,
        )

        # --------------------------------------------------
        # Phase 4.4
        # Inference Engine
        # --------------------------------------------------
        inference_patterns = self.inference_engine.analyze(
            graph_queries=graph_queries,
        )

        workspace.add_interpretation(
            "inference_patterns",
            inference_patterns,
        )

        # --------------------------------------------------
        # Phase 4.5
        # Cognitive Compiler
        # --------------------------------------------------
        cognitive_state = self.cognitive_compiler.compile(
            graph_queries=graph_queries,
            inference_patterns=inference_patterns,
        )

        workspace.add_interpretation(
            "cognitive_state",
            cognitive_state,
        )

        # --------------------------------------------------
        # Phase 4.6
        # Cognitive Reasoner
        # --------------------------------------------------
        cognitive_reasoning = self.cognitive_reasoner.run(
            workspace=workspace,
            graph_queries=graph_queries,
            cognitive_state=cognitive_state,
        )

        workspace.add_interpretation(
            "cognitive_reasoning",
            cognitive_reasoning,
        )

        # --------------------------------------------------
        # Phase 4.7
        # LLM Connector
        # --------------------------------------------------
        llm_package = self.llm_connector.build_prompt_package(
            text=text,
            graph_queries=graph_queries,
            cognitive_state=cognitive_state,
            cognitive_reasoning=cognitive_reasoning,
        )

        workspace.add_interpretation(
            "llm_package",
            llm_package,
        )

        committee_result = self.committee.synthesize(workspace)

        formulas = self.formula_engine.compute(workspace)

        report = {
            "phase": "phase_4_7_cognitive_compiler_ready",
            "text": text,
            "knowledge": knowledge_result,
            "concepts": workspace.interpretations.get("concepts", {}),
            "semantic": workspace.interpretations.get("semantic", {}),
            "semantic_reasoning": workspace.interpretations.get(
                "semantic_reasoner",
                {},
            ),
            "semantic_graph": workspace.interpretations.get(
                "semantic_graph",
                {},
            ),
            "graph_queries": workspace.interpretations.get(
                "graph_queries",
                {},
            ),
            "inference_patterns": workspace.interpretations.get(
                "inference_patterns",
                {},
            ),
            "cognitive_state": workspace.interpretations.get(
                "cognitive_state",
                {},
            ),
            "cognitive_reasoning": workspace.interpretations.get(
                "cognitive_reasoning",
                {},
            ),
            "llm_package": workspace.interpretations.get(
                "llm_package",
                {},
            ),
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
            "cognitive_balance": core["cognitive_balance"],
            "mecroyance_pressure": core["mecroyance_pressure"],
            "mecroyance_risk": core["mecroyance_risk"],
            "revisability": core["revisability"],
            "surconfidence": derived["surconfidence"],
            "cognitive_closure": derived["cognitive_closure"],
            "forgotten_reduction_pressure": derived[
                "forgotten_reduction_pressure"
            ],
            "committee_diagnosis": committee_result["diagnosis"],
            "committee_confidence": committee_result["confidence"],
            "committee_orientation": committee_result["dominant_orientation"],
            "diagnosis": formulas["diagnosis"],
        }
