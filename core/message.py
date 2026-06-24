"""
DeDe - Cognitive Message

Defines the standard message structure used for communication
between DeDe's cognitive agents and core components.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class CognitiveMessage:
    """
    Standard communication unit inside DeDe's cognitive architecture.
    """

    sender: str
    receiver: str
    message_type: str
    payload: Any

    confidence: float = 1.0
    priority: int = 0
    metadata: dict = field(default_factory=dict)

    message_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        """
        Convert the cognitive message into a serializable dictionary.
        """

        return {
            "message_id": self.message_id,
            "created_at": self.created_at,
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type,
            "payload": self.payload,
            "confidence": self.confidence,
            "priority": self.priority,
            "metadata": self.metadata,
        }
