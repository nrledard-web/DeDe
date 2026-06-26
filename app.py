import streamlit as st

from engine.doxa_engine import DoxaEngine
from user_model.user_cognitive_model import UserCognitiveModel
from memory.cognitive_comparator import CognitiveComparator


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

st.success("DeDe Alpha prototype is running.")
st.caption(
    "Current status: symbolic cognitive analysis, cognitive vector, "
    "core formulas, detector pipeline and recalibration questions."
)

if "user_model" not in st.session_state:
    st.session_state.user_model = UserCognitiveModel()

if "cognitive_comparator" not in st.session_state:
    st.session_state.cognitive_comparator = CognitiveComparator()

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

    st.session_state.user_model.update(
        detectors["cognitive_vector"]
    )

    user_profile = st.session_state.user_model.profile()

    comparison = st.session_state.cognitive_comparator.compare(
        detectors["cognitive_vector"],
        user_profile,
    )

    knowledge = report["analyses"].get("knowledge")

    if knowledge:
        st.subheader("Knowledge Response")
        st.success(knowledge["answer"])

    if report.get("response_analysis"):

        st.subheader("Knowledge Response Cognitive Analysis")

        response_vector = report["response_analysis"]["cognitive_vector"]

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            show_metric("Response G", response_vector["gnosis"])

        with col2:
            show_metric("Response N", response_vector["nous"])

        with col3:
            show_metric("Response D", response_vector["doxa"])

        with col4:
            show_metric("Response R", response_vector["reduction"])

        with col5:
            show_metric("Response V", response_vector["revisability"])

        interpretation = report.get("response_interpretation")

        if interpretation:
            st.info(interpretation["diagnosis"])

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

    st.subheader("Cognitive Vector")

    vector = detectors["cognitive_vector"]

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        show_metric("G", vector["gnosis"])
    with col2:
        show_metric("N", vector["nous"])
    with col3:
        show_metric("D", vector["doxa"])
    with col4:
        show_metric("R", vector["reduction"])
    with col5:
        show_metric("V", vector["revisability"])

    st.subheader("Core Cognitive Metrics")

    metrics = detectors["metrics"]
    core = metrics["core"]
    derived = metrics["derived"]

    col1, col2, col3 = st.columns(3)

    with col1:
        show_metric("Grounding", core["grounding"])
        show_metric("Closure Pressure", core["closure_pressure"])

    with col2:
        show_metric("Mecroyance Pressure", core["mecroyance_pressure"])
        show_metric("Cognitive Balance", core["cognitive_balance"])

    with col3:
        show_metric("Surconfidence", derived["surconfidence"])
        show_metric(
            "Forgotten Reduction",
            derived["forgotten_reduction_pressure"],
        )

    st.info(metrics["diagnosis"])

    st.subheader("Formula Variants")

    formulas = detectors["formulas"]
    mecroyance_variants = formulas["mecroyance_variants"]
    pressure_variants = formulas["pressure_variants"]
    balance_variants = formulas["balance_variants"]

    col1, col2, col3 = st.columns(3)

    with col1:
        show_metric("M0 Base", mecroyance_variants["M0_base"])
        show_metric("M1 Revisable", mecroyance_variants["M1_revisable"])

    with col2:
        show_metric(
            "M2 Reduction-aware",
            mecroyance_variants["M2_reduction_aware"],
        )
        show_metric("Cognitive Balance", balance_variants["cognitive_balance"])

    with col3:
        show_metric("Cognitive Closure", pressure_variants["cognitive_closure"])
        show_metric(
            "Forgotten Reduction",
            pressure_variants["forgotten_reduction"],
        )

    st.subheader("User Cognitive Profile")

    st.write(f"Analyses in this session: {user_profile['analysis_count']}")

    average_vector = user_profile["average_vector"]

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        show_metric("Avg G", average_vector["gnosis"])
    with col2:
        show_metric("Avg N", average_vector["nous"])
    with col3:
        show_metric("Avg D", average_vector["doxa"])
    with col4:
        show_metric("Avg R", average_vector["reduction"])
    with col5:
        show_metric("Avg V", average_vector["revisability"])

    st.subheader("Compared With Your Session Profile")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("G Δ", pct(comparison["gnosis"]["delta"]), comparison["gnosis"]["trend"])
    with col2:
        st.metric("N Δ", pct(comparison["nous"]["delta"]), comparison["nous"]["trend"])
    with col3:
        st.metric("D Δ", pct(comparison["doxa"]["delta"]), comparison["doxa"]["trend"])
    with col4:
        st.metric("R Δ", pct(comparison["reduction"]["delta"]), comparison["reduction"]["trend"])
    with col5:
        st.metric("V Δ", pct(comparison["revisability"]["delta"]), comparison["revisability"]["trend"])

    st.subheader("Cognitive Questions")
    for question in report.get("questions", []):
        st.info(question)

    st.subheader("Summary")
    st.write(report["summary"])

    with st.expander("Full detector report"):
        st.json(detectors)

    with st.expander("Agent analyses"):
        st.json(report["analyses"])
