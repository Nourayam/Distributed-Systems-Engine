from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional


class EventType(Enum):
    """Types of events that can occur in the simulation"""
    MESSAGE_SEND = auto()        # Message sending event
    MESSAGE_RECEIVED = auto()    # Message receiving event  
    MESSAGE_DROPPED = auto()     # Message dropped event
    TIMEOUT = auto()             # Timer expiration event
    NODE_CRASH = auto()          # Node failure event  
    NODE_RECOVER = auto()        # Node recovery event
    ELECTION_TIMEOUT = auto()    # Election timeout event
    HEARTBEAT_TIMEOUT = auto()   # Heartbeat timeout event


@dataclass(order=True)
class Event:
    """Represents a simulation event with timestamp and payload."""
    event_type: EventType
    timestamp: float
    data: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize data as empty dict if not provided"""
        if self.data is None:
            self.data = {}
    
    def __str__(self) -> str:
        return f"Event({self.event_type.name} at {self.timestamp:.3f})"