import streamlit as st

from engine.doxa_engine import DoxaEngine


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
st.caption("First symbolic cognitive analysis prototype")

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
    engine = DoxaEngine()
    report = engine.analyze(text)

    detectors = report["detectors"]
    scores = detectors["mecroyance"]["scores"]

    st.subheader("Cognitive Scores")

    col1, col2, col3 = st.columns(3)
    with col1:
        show_metric("Gnosis", scores["gnosis"])
        show_metric("Nous", scores["nous"])
    with col2:
        show_metric("Doxa", scores["doxa"])
        show_metric("Reduction", scores["reduction"])
    with col3:
        show_metric("Revisability", scores["revisability"])
        show_metric("Mecroyance Risk", scores["mecroyance_risk"])

    st.subheader("Cognitive Balance")
    balance = detectors["balance"]
    st.write(balance["diagnosis"])
    st.progress(min(max(scores["mecroyance_risk"], 0.0), 1.0))

    st.subheader("Main Signals")

    if detectors["reduction"]["forgotten_reduction"]:
        st.warning("Possible forgotten reduction detected.")

    if scores["cognitive_closure"] > 0.25:
        st.warning("Cognitive closure pressure detected.")

    if scores["overconfidence"] > 0.25:
        st.warning("Unsupported certainty detected.")

    st.subheader("Text Statistics")

    stats = detectors.get("processed_text", {})

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Words", stats.get("word_count", "N/A"))
        st.metric("Sentences", stats.get("sentence_count", "N/A"))

    with col2:
        st.metric("Paragraphs", stats.get("paragraph_count", "N/A"))
        st.metric("Unique words", stats.get("unique_word_count", "N/A"))

    with col3:
        lexical_diversity = stats.get("lexical_diversity")

        if lexical_diversity is None:
            st.metric("Lexical diversity", "N/A")
        else:
            st.metric(
                "Lexical diversity",
                f"{round(lexical_diversity * 100)}%",
            )

    st.subheader("Cognitive Questions")
    for question in report.get("questions", []):
        st.info(question)
        
    st.subheader("Summary")
    st.write(report["summary"])

    with st.expander("Full detector report"):
        st.json(detectors)

    with st.expander("Agent analyses"):
        st.json(report["analyses"])
        
