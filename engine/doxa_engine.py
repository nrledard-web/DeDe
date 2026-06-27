"""
DeDe - Doxa Engine
"""

from typing import Any

from agents.gnosis_agent import GnosisAgent
from agents.nous_agent import NousAgent
from agents.doxa_agent import DoxaAgent
from agents.reduction_agent import ReductionAgent
from agents.nouscope_agent import NOUSCOPEAgent
from agents.cognitive_therapy_agent import CognitiveTherapyAgent
from agents.revision_agent import RevisionAgent

from knowledge.knowledge_agent import KnowledgeAgent

from core.cognitive_state import CognitiveState
from core.shared_workspace import SharedCognitiveWorkspace


from detectors.detector_engine import DetectorEngine
from dialogue.question_generator import QuestionGenerator
from reasoning.cognitive_interpreter import CognitiveInterpreter


class DoxaEngine:
    """
    Central engine for running DeDe's symbolic cognitive analysis.
    """

    def __init__(self):
        self.agents = [
            KnowledgeAgent(),
            GnosisAgent(),
            NousAgent(),
            DoxaAgent(),
            ReductionAgent(),
            NOUSCOPEAgent(),
            CognitiveTherapyAgent(),
        ]

        self.detectors = DetectorEngine()
        self.question_generator = QuestionGenerator()
        self.interpreter = CognitiveInterpreter()
        self.revision_agent = RevisionAgent()

    def analyze(
        self,
        text: str,
        context: dict | None = None,
    ) -> dict[str, Any]:
        """
        Run the full symbolic cognitive analysis.
        """
    
        state = CognitiveState(
            user_input=text,
            context=context or {},
        )
    
        workspace = SharedCognitiveWorkspace(
            question=text,
            response="",
        )
    
        for agent in self.agents:
            if agent.can_handle(state):
                result = agent.analyze(state)
                state = agent.update_state(state, result)
    
                if result.get("agent") == "knowledge":
                    workspace.add_observation(
                        agent="Knowledge",
                        level=1.0,
                        observation=result.get(
                            "summary",
                            "Knowledge retrieved.",
                        ),
                        implication="Provides the factual basis for subsequent cognitive analysis.",
                        confidence=1.0,
                        signals=result,
                    )

                if result.get("agent") == "nous":
                    workspace.add_observation(
                        agent="Nous",
                        level=result.get("nous_level", 0.0),
                        observation=result.get(
                            "summary",
                            "No observation.",
                        ),
                        implication=(
                            "Evaluates the degree of integrated understanding "
                            "and conceptual coherence."
                        ),
                        confidence=result.get("nous_level", 0.0),
                        signals=result,
                    )
                    
                if result.get("agent") == "doxa":
                    workspace.add_observation(
                        agent="Doxa",
                        level=result.get("doxa_level", 0.0),
                        observation=result.get(
                            "summary",
                            "No observation.",
                        ),
                        implication=(
                            "Evaluates certainty, cognitive closure "
                            "and potential overconfidence."
                        ),
                        confidence=result.get("doxa_level", 0.0),
                        signals=result,
                    )
                if result.get("agent") == "reduction":
                    workspace.add_observation(
                        agent="Reduction",
                        level=result.get("reduction_level", 0.0),
                        observation=result.get(
                            "summary",
                            "No observation.",
                        ),
                        implication=(
                            "Evaluates simplifications, hidden assumptions "
                            "and possible forgotten reductions."
                        ),
                        confidence=result.get("reduction_level", 0.0),
                        signals=result,
                    )
                if result.get("agent") == "nouscope":
                    workspace.add_observation(
                        agent="NOUSCOPE",
                        level=result.get("cognitive_filter_level", 0.0),
                        observation=result.get(
                            "summary",
                            "No observation.",
                        ),
                        implication=(
                            "Evaluates possible cognitive filter influence, "
                            "including emotional, cultural and memory-based filters."
                        ),
                        confidence=result.get("cognitive_filter_level", 0.0),
                        signals=result,
                    )
    
        detector_results = self.detectors.analyze(state)
    
        interpretation = self.interpreter.interpret(
            detector_results
        )
    
        questions = self.question_generator.generate(
            {
                "detectors": detector_results,
            }
        )
    
        knowledge = state.metadata.get("knowledge", {})
        knowledge_answer = knowledge.get("answer", "")
    
        workspace.response = knowledge_answer
    
        response_analysis = None
        response_interpretation = None
        revision = None
    
        if knowledge_answer and knowledge_answer != "Knowledge not found in local knowledge base.":
            response_state = CognitiveState(
                user_input=knowledge_answer,
                context={
                    "analysis_target": "knowledge_response",
                },
            )
    
            response_analysis = self.detectors.analyze(response_state)
    
            revision = self.revision_agent.revise(
                knowledge_answer,
                response_analysis,
            )
    
            response_interpretation = self.interpreter.interpret(
                response_analysis
            )
    
        state.final_response = self._build_summary(
            state,
            detector_results,
        )
    
        return {
            "input": text,
            "active_agents": state.active_agents,
            "scores": {
                "gnosis": state.gnosis_level,
                "nous": state.nous_level,
                "doxa": state.doxa_level,
                "reduction": state.reduction_level,
                "revisability": state.revisability_level,
                "nouscope": state.metadata.get(
                    "nouscope",
                    {},
                ).get("cognitive_filter_level"),
            },
            "detectors": detector_results,
            "interpretation": interpretation,
            "response_analysis": response_analysis,
            "response_interpretation": response_interpretation,
            "revision": revision,
            "questions": questions,
            "analyses": state.analyses,
            "shared_workspace": workspace.summary(),
            "summary": state.final_response,
        }

    def _build_summary(
        self,
        state: CognitiveState,
        detector_results: dict[str, Any],
    ) -> str:
        """
        Build a first unified symbolic report.
        """

        mecroyance = detector_results["mecroyance"]
        risk = mecroyance["scores"]["mecroyance_risk"]

        return (
            "DeDe completed a symbolic cognitive analysis. "
            f"Gnosis={state.gnosis_level}, "
            f"Nous={state.nous_level}, "
            f"Doxa={state.doxa_level}, "
            f"Reduction={state.reduction_level}, "
            f"Revisability={state.revisability_level}, "
            f"MecroyanceRisk={risk}."
        )
