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

from memory.persistent_memory import PersistentMemory

from core.dede_identity import DeDeIdentity
from core.dede_state import DeDeState
from memory.user_memory import UserMemory
from dialogue.dialogue_manager import DialogueManager

from identity.onboarding import Onboarding

from reasoning.inference_engine import InferenceEngine
from reasoning.cognitive_compiler import CognitiveCompiler
from reasoning.cognitive_reasoner import CognitiveReasoner
from reasoning.cognitive_feedback import CognitiveFeedback

from dialogue.cognitive_dialogue_manager import CognitiveDialogueManager
from dialogue.response_builder import ResponseBuilder
from dialogue.conversation_manager import ConversationManager
from dialogue.conversation_reasoner import ConversationReasoner
from dialogue.dialogue_profile import DialogueProfile

from llm.llm_connector import LLMConnector
from llm.llm_response_interpreter import LLMResponseInterpreter
from llm.llm_bridge import LLMBridge

from committee.cognitive_committee import CognitiveCommittee

from core.daimon_filter import DaimonFilter

from formulas.doxa_formula_engine import DoxaFormulaEngine
from agents.nous_agent import NousAgent
from agents.doxa_agent import DoxaAgent
from agents.reduction_agent import ReductionAgent
from agents.nouscope_agent import NOUSCOPEAgent
from agents.cognitive_therapy_agent import CognitiveTherapyAgent
from memory.memory_retriever import MemoryRetriever

