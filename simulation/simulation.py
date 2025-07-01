import heapq
import time
import random
import math
import json
import logging
from enum import Enum
from typing import List, Dict, Any, Optional, Callable, Tuple, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"
    DOWN = "down"
    PARTITIONED = "partitioned"

class EventType(Enum):
    MESSAGE_DELIVER = "message_deliver"
    NODE_CRASH = "node_crash"
    NODE_RECOVER = "node_recover"
    TIMEOUT = "timeout"
    STATE_CHANGE = "state_change"
    PARTITION_START = "partition_start"
    PARTITION_END = "partition_end"
    SIMULATION_START = "simulation_start"
    SIMULATION_END = "simulation_end"

class SimulationEvent:
    __slots__ = ('event_type', 'timestamp', 'data', 'callback')
    
    def __init__(self, 
                 event_type: EventType, 
                 timestamp: float, 
                 data: Dict[str, Any],
                 callback: Optional[Callable] = None):
        self.event_type = event_type
        self.timestamp = timestamp
        self.data = data
        self.callback = callback  # Optional callback for custom handling
        
    def __lt__(self, other):
        return self.timestamp < other.timestamp

class NetworkMessage:
    __slots__ = ('msg_id', 'msg_type', 'sender', 'receiver', 'payload', 'sent_time')
    
    def __init__(self, 
                 msg_id: str, 
                 msg_type: str, 
                 sender: int, 
                 receiver: int, 
                 payload: Dict[str, Any],
                 sent_time: float):
        self.msg_id = msg_id
        self.msg_type = msg_type
        self.sender = sender
        self.receiver = receiver
        self.payload = payload
        self.sent_time = sent_time

class DistributedNode:
    def __init__(self, node_id: int, position: Tuple[float, float] = (0, 0)):
        self.node_id = node_id
        self.state = NodeState.FOLLOWER
        self.term = 0
        self.log = []
        self.state_history = []  # (timestamp, old_state, new_state)
        self.partition_group = None  # For network partition simulation
        self.active = True
        self.position = position
        self.election_timeout = None  # Time when election timeout will occur
        self.last_heartbeat = 0.0  # Timestamp of last received heartbeat
        
    def change_state(self, new_state: NodeState, timestamp: float) -> Tuple[NodeState, NodeState]:
        old_state = self.state
        self.state_history.append((timestamp, old_state, new_state))
        self.state = new_state
        return old_state, new_state
    
    def handle_message(self, message: NetworkMessage, timestamp: float) -> List[NetworkMessage]:
        """Process incoming message and return outgoing messages"""
        # Base implementation - extend this for specific protocols like Raft
        logger.debug(f"Node {self.node_id} received {message.msg_type} message at {timestamp}")
        
        # For Raft, we would add logic here to handle AppendEntries, RequestVote, etc.
        return []
    
    def handle_timeout(self, timeout_type: str, timestamp: float) -> List[NetworkMessage]:
        """Handle timeout events (election, heartbeat, etc.)"""
        logger.debug(f"Node {self.node_id} handling {timeout_type} timeout at {timestamp}")
        
        # For Raft, this would trigger elections or heartbeats
        return []
    
    def schedule_election_timeout(self, timestamp: float, min_timeout: float = 1.0, max_timeout: float = 2.0):
        """Schedule an election timeout at a random time in the future"""
        timeout = random.uniform(min_timeout, max_timeout)
        self.election_timeout = timestamp + timeout
        return self.election_timeout

