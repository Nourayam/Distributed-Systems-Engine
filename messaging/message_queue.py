from __future__ import annotations

import random
import logging
from typing import Dict, Any, TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from config import Config
    from simulation.simulation import Simulation

from simulation.simulation_events import Event, EventType

logger = logging.getLogger(__name__)


class MessageData(TypedDict):
    src: str
    dst: str 
    type: str
    payload: Dict[str, Any]


class MessageQueue:
    """Manages message delivery with realistic network behavior."""
    
    def __init__(self, config: 'Config', simulation: 'Simulation') -> None:
        self.config = config
        self.simulation = simulation
        self.logger = logging.getLogger(f"{__name__}.MessageQueue")

    def send(
        self,
        src: str,
        dst: str,
        message_type: str,
        payload: Dict[str, Any],
        current_time: float
    ) -> None:
        """Send a message with potential network delays and failures."""
        # Validate inputs
        if not isinstance(current_time, (int, float)):
            raise ValueError(f"current_time must be numeric, got {type(current_time)}")
        
        # Create message structure
        data: MessageData = {
            'src': src,
            'dst': dst,
            'type': message_type,
            'payload': payload
        }

        # Log send event
        self._log_send_event(current_time, data)
        
        # Randomly drop message based on config
        if self._should_drop_message():
            self._log_drop_event(current_time, data)
            return
        
        # Schedule delivery with random latency
        self._schedule_delivery(current_time, data)

    def _should_drop_message(self) -> bool:
        """Determine if message should be dropped based on network conditions."""
        return random.random() < self.config.drop_rate

    def _log_send_event(self, timestamp: float, data: MessageData) -> None:
        """Log message send event."""
        self.logger.debug(f"Sending {data['type']} from {data['src']} to {data['dst']}")
        send_event = Event(
            timestamp=timestamp,
            event_type=EventType.MESSAGE_SEND,
            data=dict(data)  # Convert TypedDict to regular dict
        )
        self.simulation.schedule_event(send_event)

    def _log_drop_event(self, timestamp: float, data: MessageData) -> None:
        """Log message drop event."""
        self.logger.warning(f"Dropping {data['type']} from {data['src']} to {data['dst']}")
        drop_event = Event(
            timestamp=timestamp,
            event_type=EventType.MESSAGE_DROPPED,
            data=dict(data)  # Convert TypedDict to regular dict
        )
        self.simulation.schedule_event(drop_event)

    def _schedule_delivery(self, send_time: float, data: MessageData) -> None:
        """Schedule message delivery with realistic network latency."""
        # Validate send_time
        if send_time < 0:
            raise ValueError(f"send_time cannot be negative: {send_time}")
        
        latency = random.uniform(self.config.min_latency, self.config.max_latency)
        delivery_time = send_time + latency
        
        delivery_event = Event(
            timestamp=delivery_time,
            event_type=EventType.MESSAGE_RECEIVED,
            data=dict(data)  # Convert TypedDict to regular dict
        )
        self.simulation.schedule_event(delivery_event)
        
        self.logger.debug(f"Scheduled delivery of {data['type']} at {delivery_time:.3f}")