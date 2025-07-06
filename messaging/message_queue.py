from __future__ import annotations

import random
from typing import Dict, Any, TypedDict

from simulation.simulation_events import Event, EventType
from simulation import Simulation
from config import Config


class MessageData(TypedDict):
    src: str
    dst: str 
    type: str
    payload: Dict[str, Any]


class MessageQueue:
    def __init__(self, config: Config, simulation: Simulation) -> None:
        self.config = config
        self.simulation = simulation

    def send(
        self,
        src: str,
        dst: str,
        message_type: str,
        payload: Dict[str, Any],
        current_time: float
    ) -> None:
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
        return random.random() < self.config.drop_rate

    def _log_send_event(self, timestamp: float, data: MessageData) -> None:
        send_event = Event(EventType.SEND, timestamp, data)
        self.simulation.schedule_event(send_event)

    def _log_drop_event(self, timestamp: float, data: MessageData) -> None:
        drop_event = Event(EventType.MESSAGE_DROPPED, timestamp, data)
        self.simulation.schedule_event(drop_event)

    def _schedule_delivery(self, send_time: float, data: MessageData) -> None:
        latency = random.uniform(self.config.min_latency, self.config.max_latency)
        delivery_time = send_time + latency
        delivery_event = Event(EventType.MESSAGE_RECEIVED, delivery_time, data)
        self.simulation.schedule_event(delivery_event)