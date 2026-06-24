import streamlit as st
from engine.doxa_engine import DoxaEngine

st.set_page_config(page_title="DeDe", page_icon="🧠", layout="wide")

st.title("DeDe — Cognitive Daimon")
st.caption("First symbolic cognitive analysis demo")

text = st.text_area(
    "Text to analyze",
    value="This theory is obviously true and cannot be questioned.",
    height=160,
)

if st.button("Analyze"):
    engine = DoxaEngine()
    report = engine.analyze(text)

    st.subheader("Summary")
    st.write(report["summary"])

    st.subheader("Agent scores")
    st.json(report["scores"])

    st.subheader("Detector results")
    st.json(report["detectors"])

    st.subheader("Active agents")
    st.write(report["active_agents"])
