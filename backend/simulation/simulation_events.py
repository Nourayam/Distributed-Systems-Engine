from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional


class EventType(Enum):
    MESSAGE_SEND = auto()        # Message sending event
    MESSAGE_RECEIVED = auto()    # Message receiving event  
    MESSAGE_DROPPED = auto()     # Message dropped event
    TIMEOUT = auto()             # Timer expiration event
    NODE_CRASH = auto()          # Node failure event  
    NODE_RECOVER = auto()        # Node recovery event
    ELECTION_TIMEOUT = auto()    # Election timeout event
    HEARTBEAT_TIMEOUT = auto()   # Heartbeat timeout event


@dataclass
class Event:
    # reps a simu event with timestamp and payload
    timestamp: float
    event_type: EventType
    data: Dict[str, Any] = None
    _sequence_id: int = 0  # For tie-breaking when timestamps are equal

    def __post_init__(self):
        #data as empty dict if not provided
        if self.data is None:
            self.data = {}
    
    def __lt__(self, other: 'Event') -> bool:
        #compares events by timestamp first, then by sequence ID for tie-breaking
        if not isinstance(other, Event):
            return NotImplemented
        if self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp
        # Use sequence ID for tie-breaking when timestamps are equal
        return self._sequence_id < other._sequence_id
    
    def __le__(self, other: 'Event') -> bool:
        if not isinstance(other, Event):
            return NotImplemented
        return self < other or self == other
    
    def __gt__(self, other: 'Event') -> bool:
        if not isinstance(other, Event):
            return NotImplemented
        return not self <= other
    
    def __ge__(self, other: 'Event') -> bool:
        if not isinstance(other, Event):
            return NotImplemented
        return not self < other
    
    def __eq__(self, other: 'Event') -> bool:
        #equality comparison based on timestamp and sequence ID
        if not isinstance(other, Event):
            return NotImplemented
        return (self.timestamp == other.timestamp and 
                self._sequence_id == other._sequence_id)
    
    def __hash__(self) -> int:
        return hash((self.timestamp, self._sequence_id))
    
    def __str__(self) -> str:
        return f"Event({self.event_type.name} at {self.timestamp:.3f})"