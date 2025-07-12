from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Optional


class MessageType(Enum):
    HEARTBEAT = auto()
    VOTE_REQUEST = auto()
    VOTE_RESPONSE = auto()
    APPEND_ENTRIES = auto()
    APPEND_ENTRIES_RESPONSE = auto()
    CLIENT_REQUEST = auto()


@dataclass
class Message:    
    msg_type: MessageType
    sender: str
    receiver: str
    timestamp: datetime = None
    data: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        #converts the message to dictionary for serialisation
        return {
            'type': self.msg_type.name,
            'sender': self.sender,
            'receiver': self.receiver,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        return cls(
            msg_type=MessageType[data['type']],
            sender=data['sender'],
            receiver=data['receiver'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            data=data.get('data')
        )

    def __str__(self) -> str:
        return (f"{self.msg_type.name} (from {self.sender} to {self.receiver} "
                f"at {self.timestamp})")