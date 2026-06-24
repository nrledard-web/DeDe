"""
DeDe - Daimon Orchestrator

Central cognitive coordinator.
Receives user input, calls the cognitive agents,
uses memory, and produces a unified response.
"""


class DaimonOrchestrator:
    def __init__(self, memory_agent=None, agents=None):
        self.memory_agent = memory_agent
        self.agents = agents or {}

    def receive(self, user_input: str, context: dict | None = None) -> dict:
        """
        Main entry point for DeDe.
        """

        context = context or {}

        cognitive_state = {
            "user_input": user_input,
            "context": context,
            "memory": None,
            "analyses": {},
            "final_response": None,
        }

        cognitive_state["memory"] = self._load_relevant_memory(user_input)

        cognitive_state["analyses"] = self._run_agents(
            user_input=user_input,
            context=context,
            memory=cognitive_state["memory"],
        )

        cognitive_state["final_response"] = self._synthesize_response(
            user_input=user_input,
            analyses=cognitive_state["analyses"],
            memory=cognitive_state["memory"],
        )

        return cognitive_state

    def _load_relevant_memory(self, user_input: str):
        """
        Load relevant long-term memory.
        """

        if self.memory_agent is None:
            return {}

        return self.memory_agent.retrieve(user_input)

    def _run_agents(self, user_input: str, context: dict, memory: dict) -> dict:
        """
        Run all registered cognitive agents.
        """

        results = {}

        for name, agent in self.agents.items():
            if hasattr(agent, "analyze"):
                results[name] = agent.analyze(
                    text=user_input,
                    context=context,
                    memory=memory,
                )

        return results

    def _synthesize_response(
        self,
        user_input: str,
        analyses: dict,
        memory: dict,
    ) -> str:
        """
        First simple synthesis layer.
        Later this will be replaced by a real LLM call.
        """

        return (
            "DeDe received the input and coordinated the cognitive agents. "
            "Full synthesis engine not implemented yet."
        )
