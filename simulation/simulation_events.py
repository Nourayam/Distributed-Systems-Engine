from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional


class EventType(Enum):
    #Types of events that can occur in the simulation
    MESSAGE_SEND = auto()    # Message sending event
    MESSAGE_DELIVER = auto() # Message receiving event
    TIMEOUT = auto()         # Timer expiration event
    NODE_CRASH = auto()      # Node failure event  
    NODE_RECOVER = auto()    # Node recovery event


@dataclass(order=True)
class Event:
    #Represents a simulation event with timestamp and payload.
    timestamp: float
    event_type: EventType
    data: Dict[str, Any] = None

    def __post_init__(self):
        #Initialise data as empty dict if not provided
        if self.data is None:
            self.data = {}