from abc import ABC, abstractmethod
from typing import List, Dict, Any, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from simulation.simulation_events import Event
    from simulation.simulation import Simulation


class Node(ABC):
    """Abstract base class for all nodes in the distributed system simulation."""
    
    def __init__(self, node_id: str, simulation: 'Simulation'):
        """Initialize a node with unique identifier and simulation reference."""
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
        """Handle an incoming message event (abstract method)"""
        pass
    
    @abstractmethod
    def tick(self, current_time: float) -> None:
        """Perform time-based operations (abstract method)"""
        pass
    
    def send_message(
        self, 
        dst_id: str, 
        message_type: str, 
        payload: Dict[str, Any],
        delay: float = 0.0
    ) -> None:
        """Send a message to another node with optional delay."""
        if not self.simulation.node_exists(dst_id):
            self.logger.warning(f"Attempted to send to unknown node: {dst_id}")
            return
        
        # Validate delay
        if delay < 0:
            self.logger.warning(f"Negative delay {delay} corrected to 0")
            delay = 0.0
        
        # Use message queue for realistic network behavior
        send_time = self.simulation.current_time + delay
        
        try:
            self.simulation.message_queue.send(
                self.node_id, dst_id, message_type, payload, send_time
            )
            self.logger.debug(f"Sent {message_type} to {dst_id}")
        except Exception as e:
            self.logger.error(f"Failed to send {message_type} to {dst_id}: {e}")
    
    def is_alive(self) -> bool:
        """Check if node is operational (not crashed)"""
        return self.alive
    
    def crash(self) -> None:
        """Mark node as crashed and log the event"""
        if self.alive:
            self.alive = False
            self.logger.warning("Node crashed!")
            self.simulation.log_event('NODE_CRASH', {'node_id': self.node_id})
    
    def recover(self) -> None:
        """Recover node from crashed state"""
        if not self.alive:
            self.alive = True
            self.logger.info("Node recovered from crash")
            self.simulation.log_event('NODE_RECOVER', {'node_id': self.node_id})
    
    def schedule_timeout(
        self, 
        delay: float, 
        event_type: str, 
        data: Dict[str, Any] = None
    ) -> None:
        """Schedule a timeout event for this node."""
        from simulation.simulation_events import Event, EventType
        
        # Validate delay
        if delay < 0:
            self.logger.warning(f"Negative delay {delay} corrected to 0")
            delay = 0.0
        
        # Map string event types to EventType enum
        event_type_map = {
            'election': EventType.ELECTION_TIMEOUT,
            'heartbeat': EventType.HEARTBEAT_TIMEOUT,
            'timeout': EventType.TIMEOUT
        }
        
        event_enum = event_type_map.get(event_type, EventType.TIMEOUT)
        
        timeout_data = {'node_id': self.node_id}
        if data:
            timeout_data.update(data)
        
        event = Event(
            timestamp=self.simulation.current_time + delay,
            event_type=event_enum,
            data=timeout_data
        )
        
        try:
            self.simulation.schedule_event(event)
            self.logger.debug(f"Scheduled {event_type} timeout in {delay:.3f}s")
        except Exception as e:
            self.logger.error(f"Failed to schedule {event_type} timeout: {e}")
    
    def handle_timeout(self, event: 'Event') -> None:
        """Handle a timeout event (default implementation)"""
        self.logger.debug(f"Timeout event: {event.data}")