import streamlit as st

from engine.doxa_engine_phase2 import DoxaEnginePhase2
from pathlib import Path

def pct(value):
    if value is None:
        return "N/A"
    return f"{round(value * 100)}%"


def show_metric(label, value):
    st.metric(label, pct(value))


st.set_page_config(
    page_title="DeDe",
    page_icon="🧠",
    layout="wide",
)

BANNER_PATH = Path("assets/Banner01.png")

if BANNER_PATH.exists():
    st.image(str(BANNER_PATH), use_container_width=True)
else:
    st.warning("Banner01.png not found in assets/")

st.title("DeDe — Cognitive Daimon")

st.caption("Phase 3 — Cognitive Mechanics")
st.success("DeDe Phase 3 prototype is running.")

st.caption(
    "Current status: CognitiveWorkspace, estimator layer, "
    "agent interpretation and shared cognitive mechanics."
)

# --------------------------------------------------
# Owner Identity
# --------------------------------------------------

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
# LLM Toggle
# --------------------------------------------------

enable_llm = st.toggle(
    "Enable external LLM call",
    value=False,
)

if st.button("Reset conversation"):
    st.session_state.conversation_history = []
    st.success("Conversation reset.")

# --------------------------------------------------
# Chat Display
# --------------------------------------------------

for turn in st.session_state.conversation_history:
    with st.chat_message("user"):
        st.write(turn.get("user_input", ""))

    with st.chat_message("assistant"):
        st.write(turn.get("answer", ""))

        if turn.get("follow_up_question"):
            st.info(turn["follow_up_question"])

# --------------------------------------------------
# Chat Input
# --------------------------------------------------

text = st.chat_input("Message DeDe")

if text:
    engine = st.session_state.engine

    report = engine.analyze(
        text=text,
        enable_llm=enable_llm,
        conversation_history=st.session_state.conversation_history,
    )

    st.session_state.conversation_history = report.get(
        "conversation_history",
        st.session_state.conversation_history,
    )

    user_response = report.get("user_response", {})

    with st.chat_message("user"):
        st.write(text)

    with st.chat_message("assistant"):
        st.write(
            user_response.get(
                "final_answer",
                "No answer generated.",
            )
        )

        follow_up = user_response.get("follow_up_question")

        if follow_up:
            st.info(follow_up)

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
        
        st.subheader("Autobiographical Memory")
        st.json(report.get("autobiography", {}))

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
