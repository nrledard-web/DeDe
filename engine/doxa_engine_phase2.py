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
import re

from search.search_engine import SearchEngine
from search.search_validator import SearchValidator
from search.search_query_builder import SearchQueryBuilder
from search.search_summarizer import SearchSummarizer

from llm.llm_engine import LLMEngine
from core.cognitive_workspace import CognitiveWorkspace

from knowledge.knowledge_agent import KnowledgeAgent
from knowledge.concept_extractor import ConceptExtractor
from knowledge.url_reader import URLReader
from knowledge.philosophical_retriever import PhilosophicalRetriever
from knowledge.historical_counterpoints.historical_counterpoint_retriever import (
    HistoricalCounterpointRetriever,
)

from semantic.semantic_engine import SemanticEngine
from semantic.semantic_reasoner import SemanticReasoner
from semantic.semantic_graph import SemanticGraph
from semantic.graph_query_engine import GraphQueryEngine

from estimators.estimator_engine import EstimatorEngine

from memory.memory_retriever import MemoryRetriever
from memory.memory_governor import MemoryGovernor
from memory.persistent_memory import PersistentMemory
from memory.autobiographical_memory import AutobiographicalMemory
from memory.autobiographical_reasoner import AutobiographicalReasoner

from core.dede_identity import DeDeIdentity
from core.dede_state import DeDeState
from memory.user_memory import UserMemory
from dialogue.dialogue_manager import DialogueManager

from identity.onboarding import Onboarding

from reasoning.inference_engine import InferenceEngine
from reasoning.cognitive_compiler import CognitiveCompiler
from reasoning.cognitive_reasoner import CognitiveReasoner
from reasoning.cognitive_feedback import CognitiveFeedback
from reasoning.committee_reasoner import CommitteeReasoner

from dialogue.cognitive_dialogue_manager import CognitiveDialogueManager
from dialogue.response_builder import ResponseBuilder
from dialogue.dialogue_governor import DialogueGovernor
from dialogue.conversation_manager import ConversationManager
from dialogue.conversation_reasoner import ConversationReasoner
from dialogue.dialogue_profile import DialogueProfile

from llm.llm_connector import LLMConnector
from llm.llm_response_interpreter import LLMResponseInterpreter
from llm.llm_bridge import LLMBridge

from committee.cognitive_committee import CognitiveCommittee

from core.daimon_filter import DaimonFilter
from governance.cognitive_governor import CognitiveGovernor

from formulas.doxa_formula_engine import DoxaFormulaEngine
from agents.nous_agent import NousAgent
from agents.doxa_agent import DoxaAgent
from agents.reduction_agent import ReductionAgent
from agents.nouscope_agent import NOUSCOPEAgent
from agents.cognitive_therapy_agent import CognitiveTherapyAgent

