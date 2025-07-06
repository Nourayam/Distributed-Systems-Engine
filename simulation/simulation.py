import heapq
import json
import logging
import math
import random
import time
from enum import Enum
from typing import (Any, Callable, Dict, List, Optional, Set, Tuple, Union,
                    cast)

from nodes.base_node import Node
from ..simulation.simulation_events import Event, EventType  # Added missing import

# Configure logging
logger = logging.getLogger(__name__)


class NodeState(Enum):
    #Possible states for a node in the simulation.
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"
    DOWN = "down"
    PARTITIONED = "partitioned"


class SimulationEvent:
    #Represents an event in the simulation timeline
    __slots__ = ('event_type', 'timestamp', 'data', 'callback')

    def __init__(
        self,
        event_type: str,
        timestamp: float,
        data: Dict[str, Any],
        callback: Optional[Callable] = None
    ):
        self.event_type = event_type
        self.timestamp = timestamp
        self.data = data
        self.callback = callback

    def __lt__(self, other: 'SimulationEvent') -> bool:
        return self.timestamp < other.timestamp


class NetworkMessage:
   #Represents a message sent between nodes 
    __slots__ = ('msg_id', 'msg_type', 'sender', 'receiver', 'payload', 'sent_time')

    def __init__(
        self,
        msg_id: str,
        msg_type: str,
        sender: int,
        receiver: int,
        payload: Dict[str, Any],
        sent_time: float
    ):
        self.msg_id = msg_id
        self.msg_type = msg_type
        self.sender = sender
        self.receiver = receiver
        self.payload = payload
        self.sent_time = sent_time


