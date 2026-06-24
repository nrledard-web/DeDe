"""
DeDe - First Cognitive Demo

Runs a symbolic cognitive cycle through DeDe's first-generation agents.
"""

from agents.gnosis_agent import GnosisAgent
from agents.nous_agent import NousAgent
from agents.doxa_agent import DoxaAgent
from agents.reduction_agent import ReductionAgent
from agents.nouscope_agent import NOUSCOPEAgent
from agents.cognitive_therapy_agent import CognitiveTherapyAgent

from core.cognitive_state import CognitiveState


def run_demo(user_input: str) -> CognitiveState:
    state = CognitiveState(user_input=user_input)

    agents = [
        GnosisAgent(),
        NousAgent(),
        DoxaAgent(),
        ReductionAgent(),
        NOUSCOPEAgent(),
        CognitiveTherapyAgent(),
    ]

    for agent in agents:
        if agent.can_handle(state):
            result = agent.analyze(state)
            state = agent.update_state(state, result)

    state.final_response = synthesize_response(state)

    return state


def synthesize_response(state: CognitiveState) -> str:
    return (
        "DeDe completed a first symbolic cognitive analysis. "
        f"G={state.gnosis_level}, "
        f"N={state.nous_level}, "
        f"D={state.doxa_level}, "
        f"R={state.reduction_level}, "
        f"RV={state.revisability_level}."
    )


if __name__ == "__main__":
    sample = "This theory is obviously true and cannot be questioned."

    state = run_demo(sample)

    print("=== DeDe Cognitive Demo ===")
    print()
    print("Input:")
    print(state.user_input)
    print()
    print("Active agents:")
    print(state.active_agents)
    print()
    print("Analyses:")
    for agent_name, analysis in state.analyses.items():
        print(f"\n[{agent_name.upper()}]")
        for key, value in analysis.items():
            print(f"{key}: {value}")
    print()
    print("Final response:")
    print(state.final_response)
