from dataclasses import dataclass, field
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
    timestamp: float
    # Use field(compare=False) to exclude from comparison
    event_type: EventType = field(compare=False)
    data: Dict[str, Any] = field(default_factory=dict, compare=False)
    
    def __str__(self) -> str:
        return f"Event({self.event_type.name} at {self.timestamp:.3f})"