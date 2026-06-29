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

if st.button("Analyze"):
    engine = DoxaEnginePhase2()
    report = engine.analyze(text)

    workspace = report["workspace"]
    variables = workspace["variables"]
    agent_results = report["agent_results"]
    summary = report["summary"]

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

    st.subheader("Phase 2 Cognitive Summary")

    st.write(summary["diagnosis"])

    st.metric(
        "Cognitive Balance",
        pct(summary["cognitive_balance"]),
    )

    st.subheader("Agent Interpretations")

    for name, result in agent_results.items():
        st.markdown(f"### {name}")

        st.info(result.get("summary", ""))

        if result.get("committee_reply"):
            st.write(result["committee_reply"])

        with st.expander(f"{name} details"):
            st.json(result)

    with st.expander("Full Phase 2 Report"):
        st.json(report)