class EventDrivenSimulator:
   #Main simulation engine for the distributed system 

    def __init__(self, config: Dict[str, Any], state_callback: Optional[Callable] = None):
        self.clock = 0.0
        self.event_queue: List[SimulationEvent] = []
        self.nodes: Dict[int, Nodes] = {}
        self.config = config
        self.message_drop_rate = config.get('message_drop_rate', 0.1)
        self.min_latency = config.get('min_latency', 0.1)
        self.max_latency = config.get('max_latency', 0.5)
        self.event_log: List[Dict[str, Any]] = []
        self.partitions: Dict[str, List[int]] = {}
        self.state_callback = state_callback
        self.running = False
        self.realtime = config.get('realtime', False)
        self.speed = config.get('speed', 1.0)
        self.message_counter = 0
        self.event_counter = 0
        self.simulation_id = f"sim-{int(time.time())}"

        # Initialise nodes
        self._initialise_nodes(config['node_count'])

        # Log simulation start
        self.log_event('SIMULATION_START', {
            'node_count': config['node_count'],
            'config': config
        })

    def _initialise_nodes(self, node_count: int) -> None:
       #Initialise nodes in a circular arrangement 
        node_class = self.config.get('node_class', Node)
        for i in range(node_count):
            angle = 2 * math.pi * i / node_count
            x = 300 + 200 * math.cos(angle)
            y = 300 + 200 * math.sin(angle)
            
            self.nodes[i] = node_class(str(i), self)
            self.nodes[i].position = (x, y)

    def register_node(self, node: Node) -> None:
       #Register a node with the simulation.
        
        # Args:
        #     node: Node instance to register
       
        if node.node_id not in self.nodes:
            self.nodes[int(node.node_id)] = node

    def node_exists(self, node_id: str) -> bool:
       #Check if a node exists in the simulation.
        
        # Args:
        #     node_id: ID of node to check
            
        # Returns:
        #     bool: True if node exists, False otherwise
        return int(node_id) in self.nodes

    def schedule_event(self, event: SimulationEvent) -> None:
       #Schedule an event for future processing.
        
        # Args:
        #     event: SimulationEvent to schedule
        heapq.heappush(self.event_queue, event)

    def log_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
       #Log an event to the simulation log.
        
        # Args:
        #     event_type: Type of event
        #     data: Event data
            
        # Returns:
        #     Dict: The logged event record

        self.event_counter += 1
        event_record = {
            'id': f"evt-{self.event_counter}",
            'time': self.clock,
            'type': event_type,
            'data': data
        }
        self.event_log.append(event_record)
        return event_record

    def generate_message_id(self) -> str:
       #Generate a unique message ID.
        
        # Returns:
        #     str: Unique message ID

        self.message_counter += 1
        return f"msg-{self.message_counter}-{int(time.time())}"

    def send_message(self, message: NetworkMessage) -> None:
       #Send a message with potential delay or drop.
        
        # Args:
        #     message: NetworkMessage to send

        if random.random() < self.message_drop_rate:
            self.log_event('MESSAGE_DROP', {
                'message_id': message.msg_id,
                'from': message.sender,
                'to': message.receiver,
                'type': message.msg_type
            })
            return

        latency = random.uniform(self.min_latency, self.max_latency)
        delivery_time = self.clock + latency

        self.schedule_event(SimulationEvent(
            event_type='MESSAGE_DELIVER',
            timestamp=delivery_time,
            data={'message': message}
        ))

        self.log_event('MESSAGE_SEND', {
            'message_id': message.msg_id,
            'from': message.sender,
            'to': message.receiver,
            'type': message.msg_type,
            'scheduled_delivery': delivery_time
        })

    def process_event(self, event: SimulationEvent) -> None:
       #Process a simulation event.
        
    #     Args:
    #         event: SimulationEvent to process

        handler_name = f"handle_{event.event_type.lower()}"
        if hasattr(self, handler_name):
            getattr(self, handler_name)(event)
        elif event.callback:
            event.callback(event)
        else:
            logger.warning(f"No handler for event type: {event.event_type}")

    def handle_node_crash(self, event: SimulationEvent) -> None:
       #Handle node crash event.
        
        # Args:
        #     event: Crash event to process

        node_id = event.data['node_id']
        node = self.nodes[node_id]
        if node.is_alive():
            node.crash()
            self.log_event('STATE_CHANGE', {
                'node_id': node_id,
                'new_state': 'down'
            })
    
    def handle_node_recover(self, event: SimulationEvent) -> None:
       #Handle node recovery event.
        
        # Args:
        #     event: Recovery event to process

        node_id = event.data['node_id']
        node = self.nodes[node_id]
        if not node.is_alive():
            node.recover()
            self.log_event('STATE_CHANGE', {
                'node_id': node_id,
                'new_state': node.state
            })
    
    def handle_partition_start(self, event: SimulationEvent) -> None:
       #Handle network partition start event.
        
        # Args:
        #     event: Partition start event

        partition_id = event.data['partition_id']
        node_ids = event.data['node_ids']
        self.partitions[partition_id] = node_ids
        
        for nid in node_ids:
            node = self.nodes[nid]
            if node.is_alive():
                node.partition_group = partition_id
                if hasattr(node, 'change_state'):
                    node.change_state('partitioned', self.clock)
                self.log_event('STATE_CHANGE', {
                    'node_id': nid,
                    'new_state': 'partitioned',
                    'partition_id': partition_id
                })
    
    def handle_partition_end(self, event: SimulationEvent) -> None:
       #Handle network partition end event.
        
        # Args:
        #     event: Partition end event

        partition_id = event.data['partition_id']
        if partition_id not in self.partitions:
            return
            
        node_ids = self.partitions[partition_id]
        for nid in node_ids:
            node = self.nodes[nid]
            if node.is_alive() and getattr(node, 'partition_group', None) == partition_id:
                node.partition_group = None
                if hasattr(node, 'change_state'):
                    node.change_state('follower', self.clock)
                self.log_event('STATE_CHANGE', {
                    'node_id': nid,
                    'new_state': 'follower'
                })
        
        del self.partitions[partition_id]
    
    def handle_timeout(self, event: SimulationEvent) -> None:
       #Handle timeout event.
        
        # Args:
        #     event: Timeout event to process

        node_id = event.data['node_id']
        timeout_type = event.data['timeout_type']
        node = self.nodes[node_id]
        
        if not node.is_alive():
            return
        
        node_event = Event(
            timestamp=event.timestamp,
            event_type=EventType.TIMEOUT,
            data={
                'tag': timeout_type,
                'node_id': str(node_id)
            }
        )
        
        node.inbox.append(node_event)
        node.process_inbox()
    
    def get_current_state(self) -> Dict[str, Any]:
       #Return current simulation state as JSON-serialisable dict.
        
        # Returns:
        #     Dict: Current simulation state

        node_states = []
        for node_id, node in self.nodes.items():
            state = {
                'id': node_id,
                'state': getattr(node, 'state', 'unknown'),
                'active': node.is_alive(),
                'position': getattr(node, 'position', (0, 0)),
            }
            
            if hasattr(node, 'term'):
                state['term'] = node.term
            if hasattr(node, 'partition_group'):
                state['partition_group'] = node.partition_group
            
            node_states.append(state)

        messages_in_transit = []
        for event in self.event_queue:
            if (isinstance(event, SimulationEvent) and 
                event.event_type == 'MESSAGE_DELIVER'):
                msg = event.data['message']
                progress = (self.clock - msg.sent_time) / (event.timestamp - msg.sent_time)
                messages_in_transit.append({
                    'id': msg.msg_id,
                    'from': msg.sender,
                    'to': msg.receiver,
                    'type': msg.msg_type,
                    'sent_time': msg.sent_time,
                    'delivery_time': event.timestamp,
                    'progress': min(progress, 0.99),
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
            'events': self.event_log[-100:],
            'partitions': [
                {'id': pid, 'nodes': nodes} for pid, nodes in self.partitions.items()
            ]
        }
    
    def update_frontend(self) -> None:
       #Send current state to frontend via callback 
        if self.state_callback:
            state = self.get_current_state()
            self.state_callback(state)
    
    def run(self, max_time: float = 100.0) -> None:
       #Run the simulation until max_time is reached.
        
        # Args:
        #     max_time: Maximum simulation time to run

        self.running = True
        start_real = time.time()
        last_update = 0.0
        
        while self.running and self.event_queue and self.clock <= max_time:
            event = heapq.heappop(self.event_queue)
            self.clock = event.timestamp
            
            if self.realtime:
                elapsed_real = time.time() - start_real
                sleep_time = (self.clock - elapsed_real) / self.speed
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            self.process_event(event)
            
            if self.clock - last_update > 0.033:  # ~30 fps
                self.update_frontend()
                last_update = self.clock
        
        self.running = False
        self.log_event('SIMULATION_END', {'reason': 'completed'})
        self.update_frontend()
    
    def pause(self) -> None:
       #Pause the simulation 
        self.running = False
    
    def resume(self) -> None:
       #Resume a paused simulation 
        if not self.running:
            self.running = True
            self.run()
    
    def step(self) -> None:
       #Execute the next event 
        if self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.clock = event.timestamp
            self.process_event(event)
            self.update_frontend()
    
    def inject_message(self, sender: int, receiver: int, msg_type: str, payload: Dict[str, Any]) -> None:
       #Inject a custom message into the system.
        
        # Args:
        #     sender: Sender node ID
        #     receiver: Receiver node ID
        #     msg_type: Message type
        #     payload: Message payload

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
    
    def inject_failure(self, failure_type: str, **kwargs) -> None:
       #Inject a failure into the system.
        
        # Args:
        #     failure_type: Type of failure ('crash' or 'partition')
        #     **kwargs: Additional failure parameters

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


class SimulationServer:
   #WebSocket server for simulation visualisation 
    
    def __init__(self, config: Dict[str, Any]):
        self.simulator = EventDrivenSimulator(config, self.state_callback)
        self.clients: Set[Any] = set()
        
    def state_callback(self, state: Dict[str, Any]) -> None:
       #Broadcast state updates to all connected clients.
        
        # Args:
        #     state: Current simulation state

        message = json.dumps({'type': 'state_update', 'data': state})
        for client in self.clients:
            client.send(message)
    
    def add_client(self, client: Any) -> None:
       #Add a new client to the server.
        
        # Args:
        #     client: Client connection to add

        self.clients.add(client)
        client.send(json.dumps({
            'type': 'full_state',
            'data': self.simulator.get_current_state()
        }))
    
    def remove_client(self, client: Any) -> None:
       #Remove a client from the server.
        
        # Args:
        #     client: Client connection to remove
        self.clients.discard(client)


if __name__ == "__main__":
    config = {
        'node_count': 5,
        'message_drop_rate': 0.2,
        'min_latency': 0.1,
        'max_latency': 0.5,
        'realtime': False
    }
    
    sim = EventDrivenSimulator(config)
    sim.inject_failure('crash', node_id=1, recovery_time=10)
    sim.inject_failure('partition', node_ids=[0,1], duration=15)
    sim.run(max_time=30)
    print(json.dumps(sim.get_current_state(), indent=2))