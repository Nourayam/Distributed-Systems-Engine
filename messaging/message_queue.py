import random
from typing import Dict, Any
from simulation.simulation_events import Event, EventType
from simulation.simulation import Simulation
from config import Config


class MessageQueue:
    #A message queue that simulates network communication with latency and packet drops.
    # Attributes:
    #     config: The simulation configuration containing network parameters.
    #     simulation: The simulation instance where events will be scheduled.

    
    def __init__(self, config: Config, simulation: Simulation):
        # Initialise the message queue with configuration and simulation reference.
        
        # Args:
        #     config: Configuration object containing network parameters like drop rate and latency.
        #     simulation: The simulation instance where events will be scheduled.
        
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
        #Send a message from source to destination with potential latency and drops.
        
        # Args:
        #     src: Identifier of the message sender.
        #     dst: Identifier of the message receiver.
        #     message_type: Type/category of the message.
        #     payload: Dictionary containing the message content.
        #     current_time: The simulation time when the message is sent.
    
        # Create the message data structure
        data = {
            'src': src,
            'dst': dst,
            'type': message_type,
            'payload': payload
        }
        
        # Always log the send event (for tracking purposes)
        send_event = Event(EventType.SEND, current_time, data)
        self.simulation.schedule_event(send_event)
        
        # Check if the message should be dropped
        if random.random() < self.config.drop_rate:
            drop_event = Event(EventType.MESSAGE_DROPPED, current_time, data)
            self.simulation.schedule_event(drop_event)
            return
        
        # Calculate random network latency and delivery time
        latency = random.uniform(self.config.min_latency, self.config.max_latency)
        delivery_time = current_time + latency
        
        # Schedule the message delivery event
        delivery_event = Event(EventType.MESSAGE_RECEIVED, delivery_time, data)
        self.simulation.schedule_event(delivery_event)