class DoxaEnginePhase2:
    """
    Main orchestrator for DeDe Phase 2.

    This class coordinates all symbolic, semantic, cognitive,
    inferential and LLM-preparation layers.
    """

    def __init__(
        self,
        user_id: str = "default_user",
    ):
        # --------------------------------------------------
        # Knowledge and semantic layers
        # --------------------------------------------------
        self.knowledge = KnowledgeAgent()
        self.concept_extractor = ConceptExtractor()
        self.semantic_engine = SemanticEngine()
        self.semantic_reasoner = SemanticReasoner()
        self.semantic_graph = SemanticGraph()
        self.onboarding = Onboarding()
        self.user_memory = UserMemory()
        self.persistent_memory = PersistentMemory(
            user_id=user_id,
        )
        self.memory_retriever = MemoryRetriever()
        self.dede_identity = DeDeIdentity()
        self.dede_state = DeDeState()
        self.daimon_filter = DaimonFilter()
        
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
        self.dialogue_manager = DialogueManager()
        self.cognitive_dialogue_manager = CognitiveDialogueManager()
        self.response_builder = ResponseBuilder()
        self.conversation_manager = ConversationManager()
        self.conversation_reasoner = ConversationReasoner()
        self.dialogue_profile = DialogueProfile()

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
        conversation_history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Run the complete DeDe Phase 2 cognitive pipeline.
        """

        workspace = CognitiveWorkspace(text=text)

        conversation_context = self.conversation_manager.build_context(
            conversation_history,
        )
        
        workspace.add_interpretation(
            "conversation_context",
            conversation_context,
        )
        # --------------------------------------------------
        # Phase 5.2
        # User Memory Update
        # --------------------------------------------------
        user_memory = self.user_memory.update_from_text(text)

        persistent_memory = self.persistent_memory.merge_user_memory(
            user_memory,
        )

        retrieved_memory = self.memory_retriever.retrieve(
            text=text,
            persistent_memory=persistent_memory,
        )

        workspace.add_interpretation(
            "retrieved_memory",
            retrieved_memory,
        )

        workspace.add_interpretation(
            "user_memory",
            user_memory,
        )

        # --------------------------------------------------
        # Phase 5.3
        # DeDe Identity State
        # --------------------------------------------------
        identity_state = self.dede_identity.build_identity_state(
            user_memory=user_memory,
            persistent_memory=persistent_memory,
            retrieved_memory=retrieved_memory,
        )

        workspace.add_interpretation(
            "dede_identity",
            identity_state,
        )
        # --------------------------------------------------
        # Phase 5.4
        # Dialogue Profile
        # --------------------------------------------------
        dialogue_profile = self.dialogue_profile.analyze(
            text=text,
            conversation_context=conversation_context,
        )

        workspace.add_interpretation(
            "dialogue_profile",
            dialogue_profile,
        )
        # --------------------------------------------------
        # Phase 5.5
        # DeDe Internal State
        # --------------------------------------------------
        dede_state = self.dede_state.build(
            text=text,
            user_memory=user_memory,
            dede_identity=identity_state,
            dialogue_profile=dialogue_profile,
            conversation_context=conversation_context,
        )

        workspace.add_interpretation(
            "dede_state",
            dede_state,
        )

        # --------------------------------------------------
        # Phase 5.6
        # Onboarding
        # --------------------------------------------------
        is_first_contact = conversation_context.get("turn_count", 0) == 0

        onboarding = {}

        if is_first_contact:
            onboarding = self.onboarding.build(
                dialogue_profile=dialogue_profile,
            )

        workspace.add_interpretation(
            "onboarding",
            onboarding,
        )

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
        dialogue_decision = self.cognitive_dialogue_manager.decide(
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
            user_memory=user_memory,
            persistent_memory=self.persistent_memory.get_memory(),
            retrieved_memory=retrieved_memory,
            dede_identity=identity_state,
            dede_state=dede_state,
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
        # Conversation Reasoner
        # --------------------------------------------------
        conversation_reasoning = self.conversation_reasoner.reason(
            text=text,
            conversation_context=conversation_context,
            dialogue_decision=dialogue_decision,
            cognitive_feedback=cognitive_feedback,
            summary=self._build_summary(
                workspace,
                committee_result,
                formulas,
            ),
        )
    
        workspace.add_interpretation(
            "conversation_reasoning",
            conversation_reasoning,
        )

        # --------------------------------------------------
        # Phase 4.18
        # Natural Dialogue Manager
        # --------------------------------------------------
        dialogue = self.dialogue_manager.generate_response(
            user_text=text,
            identity_state=workspace.interpretations.get(
                "dede_identity",
                {},
            ),
            dede_state=workspace.interpretations.get(
                "dede_state",
                {},
            ),
            retrieved_memory=workspace.interpretations.get(
                "retrieved_memory",
                {},
            ),
            llm_result=workspace.interpretations.get(
                "llm_bridge_response",
                {},
            ),
            cognitive_state=workspace.interpretations.get(
                "cognitive_state",
                {},
            ),
        )

        workspace.add_interpretation(
            "dialogue",
            dialogue,
        )
        
        # --------------------------------------------------
        # Phase 4.19
        # Response Builder
        # --------------------------------------------------
        
        dialogue_context = {
            "knowledge": knowledge_result,
            "dialogue_decision": dialogue_decision,
            "conversation_reasoning": conversation_reasoning,
            "dialogue_profile": dialogue_profile,
            "dede_state": dede_state,
            "onboarding": onboarding,
            "cognitive_feedback": cognitive_feedback,
            "llm_bridge_response": llm_bridge_response,
            "committee": committee_result,
            "formulas": formulas,
            "dialogue": dialogue,
            "user_memory": user_memory,
            "dede_identity": identity_state,
            "summary": self._build_summary(
                workspace,
                committee_result,
                formulas,
            ),
        }
    
        user_response = self.response_builder.build(
            dialogue_context,
        )

        user_response = self.daimon_filter.filter_response(
            response=user_response,
            dede_state=dede_state,
        )
    
        workspace.add_interpretation(
            "user_response",
            user_response,
        )
        
    
        # --------------------------------------------------
        # Phase 4.20
        # Final Report
        # --------------------------------------------------
        report = {
            "phase": "phase_5_4_identity_memory_dialogue",
            "text": text,
            "conversation_context": workspace.interpretations.get(
                "conversation_context",
                {},
            ),
            "dialogue_profile": workspace.interpretations.get(
                "dialogue_profile",
                {},
            ),
            "dede_state": workspace.interpretations.get(
                "dede_state",
                {},
            ),
            "onboarding": workspace.interpretations.get(
                "onboarding",
                {},
            ),
            "user_memory": workspace.interpretations.get(
                "user_memory",
                {},
            ),
            "dede_identity": workspace.interpretations.get(
                "dede_identity",
                {},
            ),
            "dialogue": workspace.interpretations.get(
                "dialogue",
                {},
            ),
            "knowledge": knowledge_result,
            "persistent_memory": self.persistent_memory.get_memory(),
            "retrieved_memory": workspace.interpretations.get(
                "retrieved_memory",
                {},
            ),
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
            "conversation_reasoning": workspace.interpretations.get(
                "conversation_reasoning",
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
            "daimon_filter": user_response.get(
                "daimon_filter",
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
        updated_conversation_history = self.conversation_manager.add_turn(
            history=conversation_history,
            user_input=text,
            user_response=user_response,
            report=report,
        )
        
        report["conversation_history"] = updated_conversation_history
    
    
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
