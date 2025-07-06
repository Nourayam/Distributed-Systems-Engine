import heapq
import logging
import time
from typing import Dict, List, Optional, Callable, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from nodes.base_node import Node
    from config import Config

from simulation.simulation_events import Event, EventType

logger = logging.getLogger(__name__)


class Simulation:
    """Main simulation engine for distributed systems."""
    
    def __init__(self, config: 'Config'):
        self.config = config
        self.current_time = 0.0
        self.event_queue: List[Event] = []
        self.nodes: Dict[str, 'Node'] = {}
        self.event_log: List[Dict[str, Any]] = []
        self.running = False
        self.logger = logging.getLogger(f"{__name__}.Simulation")
        self._event_sequence_counter = 0  # For unique event sequencing
        
        # Initialize message queue
        from messaging.message_queue import MessageQueue
        self.message_queue = MessageQueue(config, self)
        
        self.logger.info("Simulation initialized")

    def register_node(self, node: 'Node') -> None:
        """Register a node with the simulation."""
        self.nodes[node.node_id] = node
        self.logger.info(f"Registered node {node.node_id}")

    def node_exists(self, node_id: str) -> bool:
        """Check if a node exists in the simulation."""
        return node_id in self.nodes

    def schedule_event(self, event: Event) -> None:
        """Schedule an event for future processing."""
        # Assign unique sequence ID for proper ordering
        event._sequence_id = self._event_sequence_counter
        self._event_sequence_counter += 1
        
        # Validate event before scheduling
        if not isinstance(event.timestamp, (int, float)):
            raise ValueError(f"Event timestamp must be numeric, got {type(event.timestamp)}")
        
        if event.timestamp < 0:
            raise ValueError(f"Event timestamp cannot be negative: {event.timestamp}")
        
        try:
            heapq.heappush(self.event_queue, event)
            self.logger.debug(f"Scheduled {event} (seq: {event._sequence_id})")
        except Exception as e:
            self.logger.error(f"Failed to schedule event {event}: {e}")
            raise

    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log an event to the simulation log."""
        log_entry = {
            'timestamp': self.current_time,
            'type': event_type,
            'data': data
        }
        self.event_log.append(log_entry)
        self.logger.debug(f"Logged event: {event_type}")

    def process_event(self, event: Event) -> None:
    """Process a single event."""
    try:
        if event.event_type == EventType.MESSAGE_RECEIVED:
            self._handle_message_received(event)
        elif event.event_type == EventType.TIMEOUT:
            self._handle_timeout(event)
        elif event.event_type == EventType.ELECTION_TIMEOUT:
            self._handle_election_timeout(event)
        elif event.event_type == EventType.HEARTBEAT_TIMEOUT:
            self._handle_heartbeat_timeout(event)
        elif event.event_type == EventType.NODE_CRASH:
            self._handle_node_crash(event)
        elif event.event_type == EventType.NODE_RECOVER:
            self._handle_node_recover(event)
        elif event.event_type == EventType.MESSAGE_SEND:
            # These are logging events - no action needed
            self.logger.debug(f"Message sent: {event.data.get('type', 'unknown')} from {event.data.get('src')} to {event.data.get('dst')}")
        elif event.event_type == EventType.MESSAGE_DROPPED:
            # These are logging events - no action needed  
            self.logger.debug(f"Message dropped: {event.data.get('type', 'unknown')} from {event.data.get('src')} to {event.data.get('dst')}")
        else:
            self.logger.warning(f"Unhandled event type: {event.event_type}")
    except Exception as e:
        self.logger.error(f"Error processing event {event}: {e}", exc_info=True)

    def _handle_message_received(self, event: Event) -> None:
        """Handle message delivery to target node."""
        data = event.data
        dst_node_id = data['dst']
        
        if dst_node_id not in self.nodes:
            self.logger.warning(f"Message to unknown node: {dst_node_id}")
            return
            
        node = self.nodes[dst_node_id]
        if node.is_alive():
            node.receive_message(event)
        else:
            self.logger.debug(f"Message dropped - node {dst_node_id} is down")

    def _handle_timeout(self, event: Event) -> None:
        """Handle generic timeout event."""
        node_id = event.data.get('node_id')
        if node_id and node_id in self.nodes:
            node = self.nodes[node_id]
            if node.is_alive():
                node.handle_timeout(event)

    def _handle_election_timeout(self, event: Event) -> None:
        """Handle election timeout event."""
        node_id = event.data.get('node_id')
        if node_id and node_id in self.nodes:
            node = self.nodes[node_id]
            if node.is_alive() and hasattr(node, 'handle_election_timeout'):
                node.handle_election_timeout()

    def _handle_heartbeat_timeout(self, event: Event) -> None:
        """Handle heartbeat timeout event."""
        node_id = event.data.get('node_id')
        if node_id and node_id in self.nodes:
            node = self.nodes[node_id]
            if node.is_alive() and hasattr(node, 'handle_heartbeat_timeout'):
                node.handle_heartbeat_timeout()

    def _handle_node_crash(self, event: Event) -> None:
        """Handle node crash event."""
        node_id = event.data.get('node_id')
        if node_id and node_id in self.nodes:
            node = self.nodes[node_id]
            node.crash()

    def _handle_node_recover(self, event: Event) -> None:
        """Handle node recovery event."""
        node_id = event.data.get('node_id')
        if node_id and node_id in self.nodes:
            node = self.nodes[node_id]
            node.recover()

    def run(self, max_time: float = 100.0) -> None:
        """Run the simulation until max_time is reached."""
        self.running = True
        self.logger.info(f"Starting simulation for {max_time} seconds")
        
        try:
            while self.running and self.event_queue and self.current_time < max_time:
                # Process next event
                if not self.event_queue:
                    self.logger.debug("No more events to process")
                    break
                
                event = heapq.heappop(self.event_queue)
                
                # Validate event timestamp
                if event.timestamp < self.current_time:
                    self.logger.warning(f"Event timestamp {event.timestamp} is in the past (current: {self.current_time})")
                
                self.current_time = event.timestamp
                
                # Skip events that are too far in the future
                if self.current_time > max_time:
                    self.logger.debug(f"Reached max time {max_time}, stopping simulation")
                    break
                    
                self.process_event(event)
                
                # Let nodes tick
                for node in self.nodes.values():
                    if node.is_alive():
                        try:
                            node.tick(self.current_time)
                        except Exception as e:
                            self.logger.error(f"Error in node {node.node_id} tick: {e}", exc_info=True)
        
        except Exception as e:
            self.logger.error(f"Simulation error: {e}", exc_info=True)
            raise
        finally:
            self.running = False
            self.logger.info("Simulation completed")

    def get_state(self) -> Dict[str, Any]:
        """Get current simulation state."""
        return {
            'current_time': self.current_time,
            'running': self.running,
            'nodes': {
                node_id: {
                    'alive': node.is_alive(),
                    'state': getattr(node, 'state', 'unknown'),
                    'term': getattr(node, 'current_term', 0)
                }
                for node_id, node in self.nodes.items()
            },
            'event_count': len(self.event_log),
            'pending_events': len(self.event_queue)
        }

    def get_next_event_time(self) -> Optional[float]:
        """Get the timestamp of the next event to be processed."""
        if self.event_queue:
            return self.event_queue[0].timestamp
        return None


# Alias for backward compatibility
EventDrivenSimulator = Simulation