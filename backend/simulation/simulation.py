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
    #main simulation engine
    
    def __init__(self, config: 'Config'):
        self.config = config
        self.current_time = 0.0
        self.event_queue: List[Event] = []
        self.nodes: Dict[str, 'Node'] = {}
        self.event_log: List[Dict[str, Any]] = []
        self.running = False
        self.logger = logging.getLogger(f"{__name__}.Simulation")
        self._event_sequence_counter = 0  #for unique event sequencing
        
        from messaging.message_queue import MessageQueue
        self.message_queue = MessageQueue(config, self)
        
        self.logger.info("Simulation initialized")

    def register_node(self, node: 'Node') -> None:
        self.nodes[node.node_id] = node
        self.logger.info(f"Registered node {node.node_id}")

    def node_exists(self, node_id: str) -> bool: #checking if it exists
        return node_id in self.nodes

    def schedule_event(self, event: Event) -> None:
        #for future processing
        #assigns unique sequence ID for proper ordering
        event._sequence_id = self._event_sequence_counter
        self._event_sequence_counter += 1
        
        #validate before scheduling
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
        log_entry = {
            'timestamp': self.current_time,
            'type': event_type,
            'data': data
        }
        self.event_log.append(log_entry)
        self.logger.debug(f"Logged event: {event_type}")

    def process_event(self, event: Event) -> None:
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
                # These are logging events - no action needed, just debug log
                self.logger.debug(f"Message sent: {event.data.get('type', 'unknown')} "
                                f"from {event.data.get('src')} to {event.data.get('dst')}")
            elif event.event_type == EventType.MESSAGE_DROPPED:
                # These are logging events - no action needed, just debug log
                self.logger.debug(f"Message dropped: {event.data.get('type', 'unknown')} "
                                f"from {event.data.get('src')} to {event.data.get('dst')}")
            else:
                self.logger.warning(f"Unhandled event type: {event.event_type}")
        except Exception as e:
            self.logger.error(f"Error processing event {event}: {e}", exc_info=True)

    def _handle_message_received(self, event: Event) -> None:
        try:
            data = event.data
            dst_node_id = data.get('dst')
            
            if not dst_node_id:
                self.logger.warning("Message event missing destination node ID")
                return
                
            if dst_node_id not in self.nodes:
                self.logger.warning(f"Message to unknown node: {dst_node_id}")
                return
                
            node = self.nodes[dst_node_id]
            if node.is_alive():
                node.receive_message(event)
                self.logger.debug(f"Delivered {data.get('type', 'unknown')} message to node {dst_node_id}")
            else:
                self.logger.debug(f"Message dropped - node {dst_node_id} is down")
        except Exception as e:
            self.logger.error(f"Error handling message received: {e}", exc_info=True)

    def _handle_timeout(self, event: Event) -> None:
        #generic timeout events
        try:
            node_id = event.data.get('node_id')
            if node_id and node_id in self.nodes:
                node = self.nodes[node_id]
                if node.is_alive() and hasattr(node, 'handle_timeout'):
                    node.handle_timeout(event)
                    self.logger.debug(f"Processed timeout event for node {node_id}")
            else:
                self.logger.debug(f"Timeout event for unknown/invalid node: {node_id}")
        except Exception as e:
            self.logger.error(f"Error handling timeout: {e}", exc_info=True)

    def _handle_election_timeout(self, event: Event) -> None:
        try:
            node_id = event.data.get('node_id')
            if node_id and node_id in self.nodes:
                node = self.nodes[node_id]
                if node.is_alive() and hasattr(node, 'handle_election_timeout'):
                    node.handle_election_timeout()
                    self.logger.debug(f"Processed election timeout for node {node_id}")
            else:
                self.logger.debug(f"Election timeout for unknown/invalid node: {node_id}")
        except Exception as e:
            self.logger.error(f"Error handling election timeout: {e}", exc_info=True)

    def _handle_heartbeat_timeout(self, event: Event) -> None:
        try:
            node_id = event.data.get('node_id')
            if node_id and node_id in self.nodes:
                node = self.nodes[node_id]
                if node.is_alive() and hasattr(node, 'handle_heartbeat_timeout'):
                    node.handle_heartbeat_timeout()
                    self.logger.debug(f"Processed heartbeat timeout for node {node_id}")
            else:
                self.logger.debug(f"Heartbeat timeout for unknown/invalid node: {node_id}")
        except Exception as e:
            self.logger.error(f"Error handling heartbeat timeout: {e}", exc_info=True)

    def _handle_node_crash(self, event: Event) -> None:
        try:
            node_id = event.data.get('node_id')
            if node_id and node_id in self.nodes:
                node = self.nodes[node_id]
                if node.is_alive():
                    node.crash()
                    self.logger.info(f"Node {node_id} crashed")
                    # Log the crash event
                    self.log_event('NODE_CRASH', {'node_id': node_id, 'timestamp': self.current_time})
            else:
                self.logger.warning(f"Crash event for unknown node: {node_id}")
        except Exception as e:
            self.logger.error(f"Error handling node crash: {e}", exc_info=True)

    def _handle_node_recover(self, event: Event) -> None:
        try:
            node_id = event.data.get('node_id')
            if node_id and node_id in self.nodes:
                node = self.nodes[node_id]
                if not node.is_alive():
                    node.recover()
                    self.logger.info(f"Node {node_id} recovered")
                    # Log the recovery event
                    self.log_event('NODE_RECOVER', {'node_id': node_id, 'timestamp': self.current_time})
            else:
                self.logger.warning(f"Recovery event for unknown node: {node_id}")
        except Exception as e:
            self.logger.error(f"Error handling node recovery: {e}", exc_info=True)

    def run(self, max_time: float = 100.0) -> None:
        #runs simulation until the max time is reached
        self.running = True
        self.logger.info(f"Starting simulation for {max_time} seconds")
        
        event_count = 0
        last_progress_time = 0.0
        
        try:
            while self.running and self.event_queue and self.current_time < max_time:
                # Process next event
                if not self.event_queue:
                    self.logger.debug("No more events to process")
                    break
                
                event = heapq.heappop(self.event_queue)
                event_count += 1
                
                if event.timestamp < self.current_time:
                    self.logger.warning(f"Event timestamp {event.timestamp:.3f} is in the past "
                                      f"(current: {self.current_time:.3f})")
                
                self.current_time = event.timestamp
                
                #skips events that are too far in the future
                if self.current_time > max_time:
                    self.logger.debug(f"Reached max time {max_time}, stopping simulation")
                    break
                
                self.process_event(event)
                
                #lets nodes tick (but not too frequently to avoid overhead)
                if self.current_time - last_progress_time >= 0.1:  #every 100ms of sim time
                    for node in self.nodes.values():
                        if node.is_alive():
                            try:
                                node.tick(self.current_time)
                            except Exception as e:
                                self.logger.error(f"Error in node {node.node_id} tick: {e}", exc_info=True)
                    last_progress_time = self.current_time
                
                #periodic progress logging for long simulations
                if event_count % 10000 == 0:
                    self.logger.debug(f"Processed {event_count} events, sim time: {self.current_time:.2f}s")
        
        except KeyboardInterrupt:
            self.logger.info("Simulation interrupted by user")
        except Exception as e:
            self.logger.error(f"Simulation error: {e}", exc_info=True)
            raise
        finally:
            self.running = False
            self.logger.info(f"Simulation completed. Processed {event_count} events in {self.current_time:.2f}s sim time")

    def get_state(self) -> Dict[str, Any]:
        #get current simulation state
        return {
            'current_time': self.current_time,
            'running': self.running,
            'nodes': {
                node_id: {
                    'alive': node.is_alive(),
                    'state': getattr(node, 'state', 'unknown').name if hasattr(getattr(node, 'state', None), 'name') else str(getattr(node, 'state', 'unknown')),
                    'term': getattr(node, 'current_term', 0),
                    'voted_for': getattr(node, 'voted_for', None),
                    'log_length': len(getattr(node, 'log', [])),
                    'commit_index': getattr(node, 'commit_index', 0)
                }
                for node_id, node in self.nodes.items()
            },
            'event_count': len(self.event_log),
            'pending_events': len(self.event_queue)
        }

    def get_next_event_time(self) -> Optional[float]:
        #gets the timestamp of next event to be processed
        if self.event_queue:
            return self.event_queue[0].timestamp
        return None

    def pause(self) -> None:
        self.running = False
        self.logger.info("Simulation paused")

    def resume(self, max_time: float = 100.0) -> None:
        if not self.running:
            self.logger.info("Resuming simulation")
            self.run(max_time)

    def step(self) -> bool:
        #executes the next event and returns True if an event was processed
        if not self.event_queue:
            return False
        
        event = heapq.heappop(self.event_queue)
        self.current_time = event.timestamp
        self.process_event(event)
        
        for node in self.nodes.values():
            if node.is_alive():
                try:
                    node.tick(self.current_time)
                except Exception as e:
                    self.logger.error(f"Error in node {node.node_id} tick: {e}", exc_info=True)
        
        return True

    def inject_failure(self, failure_type: str, **kwargs) -> None:
        if failure_type == 'crash':
            node_id = kwargs.get('node_id')
            recovery_time = kwargs.get('recovery_time')
            
            if node_id and node_id in self.nodes:
                # Schedule crash immediately
                crash_event = Event(
                    timestamp=self.current_time,
                    event_type=EventType.NODE_CRASH,
                    data={'node_id': node_id}
                )
                self.schedule_event(crash_event)
                
                if recovery_time:
                    recovery_event = Event(
                        timestamp=self.current_time + recovery_time,
                        event_type=EventType.NODE_RECOVER,
                        data={'node_id': node_id}
                    )
                    self.schedule_event(recovery_event)
                    
                self.logger.info(f"Scheduled crash for node {node_id}" + 
                               (f" with recovery in {recovery_time}s" if recovery_time else ""))
            else:
                self.logger.warning(f"Cannot crash unknown node: {node_id}")
        else:
            self.logger.warning(f"Unknown failure type: {failure_type}")

    def get_statistics(self) -> Dict[str, Any]:
        node_states = {}
        for node_id, node in self.nodes.items():
            if hasattr(node, 'state'):
                state_name = node.state.name if hasattr(node.state, 'name') else str(node.state)
                node_states[state_name] = node_states.get(state_name, 0) + 1
        
        return {
            'simulation_time': self.current_time,
            'total_events': len(self.event_log),
            'events_processed': self._event_sequence_counter,
            'pending_events': len(self.event_queue),
            'node_count': len(self.nodes),
            'node_states': node_states,
            'alive_nodes': sum(1 for node in self.nodes.values() if node.is_alive()),
            'dead_nodes': sum(1 for node in self.nodes.values() if not node.is_alive())
        }


#for backward compatibility
EventDrivenSimulator = Simulation