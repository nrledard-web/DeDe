import streamlit as st
from openai import OpenAI
import tempfile
import os

from engine.doxa_engine_phase2 import DoxaEnginePhase2
from pathlib import Path
from core.real_world_anchor import RealWorldAnchor

def pct(value):
    if value is None:
        return "N/A"
    return f"{round(value * 100)}%"


def show_metric(label, value):
    st.metric(label, pct(value))
    
def generate_speech(text: str) -> bytes | None:
    if not text:
        return None

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
    )

    return speech.content

st.set_page_config(
    page_title="DeDe",
    page_icon="🧠",
    layout="wide",
)

if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

# --------------------------------------------------
# Force light theme / mobile readability
# --------------------------------------------------

st.markdown(
    """
    <style>
    :root {
        color-scheme: light !important;
    }

    html, body, .stApp {
        background-color: #ffffff !important;
        color: #111827 !important;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #ffffff !important;
        color: #111827 !important;
    }

    [data-testid="stHeader"] {
        background-color: #ffffff !important;
    }

    [data-testid="stToolbar"] {
        color: #111827 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #f9fafb !important;
        color: #111827 !important;
    }

    h1, h2, h3, h4, h5, h6,
    p, span, div, label,
    .stMarkdown, .stText {
        color: #111827 !important;
    }

    input, textarea {
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
    }

    button {
        background-color: #f3f4f6 !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
    }

    [data-testid="stChatMessage"] {
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
    }

    [data-testid="stChatInput"] {
        background-color: #ffffff !important;
        color: #111827 !important;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }

        h1 {
            font-size: 1.6rem !important;
        }

        h2 {
            font-size: 1.3rem !important;
        }

        h3 {
            font-size: 1.1rem !important;
        }

        p, div, span, label {
            font-size: 0.95rem !important;
        }

        [data-testid="stChatMessage"] {
            padding: 0.65rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

BANNER_PATH = Path("assets/Banner01.png")

if BANNER_PATH.exists():
    st.image(str(BANNER_PATH), width="stretch")
else:
    st.warning("Banner01.png not found in assets/")

st.title("DeDe — Cognitive Daimon")
st.markdown(
    "<p style='text-align:center; color:#6b7280;'><strong>An AI Reasoning Controller</strong></p>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#6b7280;'><strong>A little more time to think leads to more accurate answers.</strong></p>",
    unsafe_allow_html=True,
)

st.caption("Phase 3 — Cognitive Mechanics")

with st.expander("Prototype status"):
    st.success("DeDe Phase 3 prototype is running.")

    st.caption(
        "Current status: CognitiveWorkspace, estimator layer, "
        "agent interpretation and shared cognitive mechanics."
    )

# --------------------------------------------------
# DeDe Sidebar Configuration
# --------------------------------------------------

with st.sidebar:

    st.markdown("## ⚙️ DeDe Configuration")

    st.caption(
        "Identity, reasoning models and knowledge sources."
    )

    # --------------------------------------------------
    # Owner Identity
    # --------------------------------------------------

    st.markdown("### Identity")

    owner_id = st.text_input(
        "Owner ID",
        value=st.session_state.get("owner_id", ""),
        placeholder="Ex: nicolas, delia, test_user",
    )

    if owner_id:
        safe_owner_id = "".join(
            char for char in owner_id.lower().strip()
            if char.isalnum() or char in ["_", "-"]
        )

        if st.session_state.get("owner_id") != safe_owner_id:
            st.session_state.owner_id = safe_owner_id
            st.session_state.conversation_history = []
            st.session_state.engine = DoxaEnginePhase2(
                user_id=safe_owner_id,
            )
            st.success(
                f"Memory owner set to: {safe_owner_id}"
            )
    else:
        st.warning(
            "Enter an Owner ID to use an isolated persistent memory."
        )
        st.stop()

    # --------------------------------------------------
    # Conversation Session
    # --------------------------------------------------

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "engine" not in st.session_state and st.session_state.get("owner_id"):
        st.session_state.engine = DoxaEnginePhase2(
            user_id=st.session_state.owner_id,
        )

    # --------------------------------------------------
    # Reasoning Models
    # --------------------------------------------------

    st.markdown("### Reasoning Models")

    enable_llm = True

    st.caption(
        "Choose which reasoning models DeDe may use."
    )

    llm_model_options = {
        "OpenAI": "openai",
        "Gemini": "gemini",
        "Mistral": "mistral",
        "DeepSeek — planned": "deepseek",
        "Qwen — planned": "qwen",
        "GLM — planned": "glm",
        "Claude — planned": "claude",
        "Nemotron — planned": "nemotron",
    }

    selected_llm_labels = st.multiselect(
        "Reasoning Models",
        list(llm_model_options.keys()),
        default=[
            "OpenAI",
        ],
    )

    llm_providers = [
        llm_model_options[label]
        for label in selected_llm_labels
    ]

    llm_profile = "custom"

    active_llms = [
        provider
        for provider in llm_providers
        if provider in ["openai", "gemini", "mistral"]
    ]

    planned_llms = [
        provider
        for provider in llm_providers
        if provider not in ["openai", "gemini", "mistral"]
    ]

    st.caption(
        "Active: "
        + (", ".join(active_llms) if active_llms else "none")
        + " | Planned: "
        + (", ".join(planned_llms) if planned_llms else "none")
    )

    # --------------------------------------------------
    # Knowledge Sources
    # --------------------------------------------------

    st.markdown("### Knowledge Sources")

    st.caption(
        "Choose the knowledge profile and search strategy."
    )

    search_profile_labels = {
        "General — DuckDuckGo": "general",
        "Scientific — DuckDuckGo + ArXiv + CrossRef": "scientific",
        "Shopping — DuckDuckGo": "shopping",
        "News — DuckDuckGo": "news",
        "Programming — DuckDuckGo": "programming",
        "Legal — DuckDuckGo": "legal",
        "Custom": "custom",
    }

    selected_search_label = st.selectbox(
        "Knowledge Profile",
        list(search_profile_labels.keys()),
        index=0,
    )

    search_profile = search_profile_labels[selected_search_label]

    search_strategy = st.selectbox(
        "Search Strategy",
        [
            "Off",
            "On Request",
            "Governor (Beta)",
        ],
        index=1,
    )

    st.caption(
        "Off: no external search. "
        "On Request: search when the message requests external information. "
        "Governor: search automatically when verification is needed."
    )

    search_mode_map = {
        "Off": "off",
        "On Request": "on_request",
        "Governor (Beta)": "governor",
    }

    search_mode = search_mode_map[search_strategy]

    search_provider = []

    if search_profile == "custom":

        search_provider = st.multiselect(
            "Custom Search Providers",
            [
                "duckduckgo",
                "arxiv",
                "crossref",
                "brave — planned",
                "serpapi — planned",
                "pubmed — planned",
                "github — planned",
                "newsapi — planned",
                "semantic_scholar — planned",
                "eur_lex — planned",
            ],
            default=[
                "duckduckgo",
            ],
        )

        search_provider = [
            item.replace(" — planned", "")
            for item in search_provider
        ]
# --------------------------------------------------
# Chat Display
# --------------------------------------------------

for index, turn in enumerate(st.session_state.conversation_history):
    with st.chat_message("user"):
        st.write(turn.get("user_input", ""))

    with st.chat_message("assistant"):
    
        answer = turn.get("answer", "")
    
        st.write(answer)
    
        if answer:
            if st.button(
                "🔊 Listen",
                key=f"tts_history_{index}",
            ):
                audio = generate_speech(answer)
                st.audio(audio, format="audio/mp3")

# --------------------------------------------------
# Voice Input / Speech to Text
# --------------------------------------------------

st.subheader("Voice input")

audio_value = st.audio_input(
    "Record a voice message",
    sample_rate=16000,
    key="voice_audio_input",
)

voice_text = ""

if audio_value:
    st.audio(audio_value)

    if st.button("Transcribe voice", key="transcribe_voice_button"):
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav",
        ) as tmp:
            tmp.write(audio_value.getvalue())
            tmp_path = tmp.name

        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
            )

        voice_text = transcript.strip()

        st.session_state["voice_text"] = voice_text
        st.success("Voice transcribed.")
        st.write(voice_text)

# --------------------------------------------------
# Chat Input
# --------------------------------------------------

typed_text = st.chat_input("Message DeDe")

text = typed_text or st.session_state.get("voice_text", "")

if text:
    st.session_state["voice_text"] = ""

if text:
    engine = st.session_state.engine

    report = engine.analyze(
        text=text,
        enable_llm=enable_llm,
        search_provider=search_provider,
        search_profile=(
            None if search_profile == "custom"
            else search_profile
        ),
        search_mode=search_mode.lower(),
        llm_profile="custom",
        llm_providers=llm_providers,
        conversation_history=st.session_state.conversation_history,
    )

    # --------------------------------------------------
    # Real World Anchor Analysis
    # --------------------------------------------------

    anchor_engine = RealWorldAnchor()

    source_analysis = report.get(
        "source_analysis",
        {},
    )

    search_validation = report.get(
        "search_validation",
        {},
    )

    cognitive_comparison = report.get(
        "cognitive_comparison",
        {},
    )

    anchor_result = anchor_engine.analyze(
        text=text,
        source_analysis=source_analysis,
        search_validation=search_validation,
        cognitive_comparison=cognitive_comparison,
    )

    report["real_world_anchor"] = anchor_result

    st.session_state.conversation_history = report.get(
        "conversation_history",
        st.session_state.conversation_history,
    )

    user_response = report.get("user_response", {})

    with st.chat_message("user"):
        st.write(text)

    with st.chat_message("assistant"):

        final_answer = user_response.get(
            "final_answer",
            "No answer generated.",
        )

        st.write(final_answer)

        if st.button(
            "🔊 Listen",
            key=f"tts_current_{len(st.session_state.conversation_history)}",
        ):
            audio = generate_speech(final_answer)
            st.audio(audio, format="audio/mp3")

    workspace = report["workspace"]
    variables = workspace["variables"]
    agent_results = report["agent_results"]
    summary = report["summary"]
    committee = report["committee"]

    formulas = report["formulas"]
    core = formulas["core"]
    derived = formulas["derived"]

    # --------------------------------------------------
    # DeDe Cognitive Dashboard
    # --------------------------------------------------

    with st.expander("DeDe Cognitive Dashboard"):

        # --------------------------------------------------
        # Real World Anchor
        # --------------------------------------------------

        st.subheader("Ancrage au réel")

        st.write(anchor_result["label"])

        st.progress(anchor_result["score"])

        st.info(anchor_result["interpretation"])

        st.caption("Confiance épistémique")

        st.progress(
            anchor_result["epistemic_confidence"]
        )

        st.caption("Risque d'hallucination / suraffirmation")

        st.progress(
            anchor_result["hallucination_risk"]
        )

        st.write(
            "Action Governor :",
            anchor_result["governor_action"],
        )

        with st.expander("Détails de l'ancrage"):
            st.json(anchor_result["components"])

        # --------------------------------------------------
        # Search Engine
        # --------------------------------------------------
        
        search_result = report.get(
            "search_result",
            {},
        )
        
        st.subheader("Search Engine")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Provider",
                search_result.get(
                    "provider",
                    "none",
                ),
            )
        
        with col2:
            st.metric(
                "Status",
                search_result.get(
                    "status",
                    "disabled",
                ),
            )
        
        st.caption(
            search_result.get(
                "summary",
                "",
            )
        )
        
        with st.expander("Search Details"):
            st.json(search_result)

        # --------------------------------------------------
        # Universal Text Analysis
        # --------------------------------------------------

        st.subheader("Universal Text Analysis")

        user_text_analysis = report.get(
            "user_text_analysis",
            {},
        )

        web_text_analysis = report.get(
            "web_text_analysis",
            {},
        )

        final_response_analysis = report.get(
            "final_response_analysis",
            {},
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "User Analysis",
                user_text_analysis.get(
                    "status",
                    "N/A",
                ),
            )

        with col2:
            st.metric(
                "Web Items Analyzed",
                web_text_analysis.get(
                    "item_count",
                    0,
                ),
            )

        with col3:
            st.metric(
                "Final Response Analysis",
                final_response_analysis.get(
                    "status",
                    "N/A",
                ),
            )

        with st.expander("User Text Analysis"):
            st.json(user_text_analysis)

        with st.expander("Web Text Analysis"):
            st.json(web_text_analysis)

        with st.expander("Final Response Analysis"):
            st.json(final_response_analysis)

        # --------------------------------------------------
        # Cognitive Comparison
        # --------------------------------------------------

        st.subheader("Cognitive Comparison")

        cognitive_comparison = report.get(
            "cognitive_comparison",
            {},
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Comparison Status",
                cognitive_comparison.get(
                    "status",
                    "N/A",
                ),
            )

        with col2:
            st.metric(
                "Warnings",
                cognitive_comparison.get(
                    "warning_count",
                    0,
                ),
            )

        st.write(
            cognitive_comparison.get(
                "summary",
                "",
            )
        )

        warnings = cognitive_comparison.get(
            "warnings",
            [],
        )

        for warning in warnings:
            message = warning.get(
                "message",
                "",
            )

            severity = warning.get(
                "severity",
                "medium",
            )

            if severity == "high":
                st.error(message)
            else:
                st.warning(message)

        with st.expander(
            "Cognitive Comparison Details"
        ):
            st.json(cognitive_comparison)

        # --------------------------------------------------
        # Cognitive Source Analysis
        # --------------------------------------------------

        st.subheader("Cognitive Source Analysis")

        source_analysis = report.get(
            "source_analysis",
            {},
        )

        source_aggregate = source_analysis.get(
            "aggregate",
            {},
        )

        average_scores = source_aggregate.get(
            "average_scores",
            {},
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Sources",
                source_analysis.get(
                    "source_count",
                    0,
                ),
            )

        with col2:
            evidence_score = average_scores.get(
                "evidence_level"
            )

            st.metric(
                "Average Evidence",
                (
                    f"{evidence_score:.0%}"
                    if isinstance(
                        evidence_score,
                        (int, float),
                    )
                    else "N/A"
                ),
            )

        with col3:
            relevance_score = average_scores.get(
                "relevance"
            )

            st.metric(
                "Average Relevance",
                (
                    f"{relevance_score:.0%}"
                    if isinstance(
                        relevance_score,
                        (int, float),
                    )
                    else "N/A"
                ),
            )

        st.write(
            source_analysis.get(
                "overall_summary",
                "",
            )
        )

        st.write("Source Types")

        st.json(
            source_aggregate.get(
                "source_type_counts",
                {},
            )
        )

        with st.expander(
            "Cognitive Source Analysis Details"
        ):
            st.json(source_analysis)

        # --------------------------------------------------
        # Autobiographical Memory
        # --------------------------------------------------

        st.subheader("Autobiographical Memory")
        st.json(report.get("autobiography", {}))

        st.subheader("Autobiographical Reasoning")
        st.json(report.get("autobiographical_reasoning", {}))
        
        # --------------------------------------------------
        # Phase 2 Cognitive Variables
        # --------------------------------------------------
        
        st.subheader("Phase 2 Cognitive Variables")
    
        col1, col2, col3, col4 = st.columns(4)
    
        with col1:
            show_metric("Grounding", variables["grounding"])
    
        with col2:
            show_metric("Integration", variables["integration"])
    
        with col3:
            show_metric("Closure", variables["closure"])
    
        with col4:
            show_metric("Reduction", variables["reduction"])
    
            
        # --------------------------------------------------
        # Phase 2 Cognitive Summary
        # --------------------------------------------------
        
        st.subheader("Phase 2 Cognitive Summary")
    
        st.write(summary["diagnosis"])
    
        st.metric(
            "Cognitive Balance",
            pct(summary["cognitive_balance"]),
        )
    
        committee = report["committee"]
    
        formulas = report["formulas"]
        core = formulas["core"]
        derived = formulas["derived"]
        
        # --------------------------------------------------
        # DOXA Formula Metrics
        # --------------------------------------------------
        
        st.subheader("DOXA Formula Metrics")
    
        col1, col2, col3 = st.columns(3)
    
        with col1:
            show_metric("Support", core["support"])
            show_metric("Pressure", core["pressure"])
    
        with col2:
            show_metric("Mecroyance Pressure", core["mecroyance_pressure"])
            show_metric("Mecroyance Risk", core["mecroyance_risk"])
    
        with col3:
            show_metric("Revisability", core["revisability"])
            show_metric("Surconfidence", derived["surconfidence"])
            
        # --------------------------------------------------
        # Derived Cognitive Pressures
        # --------------------------------------------------
        
        st.subheader("Derived Cognitive Pressures")
    
        col1, col2 = st.columns(2)
    
        with col1:
            show_metric("Cognitive Closure", derived["cognitive_closure"])
    
        with col2:
            show_metric(
                "Forgotten Reduction",
                derived["forgotten_reduction_pressure"],
            )
    
        st.info(formulas["diagnosis"])
        
        # --------------------------------------------------
        # Semantic Graph
        # --------------------------------------------------
    
        semantic_graph = report.get("semantic_graph", {})

        # --------------------------------------------------
        # Universal Text Analysis
        # --------------------------------------------------
        
        st.subheader("Universal Text Analysis")
        
        st.write("USER")
        st.json(report.get("user_text_analysis", {}))
        
        st.write("WEB")
        st.json(report.get("web_text_analysis", {}))
        
        st.write("FINAL RESPONSE")
        st.json(report.get("final_response_analysis", {}))
        
        st.subheader("Semantic Graph")
    
        col1, col2, col3 = st.columns(3)
    
        with col1:
            st.metric("Nodes", semantic_graph.get("node_count", 0))
    
        with col2:
            st.metric("Edges", semantic_graph.get("edge_count", 0))
    
        with col3:
            st.metric(
                "Causal Paths",
                semantic_graph.get("causal_path_count", 0),
            )
    
        if semantic_graph.get("causal_paths"):
            st.caption("Detected cognitive paths")
    
            for path in semantic_graph["causal_paths"]:
                readable_path = " → ".join(
                    f'{step["source"]} / {step["relation"]} / {step["target"]}'
                    for step in path["path"]
                )
                st.write(f"- {readable_path}")
    
        with st.expander("Semantic Graph details"):
            st.json(semantic_graph)
        
        # --------------------------------------------------
        # Graph Queries
        # --------------------------------------------------
    
        graph_queries = report.get("graph_queries", {})
        
        st.subheader("Graph Queries")
    
        col1, col2 = st.columns(2)
    
        with col1:
            st.metric(
                "Central Nodes",
                len(graph_queries.get("central_nodes", [])),
            )
    
        with col2:
            key_paths = graph_queries.get("key_paths", {})
            available_paths = sum(
                1 for path in key_paths.values() if path
            )
            st.metric(
                "Available Key Paths",
                available_paths,
            )
    
        if graph_queries.get("central_nodes"):
            st.caption("Most connected cognitive nodes")
    
            for item in graph_queries["central_nodes"]:
                st.write(
                    f'- {item["node"]} — degree {item["degree"]}'
                )
        
        with st.expander("LLM Context Preview"):
            st.json(
                graph_queries.get(
                    "llm_context",
                    {},
                )
            )
        
        with st.expander("Graph Query details"):
            st.json(graph_queries)
        
        # --------------------------------------------------
        # Inference Pattern 
        # --------------------------------------------------
    
        inference_patterns = report.get("inference_patterns", {})
        
        st.subheader("Inference Patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Available Patterns",
                inference_patterns.get("available_pattern_count", 0),
            )
        
        with col2:
            st.metric(
                "Detected Patterns",
                inference_patterns.get("detected_pattern_count", 0),
            )
        
        st.write(
            inference_patterns.get(
                "summary",
                "",
            )
        )
        
        patterns = inference_patterns.get("patterns", [])
        
        if patterns:
            for pattern in patterns:
                confidence = pattern.get("confidence", 0)
        
                st.write(
                    f'- **{pattern.get("name", "unknown")}** '
                    f'[{pattern.get("type", "pattern")}] '
                    f'— confidence {round(confidence * 100)}%'
                )
        
                st.caption(
                    pattern.get(
                        "description",
                        "",
                    )
                )
        
        with st.expander("Inference Pattern details"):
            st.json(inference_patterns)
    
        # --------------------------------------------------
        # Cognitive State Compiler
        # --------------------------------------------------
    
        cognitive_state = report.get("cognitive_state", {})
        
        st.subheader("Cognitive State Compiler")
    
        col1, col2 = st.columns(2)
    
        with col1:
            st.metric(
                "Compiled Orientation",
                cognitive_state.get("orientation", "N/A"),
            )
    
        with col2:
            show_metric(
                "Compiled Confidence",
                cognitive_state.get("confidence"),
            )
    
        st.write(
            cognitive_state.get(
                "summary",
                "",
            )
        )
    
        with st.expander("Cognitive Focus"):
            st.json(
                cognitive_state.get(
                    "cognitive_focus",
                    [],
                )
            )
    
        with st.expander("Support"):
            st.json(
                cognitive_state.get(
                    "support",
                    [],
                )
            )
    
        with st.expander("Pressure"):
            st.json(
                cognitive_state.get(
                    "pressure",
                    [],
                )
            )
    
        with st.expander("Protective Mechanisms"):
            st.json(
                cognitive_state.get(
                    "protective_mechanisms",
                    [],
                )
            )
    
        with st.expander("Detected Dynamics"):
            st.json(
                cognitive_state.get(
                    "detected_dynamics",
                    [],
                )
            )
    
        with st.expander("Missing Dimensions"):
            st.json(
                cognitive_state.get(
                    "missing_dimensions",
                    [],
                )
            )
    
        with st.expander("Full Cognitive State"):
            st.json(cognitive_state)
    
        # --------------------------------------------------
        # Cognitive Reasoner
        # --------------------------------------------------
    
        cognitive_reasoning = report.get("cognitive_reasoning", {})
    
        st.subheader("Cognitive Reasoner")
    
        st.metric(
            "Reasoner Status",
            cognitive_reasoning.get("status", "N/A"),
        )
    
        nodes = cognitive_reasoning.get("nodes_considered", [])
    
        if nodes:
            st.caption("Nodes considered")
            st.write(", ".join(nodes))
    
        with st.expander("Hypotheses"):
            st.json(cognitive_reasoning.get("hypotheses", []))
    
        with st.expander("Contradictions"):
            st.json(cognitive_reasoning.get("contradictions", []))
    
        with st.expander("Explanations"):
            st.json(cognitive_reasoning.get("explanations", []))
    
        with st.expander("Missing Links"):
            st.json(cognitive_reasoning.get("missing_links", []))
    
        with st.expander("Predictions"):
            st.json(cognitive_reasoning.get("predictions", []))
    
        with st.expander("Counterfactuals"):
            st.json(cognitive_reasoning.get("counterfactuals", []))
    
        with st.expander("Inference Chains"):
            st.json(cognitive_reasoning.get("inference_chains", []))

        # --------------------------------------------------
        # Committee Reasoner
        # --------------------------------------------------

        committee_reasoning = report.get(
            "committee_reasoning",
            {},
        )

        st.subheader("Committee Reasoner")

        st.caption(
            "Transforms multiple LLM outputs into structured reasoning material "
            "before DeDe builds its final answer."
        )

        st.metric(
            "Reasoner Status",
            committee_reasoning.get("status", "N/A"),
        )

        st.write(
            committee_reasoning.get("summary", "")
        )

        with st.expander("Committee Reasoning Details"):
            st.json(committee_reasoning)
        
        # --------------------------------------------------
        # LLM Connector
        # --------------------------------------------------
    
        llm_package = report.get("llm_package", {})
        
        st.subheader("LLM Connector")
    
        st.metric(
            "LLM Package Status",
            llm_package.get("status", "N/A"),
        )
    
        st.write(llm_package.get("summary", ""))
    
        with st.expander("LLM System Prompt"):
            st.write(llm_package.get("system_prompt", ""))
    
        with st.expander("LLM Cognitive Context"):
            st.text(llm_package.get("cognitive_context", ""))
    
        with st.expander("Full LLM Prompt Package"):
            st.json(llm_package)
    
        # --------------------------------------------------
        # LLM Bridge
        # --------------------------------------------------
    
        llm_bridge_response = report.get("llm_bridge_response", {})
    
        st.subheader("LLM Bridge")
    
        col1, col2 = st.columns(2)
    
        with col1:
            st.metric(
                "Bridge Status",
                llm_bridge_response.get("status", "N/A"),
            )
    
        with col2:
            st.metric(
                "Provider",
                llm_bridge_response.get("provider", "N/A"),
            )
    
            st.metric(
                "JSON Valid",
                str(llm_bridge_response.get("json_valid", False)),
            )
    
        st.write(
            llm_bridge_response.get(
                "summary",
                "",
            )
        )
    
        if llm_bridge_response.get("error"):
            st.error(
                llm_bridge_response["error"]
            )
    
        if llm_bridge_response.get("response"):
            with st.expander("LLM Raw Response"):
                st.write(
                    llm_bridge_response["response"]
                )
    
        with st.expander("Full LLM Bridge Response"):
            st.json(llm_bridge_response)

        # --------------------------------------------------
        # LLM Engine
        # --------------------------------------------------
        
        llm_engine_response = report.get(
            "llm_engine_response",
            {},
        )
        
        st.subheader("Reasoning Models")
        
        st.caption(
            "Reasoning models are interchangeable LLM components used by DeDe "
            "after memory, search, semantic and cognitive preparation."
        )
        
        llm_committee = llm_engine_response.get(
            "committee",
            {},
        )
        
        if llm_committee:
        
            st.metric(
                "Committee Providers",
                llm_committee.get(
                    "provider_count",
                    0,
                ),
            )
        
            st.caption(
                llm_committee.get(
                    "summary",
                    "",
                )
            )
        
        st.metric(
            "Engine Status",
            llm_engine_response.get("status", "N/A"),
        )
        
        st.write(
            llm_engine_response.get("summary", "")
        )
        
        with st.expander("Reasoning Model Details"):
            st.json(llm_engine_response)
    
        # --------------------------------------------------
        # Cognitive Feedback
        # --------------------------------------------------
    
        cognitive_feedback = report.get("cognitive_feedback", {})
    
        st.subheader("Cognitive Feedback")
    
        col1, col2 = st.columns(2)
    
        with col1:
            st.metric(
                "Feedback Status",
                cognitive_feedback.get("status", "N/A"),
            )
    
        with col2:
            show_metric(
                "Feedback Confidence",
                cognitive_feedback.get("confidence"),
            )
    
        st.write(
            cognitive_feedback.get(
                "summary",
                "",
            )
        )
    
        with st.expander("New Concepts"):
            st.json(
                cognitive_feedback.get(
                    "new_concepts",
                    [],
                )
            )
    
        with st.expander("New Relations"):
            st.json(
                cognitive_feedback.get(
                    "new_relations",
                    [],
                )
            )
    
        with st.expander("New Hypotheses"):
            st.json(
                cognitive_feedback.get(
                    "new_hypotheses",
                    [],
                )
            )
    
        with st.expander("New Questions"):
            st.json(
                cognitive_feedback.get(
                    "new_questions",
                    [],
                )
            )
    
        with st.expander("New Missing Dimensions"):
            st.json(
                cognitive_feedback.get(
                    "new_missing_dimensions",
                    [],
                )
            )
    
        with st.expander("New Counterfactuals"):
            st.json(
                cognitive_feedback.get(
                    "new_counterfactuals",
                    [],
                )
            )
    
        with st.expander("Full Cognitive Feedback"):
            st.json(cognitive_feedback)
    
        # --------------------------------------------------
        # Dialogue Decision
        # --------------------------------------------------
        
        dialogue_decision = report.get("dialogue_decision", {})
    
        st.subheader("Dialogue Strategy")
        
        st.metric(
            "Dialogue Mode",
            dialogue_decision.get("mode", "N/A"),
        )
        
        st.write(
            dialogue_decision.get("summary", "")
        )
        
        with st.expander("Dialogue Decision"):
            st.json(dialogue_decision)
    
        # --------------------------------------------------
        # Conversation Reasoning
        # --------------------------------------------------
    
        conversation_reasoning = report.get("conversation_reasoning", {})
    
        st.subheader("Conversation Reasoning")
    
        col1, col2 = st.columns(2)
    
        with col1:
            st.metric(
                "Next Move",
                conversation_reasoning.get("move", "N/A"),
            )
    
        with col2:
            st.metric(
                "Follow-up",
                str(conversation_reasoning.get("is_follow_up", False)),
            )
    
        st.write(
            conversation_reasoning.get("summary", "")
        )
    
        if conversation_reasoning.get("next_prompt"):
            st.info(
                conversation_reasoning["next_prompt"]
            )
    
        with st.expander("Conversation Reasoning details"):
            st.json(conversation_reasoning)

        # --------------------------------------------------
        # Dialogue Profile
        # --------------------------------------------------

        dialogue_profile = report.get("dialogue_profile", {})

        st.subheader("Dialogue Profile")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Language",
                dialogue_profile.get("language", "N/A"),
            )

        with col2:
            st.metric(
                "Tone",
                dialogue_profile.get("tone", "N/A"),
            )

        with col3:
            st.metric(
                "Verbosity",
                dialogue_profile.get("verbosity", "N/A"),
            )

        st.write(
            dialogue_profile.get("summary", "")
        )

        with st.expander("Dialogue Profile details"):
            st.json(dialogue_profile)
    
        # --------------------------------------------------
        # Agent Interpretations
        # --------------------------------------------------
        
        st.subheader("Agent Interpretations")
    
        for name, result in agent_results.items():
            st.markdown(f"### {name}")
    
            st.info(result.get("summary", ""))
    
            if result.get("committee_reply"):
                st.write(result["committee_reply"])
    
            with st.expander(f"{name} details"):
                st.json(result)
    
        # --------------------------------------------------
        # Cognitive Committee
        # --------------------------------------------------
        
        st.subheader("Cognitive Committee")
    
        col1, col2 = st.columns(2)
    
        with col1:
            show_metric(
                "Committee Confidence",
                committee["confidence"],
            )
    
        with col2:
            st.metric(
                "Dominant Orientation",
                committee["dominant_orientation"],
            )
    
        st.info(committee["diagnosis"])
    
        # --------------------------------------------------
        # Committee Concerns
        # --------------------------------------------------
    
        if committee["concerns"]:
            st.subheader("Committee Concerns")
    
            for concern in committee["concerns"]:
                st.warning(concern)
    
        # --------------------------------------------------
        # Committee Recommendations
        # --------------------------------------------------
        
        st.subheader("Committee Recommendations")
    
        for recommendation in committee["recommendations"]:
            st.write(f"- {recommendation}")
                
        # --------------------------------------------------
        # Full Report
        # --------------------------------------------------
        
        st.subheader("Complete Cognitive Report")
        
        st.json(report)
