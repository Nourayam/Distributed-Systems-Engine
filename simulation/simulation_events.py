from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Dict, Optional


class EventType(Enum):
    #Types of events that can occur in the simulation.
    SEND = auto()      # Message sending event
    RECEIVE = auto()   # Message receiving event
    TIMEOUT = auto()   # Timer expiration event
    CRASH = auto()     # Node failure event
    RECOVER = auto()   # Node recovery event


@dataclass(order=True)
class Event:
    #Represents a simulation event to be processed at a specific time.
    
    #Events are ordered by their timestamp to enable priority queue processing.
    #The data field can contain any relevant payload for the event.
    
    timestamp: int          # When the event should occur (in simulation time)
    event_type: EventType   # What type of event this is
    data: Optional[Dict[str, Any]] = None  # Optional payload data
    
    def __post_init__(self):
        #Initialise data as empty dict if not provided
        if self.data is None:
            self.data = {}