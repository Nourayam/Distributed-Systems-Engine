# Create a Python module at simulation/message_queue.py.

# Requirements:

# 1. Imports:
#    - import random
#    - from typing import Dict, Any
#    - from simulation.simulation_events import Event, EventType
#    - from simulation.simulation import Simulation
#    - from config import Config

# 2. Class definition:
#    class MessageQueue:
#        def __init__(self, config: Config, simulation: Simulation):
#            - self.config = config
#            - self.simulation = simulation

# 3. Method send:
#    def send(
#        self,
#        src: str,
#        dst: str,
#        message_type: str,
#        payload: Dict[str, Any],
#        current_time: float
#    ) -> None:
#        - Build data dict: {'src': src, 'dst': dst, 'type': message_type, 'payload': payload}
#        - Always log send: schedule an Event(EventType.SEND, current_time, data)
#        - If random.random() < config.drop_rate:
#            - Schedule EventType.MESSAGE_DROPPED at current_time
#            - return
#        - Compute latency: random.uniform(config.min_latency, config.max_latency)
#        - delivery_time = current_time + latency
#        - Create Event(EventType.SEND, delivery_time, data)
#        - Call simulation.schedule_event(event)

# 4. Docstrings and inline comments explaining each step.

# Output the full module code only.
