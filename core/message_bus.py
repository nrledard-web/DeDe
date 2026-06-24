"""
DeDe - Message Bus

Central communication hub for all cognitive agents.

Every cognitive agent exchanges information exclusively
through the MessageBus, ensuring loose coupling and
scalable multi-agent communication.
"""

from collections import defaultdict
from typing import Dict, List

from .message import CognitiveMessage


class MessageBus:
    """
    Central communication system for DeDe.
    """

    def __init__(self):
        self._messages: Dict[str, List[CognitiveMessage]] = defaultdict(list)

    def send(self, message: CognitiveMessage) -> None:
        """
        Deliver a message to its receiver.
        """
        self._messages[message.receiver].append(message)

    def receive(self, receiver: str) -> List[CognitiveMessage]:
        """
        Retrieve all pending messages for a receiver.
        """
        messages = self._messages[receiver]
        self._messages[receiver] = []
        return messages

    def pending(self, receiver: str) -> int:
        """
        Return the number of waiting messages.
        """
        return len(self._messages[receiver])

    def clear(self) -> None:
        """
        Remove every pending message.
        """
        self._messages.clear()

    def statistics(self) -> dict:
        """
        Return basic MessageBus statistics.
        """
        return {
            receiver: len(messages)
            for receiver, messages in self._messages.items()
        }
