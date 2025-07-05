from abc import ABC, abstractmethod
from typing import List, Dict, Any, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ..simulation.simulation_events import Event, EventType
    from ..simulation.simulation import Simulation

class Node(ABC):
    # Abstract base class for all nodes in the distributed system simulation.
    def __init__(self, node_id: str, simulation: 'Simulation'):
    #Initialise a node with unique identifier and simulation reference.
        
        # Args:
        #     node_id: Unique identifier for this node
        #     simulation: Reference to the simulation engine
    
        self.node_id = node_id
        self.simulation = simulation
        self.inbox: List['Event'] = []
        self.logger = logging.getLogger(f"Node[{node_id}]")
        self.alive = True
        
        # Register node with simulation engine
        self.simulation.register_node(self)
        self.logger.info("Node initialised and registered")
    
    def __repr__(self) -> str:
        return f"<Node {self.node_id} alive={self.alive}>"
    
    @abstractmethod
    def receive_message(self, event: 'Event') -> None:
       #Handle an incoming message event (abstract method) 
        pass
    
    @abstractmethod
    def tick(self, current_time: float) -> None:
       #Perform time-based operations (abstract method) 
        pass
    
    def send_message(
        self, 
        dst_id: str, 
        message_type: str, 
        payload: Dict[str, Any],
        delay: float = 0.0
    ) -> None:
        # Send a message to another node with optional delay.
        
        # Args:
        #     dst_id: Destination node ID
        #     message_type: Type of message being sent
        #     payload: Message content
        #     delay: Optional delay before sending (in simulation time)
    
        # Validate destination exists
        if not self.simulation.node_exists(dst_id):
            self.logger.warning(f"Attempted to send to unknown node: {dst_id}")
            return
            
        # Prepare message data
        message_data = {
            'src': self.node_id,
            'dst': dst_id,
            'type': message_type,
            'payload': payload
        }
        
        # Create and schedule event
        event = Event(
            timestamp=self.simulation.current_time + delay,
            event_type=EventType.MESSAGE_SEND,
            data=message_data
        )
        self.simulation.schedule_event(event)
        self.logger.debug(f"Scheduled {message_type} to {dst_id} at {event.timestamp:.2f}")
    
    def process_inbox(self) -> None:
        # Process all messages in the inbox (FIFO order)
        while self.inbox:
            event = self.inbox.pop(0)
            try:
                self.logger.debug(
                    f"Processing {event.data['type']} from {event.data['src']} "
                    f"at {event.timestamp:.2f}"
                )
                self.receive_message(event)
            except Exception as e:
                self.logger.error(f"Error processing message: {str(e)}", exc_info=True)
    
    def is_alive(self) -> bool:
        #Check if node is operational (not crashed)
        return self.alive
    
    def crash(self) -> None:
        # Mark node as crashed and log the event
        if self.alive:
            self.alive = False
            self.logger.warning("Node crashed!")
            self.simulation.log_event(
                event_type='NODE_CRASH',
                data={'node_id': self.node_id}
            )
    
    def recover(self) -> None:
        # Recover node from crashed state
        if not self.alive:
            self.alive = True
            self.logger.info("Node recovered from crash")
            self.simulation.log_event(
                event_type='NODE_RECOVER',
                data={'node_id': self.node_id}
            )
    
    def schedule_timeout(
        self, 
        delay: float, 
        tag: str, 
        payload: Dict[str, Any] = None
    ) -> None:
        # Schedule a timeout event for this node.
        
        # Args:
        #     delay: When the timeout should occur (relative to current time)
        #     tag: Identifier for this timeout
        #     payload: Optional additional data
    
        event = Event(
            timestamp=self.simulation.current_time + delay,
            event_type=EventType.TIMEOUT,
            data={
                'node_id': self.node_id,
                'tag': tag,
                'payload': payload or {}
            }
        )
        self.simulation.schedule_event(event)
        self.logger.debug(f"Scheduled timeout '{tag}' in {delay:.2f}s")