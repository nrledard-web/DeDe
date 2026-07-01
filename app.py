import streamlit as st

from engine.doxa_engine_phase2 import DoxaEnginePhase2


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

st.title("DeDe — Cognitive Daimon")
st.caption("Phase 2 — Cognitive Mechanics")

st.success("DeDe Phase 2 prototype is running.")
st.caption(
    "Current status: CognitiveWorkspace, estimator layer, "
    "agent interpretation and shared cognitive mechanics."
)

text = st.text_area(
    "Text to analyze",
    value=(
        "The climate debate is completely settled. Anyone who disagrees is "
        "simply ignorant. There is no need to examine alternative hypotheses "
        "because science has already proven everything with absolute certainty."
    ),
    height=180,
)
enable_llm = st.toggle(
    "Enable external LLM call",
    value=False,
)

if st.button("Analyze"):
    engine = DoxaEnginePhase2()
    report = engine.analyze(
        text,
        enable_llm=enable_llm,
    )

    workspace = report["workspace"]
    variables = workspace["variables"]
    agent_results = report["agent_results"]
    summary = report["summary"]
    
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
    # Full Phase 2 Report
    # --------------------------------------------------

    with st.expander("Full Phase 2 Report"):
        st.json(report)
