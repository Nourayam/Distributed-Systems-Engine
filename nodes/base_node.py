
# Defines an abstract base Node for discrete-event simulations in distributed systems.
# Each Node holds a unique ID, references the Simulation engine, and manages an inbox
# for incoming events. Concrete nodes must implement message handling and time-based logic.


from abc import ABC, abstractmethod
from typing import List, Dict, Any, TYPE_CHECKING
import logging

# Avoid circular imports for type checking
if TYPE_CHECKING:
    from simulation.simulation_events import Event, EventType
    from simulation.simulation import Simulation

class Node(ABC):
    
    # Abstract base class for all nodes in the distributed system simulation
    
    # Attributes:
    #     node_id: Unique string identifier for the node
    #     simulation: Reference to the simulation engine instance
    #     inbox: FIFO queue for incoming message events
    #     alive: Operational status of the node (True = functional, False = crashed)
    
    
    def __init__(self, node_id: str, simulation: 'Simulation'):
        
        # Initialise a node with unique identifier and simulation reference
        
        # Args:
        #     node_id: Unique string identifier for the node
        #     simulation: Reference to the simulation engine instance
        
        self.node_id = node_id
        self.simulation = simulation
        self.inbox: List['Event'] = []
        self.logger = logging.getLogger(f"Node[{node_id}]")
        self.alive = True  # Single flag for operational status
        
        # Register node with simulation engine
        self.simulation.register_node(self)
        self.logger.info("Node initialised and registered")
    
    def __repr__(self) -> str:
        #Human-readable representation for debugging
        return f"<Node {self.node_id} alive={self.alive}>"
    
    @abstractmethod
    def receive_message(self, event: 'Event') -> None:
        
        # Handle an incoming message event (abstract method)
        
        # Args:
        #     event: Event containing message details in event.data
        
        pass
    
    @abstractmethod
    def tick(self, current_time: float) -> None:
        
        # Perform time-based operations (abstract method)
        
        # Called by the simulation engine at each time step. Concrete implementations
        # should handle timeouts, state transitions, and periodic actions here.
        
        # Args:
        #     current_time: Current simulation time in seconds
        
        pass
    
    def send_message(
        self, 
        dst_id: str, 
        message_type: str, 
        payload: Dict[str, Any],
        delay: float = 0.0
    ) -> None:
        
        # Send a message to another node with optional delay
        
        # Args:
        #     dst_id: Destination node ID
        #     message_type: Message category (e.g., 'HEARTBEAT', 'VOTE_REQUEST')
        #     payload: Dictionary containing message content
        #     delay: Optional transmission delay in simulation seconds
        
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
        from simulation.simulation_events import Event, EventType
        event = Event(
            timestamp=self.simulation.current_time + delay,
            event_type=EventType.MESSAGE_SEND,
            data=message_data
        )
        self.simulation.schedule_event(event)
        self.logger.debug(f"Scheduled {message_type} to {dst_id} at {event.timestamp:.2f}")
    
    def process_inbox(self) -> None:
        #Process all messages in the inbox (FIFO order)
        while self.inbox:
            event = self.inbox.pop(0)
            try:
                self.logger.debug(
                    f"Processing {event.data['type']} from {event.data['src']} "
                    f"at {event.timestamp:.2f}"
                )
                self.receive_message(event)
            except Exception as e:
                # Gracefully handle errors without crashing simulation
                self.logger.error(
                    f"Error processing message: {str(e)}",
                    exc_info=True
                )
    
    def is_alive(self) -> bool:
        #Check if node is operational (not crashed)
        return self.alive
    
    def crash(self) -> None:
        #Mark node as crashed and log the event
        if self.alive:
            self.alive = False
            self.logger.warning("Node crashed!")
            
            # Notify simulation of failure
            self.simulation.log_event(
                event_type='NODE_CRASH',
                data={'node_id': self.node_id}
            )
    
    def recover(self) -> None:
        #Recover node from crashed state
        if not self.alive:
            self.alive = True
            self.logger.info("Node recovered from crash")
            
            # Notify simulation of recovery
            self.simulation.log_event(
                event_type='NODE_RECOVER',
                data={'node_id': self.node_id}
            )
    
    def schedule_timeout(self, delay: float, tag: str, payload: Dict[str, Any] = None) -> None:
        
        # Schedule a timeout event for this node
        
        # Args:
        #     delay: Timeout duration in simulation seconds
        #     tag: Identifier for timeout type
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

# Example implementation and test
if __name__ == "__main__":
    # Dummy implementations for testing
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from simulation.simulation_events import Event, EventType
    from simulation.simulation import Simulation
    
    class DummySimulation(Simulation):
        """Mock simulation for testing"""
        def __init__(self):
            self.current_time = 0.0
            self.nodes = {}
            self.event_queue = []
            self.log = []
        
        def schedule_event(self, event):
            heapq.heappush(self.event_queue, (event.timestamp, event))
        
        def register_node(self, node):
            self.nodes[node.node_id] = node
        
        def node_exists(self, node_id):
            return node_id in self.nodes
        
        def log_event(self, event_type, data):
            self.log.append((event_type, data))
    
    class TestNode(Node):
        """Concrete node implementation for testing"""
        def receive_message(self, event):
            print(f"Node {self.node_id} received: {event.data['type']}")
        
        def tick(self, current_time):
            print(f"Node {self.node_id} tick at {current_time:.1f}")
    
    # Setup simulation and nodes
    sim = DummySimulation()
    node1 = TestNode("node-1", sim)
    node2 = TestNode("node-2", sim)
    
    # Send message from node1 to node2
    node1.send_message("node-2", "TEST_MSG", {"key": "value"})
    
    # Create and deliver message event
    test_event = Event(
        timestamp=1.0,
        event_type=EventType.MESSAGE_SEND,
        data={
            'src': 'node-1',
            'dst': 'node-2',
            'type': 'TEST_MSG',
            'payload': {}
        }
    )
    
    # Process message
    node2.inbox.append(test_event)
    node2.process_inbox()
    
    # Test crash/recovery
    print("Node alive:", node1.is_alive())  # True
    node1.crash()
    print("Node alive after crash:", node1.is_alive())  # False
    node1.recover()
    print("Node alive after recovery:", node1.is_alive())  # True
    
    # Test time-based tick
    node1.tick(2.5)
    
    # Test timeout scheduling
    node1.schedule_timeout(3.0, "ELECTION_TIMEOUT")
    print("Scheduled timeout:", sim.event_queue[0][1])