from analysis.text_analysis_engine import TextAnalysisEngine
from analysis.cognitive_comparator import CognitiveComparator
from analysis.source_analysis_engine import SourceAnalysisEngine

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
        self.url_reader = URLReader()
        self.concept_extractor = ConceptExtractor()
        self.philosophical_retriever = PhilosophicalRetriever()
        self.historical_counterpoint_retriever = (
            HistoricalCounterpointRetriever()
        )
        self.semantic_engine = SemanticEngine()
        self.semantic_reasoner = SemanticReasoner()
        self.semantic_graph = SemanticGraph()
        self.onboarding = Onboarding()
        self.user_memory = UserMemory()
        self.memory_governor = MemoryGovernor()
        self.persistent_memory = PersistentMemory(
            user_id=user_id,
        )
        self._initialize_owner_profile(user_id)
        self.memory_retriever = MemoryRetriever()
        self.autobiographical_memory = AutobiographicalMemory()
        self.autobiographical_reasoner = AutobiographicalReasoner()
        self.dede_identity = DeDeIdentity()
        self.dede_state = DeDeState()
        self.daimon_filter = DaimonFilter()
        self.cognitive_governor = CognitiveGovernor()
        
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
        self.committee_reasoner = CommitteeReasoner()
        self.cognitive_feedback = CognitiveFeedback()
        self.dialogue_manager = DialogueManager()
        self.cognitive_dialogue_manager = CognitiveDialogueManager()
        self.response_builder = ResponseBuilder()
        self.dialogue_governor = DialogueGovernor()
        self.conversation_manager = ConversationManager()
        self.conversation_reasoner = ConversationReasoner()
        self.dialogue_profile = DialogueProfile()
        self.search_engine = SearchEngine()
        self.search_validator = SearchValidator()
        self.search_query_builder = SearchQueryBuilder()
        self.search_summarizer = SearchSummarizer()
        self.text_analysis_engine = TextAnalysisEngine()
        self.cognitive_comparator = CognitiveComparator()
        self.source_analysis_engine = SourceAnalysisEngine()

        # --------------------------------------------------
        # LLM preparation layers
        # --------------------------------------------------
        self.llm_connector = LLMConnector()
        self.llm_bridge = LLMBridge()
        self.llm_response_interpreter = LLMResponseInterpreter()
        self.llm_engine = LLMEngine()

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
        
    def _initialize_owner_profile(
        self,
        user_id: str,
    ) -> None:
        """
        Initialize a human owner profile from the technical Owner ID.
    
        Owner ID is technical.
        preferred_name is human-facing.
        """
    
        memory = self.persistent_memory.get_memory()
    
        owner = memory.setdefault("owner", {})
    
        owner.setdefault("id", user_id)
    
        if not owner.get("preferred_name"):
            owner["preferred_name"] = self._owner_id_to_name(user_id)
    
        self.persistent_memory.data = memory
        self.persistent_memory.save()

    def _owner_id_to_name(
        self,
        user_id: str,
    ) -> str:
        """
        Convert a technical owner id into a readable default name.
        """
    
        cleaned = user_id.replace("_", " ").replace("-", " ").strip()
    
        if not cleaned:
            return "Owner"
    
        return cleaned.title()

    def _build_search_query(
        self,
        text: str,
        conversation_context: dict[str, Any] | None = None,
        concept_data: dict[str, Any] | None = None,
    ) -> str:

        conversation_context = conversation_context or {}
        concept_data = concept_data or {}

        concepts = concept_data.get("main_concepts", [])

        strong_concepts = [
            item
            for item in concepts
            if item
        ]

        if strong_concepts:
            return " ".join(strong_concepts[:3])

        recent_topics = conversation_context.get("recent_topics", [])

        if recent_topics:
            return str(recent_topics[-1])

        return text
    
    def analyze(
        self,
        text: str,
        document_context: dict[str, Any] | None = None,
        enable_llm: bool = False,
        search_provider: str | list[str] = "none",
        search_profile: str | None = None,
        search_mode: str = "off",
        llm_profile: str = "fast",
        llm_providers: list[str] | None = None,
        knowledge_providers: list[str] | None = None,
        knowledge_mode: str = "best",
        conversation_history: list[dict[str, Any]] | None = None,
        explicit_search_request: bool = False,
    ) -> dict[str, Any]:
        """
        Run the complete DeDe Phase 2 cognitive pipeline.
        """

        document_context = (
            document_context or {}
        )

        workspace = CognitiveWorkspace(
            text=text
        )

        workspace.add_interpretation(
            "document_context",
            document_context,
        )

        # --------------------------------------------------
        # Universal Text Analysis — User Input
        # --------------------------------------------------

        user_text_analysis = self.text_analysis_engine.analyze(
            text=text,
            source_type="user",
            provenance={
                "origin": "conversation",
                "role": "user",
            },
            context={
                "pipeline": "doxa_engine_phase2",
            },
        )

        workspace.add_interpretation(
            "user_text_analysis",
            user_text_analysis,
        )

        url_read_result = self.url_reader.read_first_url(text)

        workspace.add_interpretation(
            "url_read_result",
            url_read_result,
        )

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

        persistent_memory = self.persistent_memory.get_memory()
        owner_profile = persistent_memory.get("owner", {})
        
        user_memory.setdefault("owner", {})
        user_memory["owner"]["id"] = owner_profile.get("id")
        user_memory["owner"]["preferred_name"] = owner_profile.get("preferred_name")

        memory_governance = self.memory_governor.evaluate(text)
        
        if memory_governance.get("allow_persistent_storage", True):
            persistent_memory = self.persistent_memory.merge_user_memory(
                user_memory,
            )
        else:
            persistent_memory = self.persistent_memory.get_memory()

        if memory_governance.get("allow_persistent_storage", True):
            persistent_memory = self.autobiographical_memory.update(
                text=text,
                persistent_memory=persistent_memory,
            )
            self.persistent_memory.data = persistent_memory
            self.persistent_memory.save()

        retrieved_memory = self.memory_retriever.retrieve(
            text=text,
            persistent_memory=persistent_memory,
        )
        
        autobiographical_reasoning = self.autobiographical_reasoner.reason(
            persistent_memory=persistent_memory,
        )
        
        workspace.add_interpretation(
            "autobiographical_reasoning",
            autobiographical_reasoning,
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
            retrieved_memory=retrieved_memory,
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
        knowledge_result = self.knowledge.analyze(
            workspace=workspace,
            selected_providers=knowledge_providers,
            mode=knowledge_mode,
        )

        # --------------------------------------------------
        # Phase 4.1
        # Concept Extraction + Semantic Engine + Semantic Reasoner
        # --------------------------------------------------
        workspace = self.concept_extractor.run(workspace)
        workspace = self.semantic_engine.run(workspace)
        workspace = self.semantic_reasoner.run(workspace)

        # --------------------------------------------------
        # Foundational Philosophical Retrieval
        # --------------------------------------------------

        concept_data = workspace.interpretations.get(
            "concepts",
            {},
        )

        philosophical_context = (
            self.philosophical_retriever.retrieve(
                text=text,
                concept_data=concept_data,
            )
        )

        workspace.add_interpretation(
            "philosophical_context",
            philosophical_context,
        )

        # --------------------------------------------------
        # Phase 5.4b
        # Search Provider
        # --------------------------------------------------

        search_mode = (
            search_mode
            or "off"
        ).lower().strip()

        semantic_search_classification = {
            "status": "not_required",
            "decision": None,
            "reason": (
                "Semantic classification was not required "
                "for the selected search mode."
            ),
            "raw_response": "",
        }

        # --------------------------------------------------
        # Semantic Search Classification
        # --------------------------------------------------

        if search_mode in {
            "on_request",
            "governor",
        }:

            if enable_llm and llm_providers:
                classification_prompt = (
                    self.cognitive_governor
                    .build_search_classification_prompt(
                        text=text,
                        conversation_context=conversation_context,
                        search_mode=search_mode,
                    )
                )

                classification_response = self.llm_engine.ask(
                    prompt=classification_prompt,
                    profile="fast",
                    providers=llm_providers,
                    enabled=True,
                )

                semantic_search_classification = (
                    self.cognitive_governor
                    .parse_search_classification(
                        classification_response.get(
                            "response",
                            "",
                        )
                    )
                )

            else:
                semantic_search_classification = {
                    "status": "unavailable",
                    "decision": "SKIP",
                    "reason": (
                        "Semantic search classification requires an "
                        "active reasoning model. Search was skipped safely."
                    ),
                    "raw_response": "",
                }

        # --------------------------------------------------
        # Historical Counterpoint Retrieval
        # --------------------------------------------------

        canonical_concepts = (
            semantic_search_classification.get(
                "canonical_concepts",
                [],
            )
        )

        selected_counterpoint_ids = (
            semantic_search_classification.get(
                "counterpoint_ids",
                [],
            )
        )

        historical_counterpoint_context = (
            self.historical_counterpoint_retriever.retrieve(
                selected_counterpoint_ids=selected_counterpoint_ids,
                canonical_concepts=canonical_concepts,
                text=text,
            )
        )

        workspace.add_interpretation(
            "historical_counterpoint_context",
            historical_counterpoint_context,
        )

        # --------------------------------------------------
        # Final Search Decision
        # --------------------------------------------------

        search_decision = self.cognitive_governor.decide_search(
            search_mode=search_mode,
            explicit_request=explicit_search_request,
            semantic_decision=(
                semantic_search_classification.get(
                    "decision"
                )
            ),
            semantic_reason=(
                semantic_search_classification.get(
                    "reason"
                )
            ),
        )
        
        should_search = search_decision.get(
            "should_search",
            False,
        )

        workspace.add_interpretation(
            "search_decision",
            search_decision,
        )

        workspace.add_interpretation(
            "semantic_search_classification",
            semantic_search_classification,
        )

        if should_search:

            if not search_provider and search_profile:
                search_provider = search_profile

            # --------------------------------------------------
            # Semantic Search Query
            # --------------------------------------------------
            # The selected reasoning model converts the natural-language
            # request into a concise search-engine query.
            #
            # No language-specific markers, stop-word lists or personal
            # identifiers are used.

            original_search_request = text.strip()

            search_query = original_search_request

            query_rewrite_status = "fallback"
            query_rewrite_response = ""

            if enable_llm and llm_providers:

                query_rewrite_prompt = (
                    "Convert the following user request into a concise "
                    "web-search query.\n\n"

                    "Preserve the central subject and any necessary names, "
                    "dates, places or technical qualifiers.\n"

                    "When the subject is an ideology, doctrine, political "
                    "system, religious system or economic model, include the "
                    "historical dimensions needed to confront its declared "
                    "principles with reality: applications, institutions, "
                    "repression, political violence, camps, deportations, "
                    "famines, human consequences and credible estimates of "
                    "victims whenever these dimensions are relevant.\n"

                    "Do not assume in advance that these consequences occurred. "
                    "Formulate the query so that external sources can confirm, "
                    "reject or qualify them.\n"

                    "Remove conversational phrasing, politeness and requests "
                    "to explain, summarize or provide links.\n"
                    "Do not answer the request.\n"
                    "Do not add commentary.\n"
                    "Return only the search query on one line.\n\n"
                    f"User request:\n{original_search_request}"
                )

                query_rewrite_result = self.llm_engine.ask(
                    prompt=query_rewrite_prompt,
                    profile="fast",
                    providers=llm_providers,
                    enabled=True,
                )

                query_rewrite_response = str(
                    query_rewrite_result.get(
                        "response",
                        "",
                    )
                    or ""
                ).strip()

                # Preserve only the first non-empty line.
                rewritten_lines = [
                    line.strip()
                    for line in query_rewrite_response.splitlines()
                    if line.strip()
                ]

                if rewritten_lines:
                    candidate_query = rewritten_lines[0].strip(
                        " `\"'"
                    )

                    # Remove a possible generic label returned by the model.
                    if ":" in candidate_query:
                        prefix, remainder = candidate_query.split(
                            ":",
                            1,
                        )

                        if (
                            len(prefix.split()) <= 3
                            and remainder.strip()
                        ):
                            candidate_query = remainder.strip(
                                " `\"'"
                            )
                            
                    # Safe length control.
                    candidate_words = candidate_query.split()

                    if len(candidate_words) > 12:
                        candidate_query = " ".join(
                            candidate_words[:12]
                        )

                    if candidate_query:
                        search_query = candidate_query
                    
                        search_query = self._clean_search_query(
                            query=search_query,
                            original_text=original_search_request,
                        )
                    
                        query_rewrite_status = "success"

            search_query_data = {
                "builder": "semantic_search_query",
                "status": query_rewrite_status,
                "query": search_query,
                "original_text": original_search_request,
                "source": (
                    "reasoning_model"
                    if query_rewrite_status == "success"
                    else "original_text_fallback"
                ),
                "raw_model_response": query_rewrite_response,
                "summary": (
                    "The user request was semantically converted into "
                    f"the search query: '{search_query}'."
                    if query_rewrite_status == "success"
                    else (
                        "Semantic query rewriting was unavailable. "
                        "The original request was preserved."
                    )
                ),
            }

            print("=" * 80)
            print("SEARCH DIAGNOSTIC")
            print("ORIGINAL TEXT :", text)
            print("QUERY DATA :", search_query_data)
            print("FINAL QUERY :", search_query)
            print("PROVIDER :", search_provider)
            print("MODE :", search_mode)
            print("=" * 80)

            # Never send an empty query.
            if not search_query:
                search_query = text.strip()

                search_query_data = {
                    **search_query_data,
                    "status": "fallback",
                    "query": search_query,
                    "source": "original_text_fallback",
                    "summary": (
                        "Search query builder returned no usable topic; "
                        "the original message was preserved."
                    ),
                }

            # --------------------------------------------------
            # First search
            # --------------------------------------------------

            print("=" * 80)
            print("SEARCH QUERY BUILT :", repr(search_query))
            print("=" * 80)
            
            search_result = self.search_engine.search(
                query=search_query,
                provider=search_provider,
            )

            print("=" * 80)
            print("SEARCH ENGINE RESULT")
            print("QUERY SENT :", search_query)
            print("STATUS :", search_result.get("status"))
            print("RESULT COUNT :", len(search_result.get("results", [])))
            print("FULL RESULT :", search_result)
            print("=" * 80)

            search_validation = self.search_validator.validate(
                query=search_query,
                search_result=search_result,
            )

            # --------------------------------------------------
            # Optional fallback search
            # --------------------------------------------------

            if not search_validation.get(
                "is_relevant",
                False,
            ):
                fallback_query = (
                    f"{search_query} wikipedia"
                )

                fallback_result = self.search_engine.search(
                    query=fallback_query,
                    provider=search_provider,
                )

                fallback_validation = (
                    self.search_validator.validate(
                        query=fallback_query,
                        search_result=fallback_result,
                    )
                )

                original_relevance = float(
                    search_validation.get(
                        "relevance",
                        0.0,
                    )
                )

                fallback_relevance = float(
                    fallback_validation.get(
                        "relevance",
                        0.0,
                    )
                )

                if fallback_relevance > original_relevance:
                    initial_query = search_query

                    search_query = fallback_query
                    search_result = fallback_result
                    search_validation = fallback_validation

                    search_query_data = {
                        **search_query_data,
                        "fallback_used": True,
                        "initial_query": initial_query,
                        "query": fallback_query,
                    }

                else:
                    search_query_data["fallback_used"] = False

            # --------------------------------------------------
            # Preserve results even when relevance is limited
            # --------------------------------------------------

            results = search_result.get(
                "results",
                [],
            )

            if (
                results
                and not search_validation.get(
                    "is_relevant",
                    False,
                )
            ):
                search_result["status"] = "low_relevance"

                search_result["summary"] = (
                    "Search completed. Results were preserved, "
                    "but their relevance may be limited."
                )

            elif not results:
                search_result["status"] = "no_results"

                search_result["summary"] = (
                    "No search results were found for "
                    f"'{search_query}'."
                )

            search_summary = self.search_summarizer.summarize(
                search_result=search_result,
                search_validation=search_validation,
            )

        else:
            search_query = text

            search_query_data = {
                "builder": "search_query_builder",
                "status": "disabled",
                "query": text,
                "source": "disabled",
                "summary": (
                    "Search query builder skipped."
                ),
            }

            search_result = {
                "engine": "search_engine",
                "status": "disabled",
                "provider": "none",
                "providers": [],
                "query": text,
                "results": [],
                "provider_results": [],
                "summary": (
                    f"Search skipped (mode={search_mode})."
                ),
            }

            search_validation = {
                "validator": "search_validator",
                "status": "disabled",
                "query": text,
                "relevance": 0.0,
                "is_relevant": False,
                "summary": (
                    "Search validation skipped."
                ),
            }

            search_summary = {
                "summarizer": "search_summarizer",
                "status": "disabled",
                "sources": [],
                "summary_text": "",
                "summary": (
                    "Search summarizer skipped."
                ),
            }

        # --------------------------------------------------
        # Universal Text Analysis — Web Results
        # --------------------------------------------------

        web_analysis_items = []

        for index, result_item in enumerate(
            search_result.get(
                "results",
                [],
            )
        ):
            if not isinstance(result_item, dict):
                continue

            title = str(
                result_item.get(
                    "title",
                    "",
                )
                or ""
            ).strip()

            snippet = str(
                result_item.get(
                    "snippet",
                    "",
                )
                or ""
            ).strip()

            web_text = "\n\n".join(
                value
                for value in [
                    title,
                    snippet,
                ]
                if value
            )

            if not web_text:
                continue

            web_analysis_items.append(
                {
                    "text": web_text,
                    "source_type": "web",
                    "provenance": {
                        "result_index": index,
                        "provider": result_item.get(
                            "provider",
                            search_result.get(
                                "provider",
                                "unknown",
                            ),
                        ),
                        "title": title,
                        "url": result_item.get(
                            "url",
                            "",
                        ),
                        "query": search_query,
                    },
                }
            )

        web_text_analysis = (
            self.text_analysis_engine.analyze_many(
                items=web_analysis_items,
                source_type="web",
                shared_context={
                    "search_mode": search_mode,
                    "search_query": search_query,
                },
            )
        )

        workspace.add_interpretation(
            "web_text_analysis",
            web_text_analysis,
        )
        
        # --------------------------------------------------
        # Cognitive Source Analysis
        # --------------------------------------------------

        retrieved_sources = search_result.get(
            "results",
            [],
        )

        if retrieved_sources:

            if enable_llm and llm_providers:
                source_analysis_prompt = (
                    self.source_analysis_engine.build_prompt(
                        search_results=retrieved_sources,
                        user_request=text,
                        search_query=search_query,
                    )
                )

                source_analysis_response = self.llm_engine.ask(
                    prompt=source_analysis_prompt,
                    profile="fast",
                    providers=llm_providers,
                    enabled=True,
                )

                source_analysis = (
                    self.source_analysis_engine.parse_response(
                        model_response=source_analysis_response.get(
                            "response",
                            "",
                        ),
                        search_results=retrieved_sources,
                    )
                )

            else:
                source_analysis = (
                    self.source_analysis_engine.unavailable(
                        search_results=retrieved_sources,
                        reason=(
                            "Source analysis requires an active "
                            "reasoning model."
                        ),
                    )
                )

        else:
            source_analysis = {
                "engine": "source_analysis_engine",
                "status": "empty",
                "source_count": 0,
                "sources": [],
                "aggregate": {
                    "source_type_counts": {},
                    "average_scores": {},
                },
                "overall_summary": (
                    "No retrieved source was available for analysis."
                ),
                "raw_response": "",
            }

        workspace.add_interpretation(
            "source_analysis",
            source_analysis,
        )
        print("=" * 80)
        print("SOURCE ANALYSIS")
        print(source_analysis)
        print("=" * 80)

        print("=" * 80)
        print("SEARCH MODE :", search_mode)
        print("SEARCH PROVIDER :", search_provider)
        print("SEARCH QUERY :", search_query)
        print("SEARCH RESULT :", search_result)
        print("=" * 80)
        print(
            "SEARCH VALIDATION :",
            search_validation,
        )

        workspace.add_interpretation(
            "search_result",
            search_result,
        )

        workspace.add_interpretation(
            "search_validation",
            search_validation,
        )

        workspace.add_interpretation(
            "search_query",
            search_query_data,
        )

        workspace.add_interpretation(
            "search_summary",
            search_summary,
        )

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
        print("=" * 80)
        print("SEARCH SENT TO LLM CONNECTOR")
        print("STATUS :", search_result.get("status"))
        print("QUERY :", search_result.get("query"))
        print("RESULT COUNT :", len(search_result.get("results", [])))
        print("SUMMARY :", search_summary)
        print("=" * 80)

        
        llm_package = self.llm_connector.build_prompt_package(
            text=text,
            graph_queries=graph_queries,
            cognitive_state=cognitive_state,
            cognitive_reasoning=cognitive_reasoning,
            user_memory=user_memory,
            persistent_memory=self.persistent_memory.get_memory(),
            retrieved_memory=retrieved_memory,
            autobiographical_reasoning=autobiographical_reasoning,
            philosophical_context=philosophical_context,
            historical_counterpoint_context=(
                historical_counterpoint_context
            ),
            document_context=document_context,
            dede_identity=identity_state,
            dede_state=dede_state,
            search_result=search_result,
            search_summary=search_summary,
            source_analysis=source_analysis,
            url_read_result=url_read_result,
        )

        # --------------------------------------------------
        # Cognitive Governor 4.11b
        # --------------------------------------------------

        llm_package = self.cognitive_governor.apply_to_prompt_package(
            llm_package=llm_package,
            search_result=search_result,
            search_validation=search_validation,
            search_summary=search_summary,
            retrieved_memory=retrieved_memory,
        )

        workspace.add_interpretation(
            "llm_package",
            llm_package,
        )

        workspace.add_interpretation(
            "cognitive_governor",
            llm_package.get("cognitive_governor", {}),
        )

        # --------------------------------------------------
        # Phase 4.12
        # LLM Bridge
        # --------------------------------------------------
        llm_engine_response = self.llm_engine.ask(
            prompt=llm_package.get("full_prompt", ""),
            profile=llm_profile,
            providers=llm_providers,
            enabled=enable_llm,
        )
        
        llm_bridge_response = {
            "status": llm_engine_response.get("status"),
            "provider": "+".join(llm_engine_response.get("providers", [])),
            "response": llm_engine_response.get("response", ""),
            "parsed_json": None,
            "json_valid": False,
            "llm_engine": llm_engine_response,
            "summary": llm_engine_response.get("summary", ""),
        }

        workspace.add_interpretation(
            "llm_bridge_response",
            llm_bridge_response,
        )
        committee_reasoning = self.committee_reasoner.analyze(
            llm_bridge_response.get(
                "llm_engine",
                {},
            ).get(
                "committee",
                {},
            )
        )
        
        workspace.add_interpretation(
            "committee_reasoning",
            committee_reasoning,
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
            llm_response=llm_interpretation.get("raw_response"),
            parsed_json=llm_interpretation.get("parsed_json"),
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
            "llm_interpretation": llm_interpretation,
            "committee": committee_result,
            "formulas": formulas,
            "dialogue": dialogue,
            "user_memory": user_memory,
            "dede_identity": identity_state,
            "search_result": search_result,
            "search_summary": search_summary,
            "committee_reasoning": committee_reasoning,
            "summary": self._build_summary(
                workspace,
                committee_result,
                formulas,
            ),
        }
    
        user_response = self.response_builder.build(
            dialogue_context,
        )
        
        # ----------------------------------------
        # Daimon Filter
        # ----------------------------------------

        user_response = self.daimon_filter.filter_response(
            response=user_response,
            dede_state=dede_state,
        )
        
        # ----------------------------------------
        # Dialogue Governor
        # ----------------------------------------

        if isinstance(user_response, dict):
            for key in [
                "final_answer",
                "response",
                "message",
                "text",
                "content",
                "answer",
                "user_facing_response",
            ]:
                if (
                    key in user_response
                    and isinstance(
                        user_response[key],
                        str,
                    )
                ):
                    user_response[key] = (
                        self.dialogue_governor.apply(
                            user_response[key]
                        )
                    )

        # --------------------------------------------------
        # Universal Text Analysis — Final DeDe Response
        # --------------------------------------------------

        final_response_text = ""

        if isinstance(user_response, str):
            final_response_text = user_response.strip()

        elif isinstance(user_response, dict):

            # Most likely direct response fields.
            response_keys = [
                "final_answer",
                "response",
                "message",
                "text",
                "content",
                "answer",
                "user_facing_response",
            ]

            for response_key in response_keys:
                candidate = user_response.get(
                    response_key
                )

                if isinstance(candidate, str) and candidate.strip():
                    final_response_text = candidate.strip()
                    break

            # Safe fallback for a nested dialogue structure.
            if not final_response_text:
                for container_key in [
                    "dialogue",
                    "result",
                    "output",
                ]:
                    nested = user_response.get(
                        container_key
                    )

                    if not isinstance(nested, dict):
                        continue

                    for response_key in response_keys:
                        candidate = nested.get(
                            response_key
                        )

                        if isinstance(candidate, str) and candidate.strip():
                            final_response_text = candidate.strip()
                            break

                    if final_response_text:
                        break

        final_response_analysis = (
            self.text_analysis_engine.analyze(
                text=final_response_text,
                source_type="final_response",
                provenance={
                    "origin": "dede",
                    "role": "assistant",
                    "llm_providers": (
                        llm_providers
                        or []
                    ),
                    "search_used": bool(
                        search_result.get(
                            "results",
                            [],
                        )
                    ),
                },
                context={
                    "search_mode": search_mode,
                    "search_query": search_query,
                },
            )
        )

        workspace.add_interpretation(
            "final_response_analysis",
            final_response_analysis,
        )
        
        # --------------------------------------------------
        # Cognitive Comparison
        # --------------------------------------------------

        cognitive_comparison = (
            self.cognitive_comparator.compare(
                user_analysis=workspace.interpretations.get(
                    "user_text_analysis",
                    {},
                ),
                web_analysis=workspace.interpretations.get(
                    "web_text_analysis",
                    {},
                ),
                final_analysis=final_response_analysis,
            )
        )

        workspace.add_interpretation(
            "cognitive_comparison",
            cognitive_comparison,
        )

        print("=" * 80)
        print("FINAL RESPONSE ANALYSIS DIAGNOSTIC")
        print("USER RESPONSE TYPE :", type(user_response).__name__)
        print("USER RESPONSE :", user_response)
        print("FINAL RESPONSE TEXT :", repr(final_response_text))
        print(
            "FINAL ANALYSIS STATUS :",
            final_response_analysis.get(
                "status",
            ),
        )
        print("=" * 80)

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
            "autobiography": self.persistent_memory.get_memory().get(
                "autobiography",
                {},
            ),
            "autobiographical_reasoning": workspace.interpretations.get(
                "autobiographical_reasoning",
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
            "memory_governance": memory_governance,
            "concepts": workspace.interpretations.get("concepts", {}),
            "philosophical_context": (
                workspace.interpretations.get(
                    "philosophical_context",
                    {},
                )
            ),
            "document_context": {
                "status": document_context.get(
                    "status",
                    "unavailable",
                ),
                "source_type": document_context.get(
                    "source_type",
                    "",
                ),
                "filename": document_context.get(
                    "filename",
                    "",
                ),
                "page_count": document_context.get(
                    "page_count",
                    0,
                ),
                "pages_read": document_context.get(
                    "pages_read",
                    0,
                ),
                "word_count": document_context.get(
                    "word_count",
                    0,
                ),
                "character_count": document_context.get(
                    "character_count",
                    0,
                ),
                "metadata": document_context.get(
                    "metadata",
                    {},
                ),
                "summary": document_context.get(
                    "summary",
                    "",
                ),
            },
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
            "llm_engine_response": workspace.interpretations.get(
                "llm_bridge_response",
                {},
            ).get("llm_engine", {}),
            
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

            "user_text_analysis": (
                workspace.interpretations.get(
                    "user_text_analysis",
                    {},
                )
            ),
            "web_text_analysis": (
                workspace.interpretations.get(
                    "web_text_analysis",
                    {},
                )
            ),
            "source_analysis": (
                workspace.interpretations.get(
                    "source_analysis",
                    {},
                )
            ),
            "final_response_analysis": (
                workspace.interpretations.get(
                    "final_response_analysis",
                    {},
                )
            ),
            "cognitive_comparison": (
                workspace.interpretations.get(
                    "cognitive_comparison",
                    {},
                )
            ),
            "search_result": workspace.interpretations.get(
                "search_result",
                {},
            ),
            "committee_reasoning": workspace.interpretations.get(
                "committee_reasoning",
                {},
            ),
            "url_read_result": workspace.interpretations.get(
                "url_read_result",
                {},
            ),
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

    def _clean_search_query(
        self,
        query: str,
        original_text: str = "",
    ) -> str:
        """
        Remove residual output-format words from a query already
        rewritten by the reasoning model.
        """

        cleaned = str(query or "").strip()

        if not cleaned:
            cleaned = str(original_text or "").strip()

        if not cleaned:
            return ""

        removable_words = {
            "link",
            "links",
            "website",
            "websites",
            "webpage",
            "webpages",
            "lien",
            "liens",
            "site",
            "sites",
            "enlace",
            "enlaces",
            "sitio",
            "sitios",
        }

        words = cleaned.split()

        filtered_words = [
            word
            for word in words
            if word.lower().strip(
                ".,;:!?()[]{}"
            ) not in removable_words
        ]

        cleaned = " ".join(
            filtered_words
        ).strip()

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned,
        ).strip()

        if len(cleaned) < 2:
            return str(
                original_text or query or ""
            ).strip()

        return cleaned

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
