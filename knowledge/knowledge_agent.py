from interfaces.cognitive_agent import CognitiveAgent


class KnowledgeAgent(CognitiveAgent):
    """
    First knowledge agent.

    Currently returns a placeholder answer.

    Later it will query:
    - local documents
    - memory
    - LLM
    - web search
    """

    def can_handle(self, state):
        return True

    def analyze(self, state):
        return {
            "agent": "knowledge",
            "answer": (
                "Knowledge generation is not yet connected. "
                "This is the first placeholder."
            ),
        }

    def update_state(self, state, result):
        state.analyses["knowledge"] = result
        state.metadata["knowledge"] = result
        return state
