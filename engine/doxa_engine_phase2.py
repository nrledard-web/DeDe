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
Cognitive Dialogue Manager
    ↓
LLM Connector
    ↓
LLM Bridge
    ↓
LLM Response Interpreter
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

from estimators.estimator_engine import EstimatorEngine

from reasoning.inference_engine import InferenceEngine
from reasoning.cognitive_compiler import CognitiveCompiler
from reasoning.cognitive_reasoner import CognitiveReasoner
from reasoning.cognitive_feedback import CognitiveFeedback

from dialogue.cognitive_dialogue_manager import CognitiveDialogueManager
from dialogue.response_builder import ResponseBuilder

from llm.llm_connector import LLMConnector
from llm.llm_response_interpreter import LLMResponseInterpreter
from llm.llm_bridge import LLMBridge

from committee.cognitive_committee import CognitiveCommittee

from formulas.doxa_formula_engine import DoxaFormulaEngine

from agents.nous_agent import NousAgent
from agents.doxa_agent import DoxaAgent
from agents.reduction_agent import ReductionAgent
from agents.nouscope_agent import NOUSCOPEAgent
from agents.cognitive_therapy_agent import CognitiveTherapyAgent


class DoxaEnginePhase2:
    """
    Main orchestrator for DeDe Phase 2.

    This class coordinates all symbolic, semantic, cognitive,
    inferential and LLM-preparation layers.
    """

    def __init__(self):
        # --------------------------------------------------
        # Knowledge and semantic layers
        # --------------------------------------------------
        self.knowledge = KnowledgeAgent()
        self.concept_extractor = ConceptExtractor()
        self.semantic_engine = SemanticEngine()
        self.semantic_reasoner = SemanticReasoner()
        self.semantic_graph = SemanticGraph()

        # --------------------------------------------------
        # Estimation layer
        # --------------------------------------------------
        self.estimator_engine = EstimatorEngine()

        # --------------------------------------------------
        # Graph and reasoning layers
        # --------------------------------------------------
        self.graph_query_engine = GraphQueryEngine()
        self.inference_engine = InferenceEngine()
        self.cognitive_compiler = CognitiveCompiler()
        self.cognitive_reasoner = CognitiveReasoner()
        self.cognitive_feedback = CognitiveFeedback()
        self.dialogue_manager = CognitiveDialogueManager()
        self.response_builder = ResponseBuilder()

        # --------------------------------------------------
        # LLM preparation layers
        # --------------------------------------------------
        self.llm_connector = LLMConnector()
        self.llm_bridge = LLMBridge()
        self.llm_response_interpreter = LLMResponseInterpreter()

        # --------------------------------------------------
        # Committee and formula layers
        # --------------------------------------------------
        self.committee = CognitiveCommittee()
        self.formula_engine = DoxaFormulaEngine()

        # --------------------------------------------------
        # Cognitive agents
        # --------------------------------------------------
        self.agents = [
            NousAgent(),
            DoxaAgent(),
            ReductionAgent(),
            NOUSCOPEAgent(),
            CognitiveTherapyAgent(),
        ]

    def analyze(
        self,
        text: str,
        enable_llm: bool = False,
    ) -> dict[str, Any]:
        """
        Run the complete DeDe Phase 2 cognitive pipeline.
        """

        workspace = CognitiveWorkspace(text=text)

        # --------------------------------------------------
        # Phase 4.0
        # Knowledge
        # --------------------------------------------------
        knowledge_result = self.knowledge.analyze(workspace)

        # --------------------------------------------------
        # Phase 4.1
        # Concept Extraction + Semantic Engine + Semantic Reasoner
        # --------------------------------------------------
        workspace = self.concept_extractor.run(workspace)
        workspace = self.semantic_engine.run(workspace)
        workspace = self.semantic_reasoner.run(workspace)

        # --------------------------------------------------
        # Phase 4.2
        # Initial Semantic Graph
        # --------------------------------------------------
        workspace = self.semantic_graph.run(workspace)

        # --------------------------------------------------
        # Phase 4.3
        # Estimators
        # --------------------------------------------------
        workspace = self.estimator_engine.run(workspace)

        # --------------------------------------------------
        # Phase 4.4
        # Cognitive Agents
        # --------------------------------------------------
        agent_results = {}

        for agent in self.agents:
            result = agent.analyze(workspace)
            agent_results[agent.name] = result

        # --------------------------------------------------
        # Phase 4.5
        # Cognitive Graph Enrichment
        # --------------------------------------------------
        workspace = self.semantic_graph.enrich_from_agents(
            workspace,
            agent_results,
        )

        # --------------------------------------------------
        # Phase 4.6
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
        # Phase 4.7
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
        # Phase 4.8
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
        # Phase 4.9
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
        # Phase 4.10
        # Cognitive Dialogue Manager
        # --------------------------------------------------
        dialogue_decision = self.dialogue_manager.decide(
            text=text,
            knowledge=knowledge_result,
            cognitive_state=cognitive_state,
            cognitive_reasoning=cognitive_reasoning,
        )

        workspace.add_interpretation(
            "dialogue_decision",
            dialogue_decision,
        )

        # --------------------------------------------------
        # Phase 4.11
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

        # --------------------------------------------------
        # Phase 4.12
        # LLM Bridge
        # --------------------------------------------------
        llm_bridge_response = self.llm_bridge.ask(
            llm_package=llm_package,
            enabled=enable_llm,
        )

        workspace.add_interpretation(
            "llm_bridge_response",
            llm_bridge_response,
        )

        # --------------------------------------------------
        # Phase 4.13
        # LLM Response Interpreter
        # --------------------------------------------------
        llm_interpretation = self.llm_response_interpreter.interpret(
            llm_package=llm_package,
            llm_response=llm_bridge_response.get("response"),
        )

        workspace.add_interpretation(
            "llm_interpretation",
            llm_interpretation,
        )

        # --------------------------------------------------
        # Phase 4.14
        # Cognitive Feedback
        # --------------------------------------------------
        cognitive_feedback = self.cognitive_feedback.analyze(
            llm_response=llm_bridge_response.get("response"),
            parsed_json=llm_bridge_response.get("parsed_json"),
        )

        workspace.add_interpretation(
            "cognitive_feedback",
            cognitive_feedback,
        )

        # --------------------------------------------------
        # Phase 4.15
        # Cognitive Committee
        # --------------------------------------------------
        committee_result = self.committee.synthesize(workspace)
    
        # --------------------------------------------------
        # Phase 4.16
        # Formula Engine
        # --------------------------------------------------
        formulas = self.formula_engine.compute(workspace)

        # --------------------------------------------------
        # Phase 4.17
        # Response Builder
        # --------------------------------------------------
        
        dialogue_context = {
            "knowledge": knowledge_result,
            "dialogue_decision": dialogue_decision,
            "cognitive_feedback": cognitive_feedback,
            "llm_bridge_response": llm_bridge_response,
            "committee": committee_result,
            "formulas": formulas,
            "summary": self._build_summary(
                workspace,
                committee_result,
                formulas,
            ),
        }

        user_response = self.response_builder.build(
            dialogue_context,
        )

        workspace.add_interpretation(
            "user_response",
            user_response,
        )
        
    
        # --------------------------------------------------
        # Phase 4.18
        # Final Report
        # --------------------------------------------------
        report = {
            "phase": "phase_5_0_cognitive_feedback_ready",
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
            "dialogue_decision": workspace.interpretations.get(
                "dialogue_decision",
                {},
            ),
            "llm_package": workspace.interpretations.get(
                "llm_package",
                {},
            ),
            "llm_bridge_response": workspace.interpretations.get(
                "llm_bridge_response",
                {},
            ),
            "llm_interpretation": workspace.interpretations.get(
                "llm_interpretation",
                {},
            ),
            "cognitive_feedback": workspace.interpretations.get(
                "cognitive_feedback",
                {},
            ),
            "user_response": workspace.interpretations.get(
                "user_response",
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
        """
        Build a compact final summary from workspace variables,
        committee synthesis and formula results.
        """

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