class EventDrivenSimulator:
    def __init__(self, config: Dict[str, Any], state_callback: Optional[Callable] = None):
        self.clock = 0.0  # Simulation time
        self.event_queue = []  # Min-heap priority queue
        self.nodes: Dict[int, DistributedNode] = {}
        self.config = config
        self.message_drop_rate = config.get('message_drop_rate', 0.1)
        self.min_latency = config.get('min_latency', 0.1)
        self.max_latency = config.get('max_latency', 0.5)
        self.event_log = []  # List of events for logging
        self.partitions: Dict[str, List[int]] = {}  # partition_id: list of nodes
        self.state_callback = state_callback  # Callback to send state updates
        self.running = False
        self.realtime = config.get('realtime', False)
        self.speed = config.get('speed', 1.0)  # Real-time speed multiplier
        self.message_counter = 0
        self.event_counter = 0
        self.simulation_id = f"sim-{int(time.time())}"
        
        # Initialise nodes with positions in a circle
        node_count = config['node_count']
        for i in range(node_count):
            angle = 2 * 3.14159 * i / node_count
            x = 300 + 200 * math.cos(angle)
            y = 300 + 200 * math.sin(angle)
            self.nodes[i] = DistributedNode(i, position=(x, y))
        
        # Schedule initial timeouts (election timeouts for Raft)
        for node in self.nodes.values():
            timeout_at = node.schedule_election_timeout(self.clock)
            self.schedule_event(SimulationEvent(
                event_type=EventType.TIMEOUT,
                timestamp=timeout_at,
                data={
                    'node_id': node.node_id,
                    'timeout_type': 'election'
                }
            ))
        
        # Log simulation start
        self.log_event('SIMULATION_START', {
            'node_count': node_count,
            'config': config
        })
    
    def schedule_event(self, event: SimulationEvent):
        heapq.heappush(self.event_queue, event)
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event for the event log"""
        self.event_counter += 1
        event_id = f"evt-{self.event_counter}"
        event_record = {
            'id': event_id,
            'time': self.clock,
            'type': event_type,
            'data': data
        }
        self.event_log.append(event_record)
        return event_record
    
    def generate_message_id(self) -> str:
        self.message_counter += 1
        return f"msg-{self.message_counter}-{int(time.time())}"
    
    def send_message(self, message: NetworkMessage):
        """Schedule message delivery with simulated latency or drop"""
        # Handle message drop
        if random.random() < self.message_drop_rate:
            self.log_event('MESSAGE_DROP', {
                'message_id': message.msg_id,
                'from': message.sender,
                'to': message.receiver,
                'type': message.msg_type
            })
            return
        
        # Calculate delivery time
        latency = random.uniform(self.min_latency, self.max_latency)
        delivery_time = self.clock + latency
        
        # Schedule delivery event
        self.schedule_event(SimulationEvent(
            event_type=EventType.MESSAGE_DELIVER,
            timestamp=delivery_time,
            data={
                'message': message
            }
        ))
        
        # Log the send event
        self.log_event('MESSAGE_SEND', {
            'message_id': message.msg_id,
            'from': message.sender,
            'to': message.receiver,
            'type': message.msg_type,
            'scheduled_delivery': delivery_time
        })
    
    def crash_node(self, node_id: int, recovery_time: Optional[float] = None):
        """Crash a node and optionally schedule recovery"""
        # Schedule crash immediately
        self.schedule_event(SimulationEvent(
            event_type=EventType.NODE_CRASH,
            timestamp=self.clock,
            data={'node_id': node_id}
        ))
        
        # Schedule recovery if specified
        if recovery_time is not None:
            self.schedule_event(SimulationEvent(
                event_type=EventType.NODE_RECOVER,
                timestamp=self.clock + recovery_time,
                data={'node_id': node_id}
            ))
    
    def create_partition(self, partition_id: str, node_ids: List[int], duration: float):
        """Isolate nodes in a network partition for a duration"""
        # Start partition immediately
        self.schedule_event(SimulationEvent(
            event_type=EventType.PARTITION_START,
            timestamp=self.clock,
            data={
                'partition_id': partition_id,
                'node_ids': node_ids
            }
        ))
        
        # End partition after duration
        self.schedule_event(SimulationEvent(
            event_type=EventType.PARTITION_END,
            timestamp=self.clock + duration,
            data={
                'partition_id': partition_id
            }
        ))
    
    def process_event(self, event: SimulationEvent):
        """Process an event by its type"""
        logger.info(f"Processing {event.event_type.name} at {event.timestamp}")
        
        handler_name = f'handle_{event.event_type.value}'
        if hasattr(self, handler_name):
            handler = getattr(self, handler_name)
            handler(event)
        elif event.callback:
            event.callback(self, event)
        else:
            logger.warning(f"No handler for event type: {event.event_type}")
    
    def handle_message_deliver(self, event: SimulationEvent):
        message = event.data['message']
        receiver_id = message.receiver
        receiver = self.nodes.get(receiver_id)
        
        # If receiver doesn't exist or is down, skip
        if receiver is None or not receiver.active:
            self.log_event('MESSAGE_DROP', {
                'message_id': message.msg_id,
                'reason': 'receiver_down',
                'from': message.sender,
                'to': message.receiver
            })
            return
        
        # If partitioned, check if sender is in the same partition group
        sender = self.nodes.get(message.sender)
        if sender and receiver.partition_group is not None and sender.partition_group != receiver.partition_group:
            # Message is dropped due to partition
            self.log_event('MESSAGE_DROP', {
                'message_id': message.msg_id,
                'reason': 'partition',
                'from': message.sender,
                'to': message.receiver,
                'partition_group': receiver.partition_group
            })
            return
        
        # Log delivery
        self.log_event('MESSAGE_DELIVER', {
            'message_id': message.msg_id,
            'to': message.receiver,
            'latency': event.timestamp - message.sent_time
        })
        
        # Deliver to node
        responses = receiver.handle_message(message, self.clock)
        for response in responses:
            self.send_message(response)
    
    def handle_node_crash(self, event: SimulationEvent):
        node_id = event.data['node_id']
        node = self.nodes[node_id]
        if node.active:
            old_state, new_state = node.change_state(NodeState.DOWN, self.clock)
            node.active = False
            self.log_event('STATE_CHANGE', {
                'node_id': node_id,
                'old_state': old_state.value,
                'new_state': new_state.value
            })
    
    def handle_node_recover(self, event: SimulationEvent):
        node_id = event.data['node_id']
        node = self.nodes[node_id]
        if not node.active:
            old_state, new_state = node.change_state(NodeState.FOLLOWER, self.clock)
            node.active = True
            # Schedule a new election timeout
            timeout_at = node.schedule_election_timeout(self.clock)
            self.schedule_event(SimulationEvent(
                event_type=EventType.TIMEOUT,
                timestamp=timeout_at,
                data={
                    'node_id': node_id,
                    'timeout_type': 'election'
                }
            ))
            self.log_event('STATE_CHANGE', {
                'node_id': node_id,
                'old_state': old_state.value,
                'new_state': new_state.value
            })
    
    def handle_partition_start(self, event: SimulationEvent):
        partition_id = event.data['partition_id']
        node_ids = event.data['node_ids']
        self.partitions[partition_id] = node_ids
        
        for nid in node_ids:
            node = self.nodes[nid]
            # Only partition active nodes
            if node.active:
                old_state, new_state = node.change_state(NodeState.PARTITIONED, self.clock)
                node.partition_group = partition_id
                self.log_event('STATE_CHANGE', {
                    'node_id': nid,
                    'old_state': old_state.value,
                    'new_state': new_state.value,
                    'partition_id': partition_id
                })
    
    def handle_partition_end(self, event: SimulationEvent):
        partition_id = event.data['partition_id']
        if partition_id not in self.partitions:
            return
            
        node_ids = self.partitions[partition_id]
        for nid in node_ids:
            node = self.nodes[nid]
            if node.active and node.partition_group == partition_id:
                old_state, new_state = node.change_state(NodeState.FOLLOWER, self.clock)
                node.partition_group = None
                self.log_event('STATE_CHANGE', {
                    'node_id': nid,
                    'old_state': old_state.value,
                    'new_state': new_state.value
                })
        
        del self.partitions[partition_id]
    
    def handle_timeout(self, event: SimulationEvent):
        node_id = event.data['node_id']
        timeout_type = event.data['timeout_type']
        node = self.nodes[node_id]
        
        if not node.active:
            return
        
        # Let the node handle the timeout and get responses
        responses = node.handle_timeout(timeout_type, self.clock)
        for response in responses:
            self.send_message(response)
        
        # If it was an election timeout, reschedule
        if timeout_type == 'election':
            timeout_at = node.schedule_election_timeout(self.clock)
            self.schedule_event(SimulationEvent(
                event_type=EventType.TIMEOUT,
                timestamp=timeout_at,
                data={
                    'node_id': node_id,
                    'timeout_type': 'election'
                }
            ))
    
    def get_current_state(self) -> Dict[str, Any]:
        """Return the current state of the simulation in JSON format"""
        node_states = []
        for node_id, node in self.nodes.items():
            node_states.append({
                'id': node_id,
                'state': node.state.value,
                'term': node.term,
                'active': node.active,
                'partition_group': node.partition_group,
                'position': node.position,
                'metadata': {
                    'last_heartbeat': node.last_heartbeat,
                    'election_timeout': node.election_timeout
                }
            })
        
        # Collect in-transit messages
        messages_in_transit = []
        for event in self.event_queue:
            if event.event_type == EventType.MESSAGE_DELIVER:
                msg = event.data['message']
                progress = (self.clock - msg.sent_time) / (event.timestamp - msg.sent_time)
                messages_in_transit.append({
                    'id': msg.msg_id,
                    'from': msg.sender,
                    'to': msg.receiver,
                    'type': msg.msg_type,
                    'sent_time': msg.sent_time,
                    'delivery_time': event.timestamp,
                    'progress': min(progress, 0.99),  # Cap at 99% until delivered
                    'status': 'in-transit',
                    'payload': msg.payload
                })
        
        return {
            'simulation': {
                'id': self.simulation_id,
                'current_time': self.clock,
                'max_time': max([evt.timestamp for evt in self.event_queue] + [self.clock]),
                'speed': self.speed,
                'status': 'running' if self.running else 'paused',
                'message_drop_rate': self.message_drop_rate
            },
            'nodes': node_states,
            'messages': messages_in_transit,
            'events': self.event_log[-100:],  # Last 100 events
            'partitions': [
                {'id': pid, 'nodes': nodes} for pid, nodes in self.partitions.items()
            ]
        }
    
    def update_frontend(self):
        """Send current state to frontend via callback"""
        if self.state_callback:
            state = self.get_current_state()
            self.state_callback(state)
    
    def run(self, max_time: float = 100.0):
        """Run the simulation until max_time is reached"""
        self.running = True
        start_real = time.time()
        last_update = 0.0
        
        while self.running and self.event_queue and self.clock <= max_time:
            # Process the next event
            event = heapq.heappop(self.event_queue)
            self.clock = event.timestamp
            
            # Sync with real time if in realtime mode
            if self.realtime:
                elapsed_real = time.time() - start_real
                sleep_time = (self.clock - elapsed_real) / self.speed
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            self.process_event(event)
            
            # Update frontend at most 30 times per second
            if self.clock - last_update > 0.033:  # ~30 fps
                self.update_frontend()
                last_update = self.clock
        
        self.running = False
        self.log_event('SIMULATION_END', {'reason': 'completed'})
        self.update_frontend()
    
    def pause(self):
        self.running = False
    
    def resume(self):
        if not self.running:
            self.running = True
            self.run()
    
    def step(self):
        """Execute the next event"""
        if self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.clock = event.timestamp
            self.process_event(event)
            self.update_frontend()
    
    def inject_message(self, sender: int, receiver: int, msg_type: str, payload: Dict[str, Any]):
        """Inject a custom message into the system"""
        msg_id = self.generate_message_id()
        message = NetworkMessage(
            msg_id=msg_id,
            msg_type=msg_type,
            sender=sender,
            receiver=receiver,
            payload=payload,
            sent_time=self.clock
        )
        self.send_message(message)
    
    def inject_failure(self, failure_type: str, **kwargs):
        """Inject a failure based on type and parameters"""
        if failure_type == 'crash':
            node_id = kwargs['node_id']
            recovery_time = kwargs.get('recovery_time')
            self.crash_node(node_id, recovery_time)
        elif failure_type == 'partition':
            partition_id = kwargs.get('partition_id', f"part-{int(time.time())}")
            node_ids = kwargs['node_ids']
            duration = kwargs['duration']
            self.create_partition(partition_id, node_ids, duration)
        else:
            logger.warning(f"Unknown failure type: {failure_type}")

# WebSocket server helper (for integration)
class SimulationServer:
    def __init__(self, config: Dict[str, Any]):
        self.simulator = EventDrivenSimulator(config, self.state_callback)
        self.clients = set()
        
    def state_callback(self, state: Dict[str, Any]):
        """Broadcast state to all connected clients"""
        message = json.dumps({'type': 'state_update', 'data': state})
        for client in self.clients:
            client.send(message)
    
    def handle_client_message(self, client, message: Dict[str, Any]):
        action = message.get('action')
        
        if action == 'start':
            self.simulator.run()
        elif action == 'pause':
            self.simulator.pause()
        elif action == 'resume':
            self.simulator.resume()
        elif action == 'step':
            self.simulator.step()
        elif action == 'inject_failure':
            self.simulator.inject_failure(**message['params'])
        elif action == 'inject_message':
            self.simulator.inject_message(**message['params'])
        elif action == 'set_time':
            # This would require more complex implementation
            logger.warning("Time setting not implemented yet")
    
    def add_client(self, client):
        self.clients.add(client)
        # Send initial state
        client.send(json.dumps({
            'type': 'full_state',
            'data': self.simulator.get_current_state()
        }))
    
    def remove_client(self, client):
        self.clients.discard(client)

# Example usage
if __name__ == "__main__":
    # Default configuration
    config = {
        'node_count': 5,
        'message_drop_rate': 0.2,
        'min_latency': 0.1,
        'max_latency': 0.5,
        'realtime': False
    }
    
    # Create a simulator instance
    sim = EventDrivenSimulator(config)
    
    # Inject a crash of node 1 at time 0 (immediately) with recovery after 10 seconds
    sim.inject_failure('crash', node_id=1, recovery_time=10)
    
    # Create a partition between nodes [0,1] and others for 15 seconds
    sim.inject_failure('partition', node_ids=[0,1], duration=15)
    
    # Run for 30 seconds of simulation time
    sim.run(max_time=30)
    
    # Output final state
    print(json.dumps(sim.get_current_state(), indent=2))