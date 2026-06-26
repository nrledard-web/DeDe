from interfaces.cognitive_agent import CognitiveAgent


class KnowledgeAgent(CognitiveAgent):

    def __init__(self):

        self.knowledge_base = {

            "what is gravity":
                "Gravity is the attraction between masses.",

            "who discovered relativity":
                "Albert Einstein developed General Relativity.",

            "what is cognition":
                "Cognition refers to processes involved in acquiring and using knowledge.",

            "what is mecroyance":
                (
                    "Mecroyance is a cognitive condition in which certainty "
                    "stabilizes faster than understanding."
                ),

            "what is doxa":
                (
                    "Doxa refers to stabilized certainty that can become "
                    "resistant to revision."
                ),

        }

    def can_handle(self, state):
        return True

    def analyze(self, state):

        question = state.user_input.lower().strip()

        answer = self.knowledge_base.get(
            question,
            "Knowledge not found in local knowledge base."
        )

        return {
            "agent": "knowledge",
            "question": question,
            "answer": answer,
            "source": "local_knowledge_base",
        }

    def update_state(self, state, result):

        state.analyses["knowledge"] = result
        state.metadata["knowledge"] = result

        return state
