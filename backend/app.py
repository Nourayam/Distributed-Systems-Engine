#This is the RAFT Distributed Systems Simulator - Backend

import sys
import os
import traceback
from typing import Dict, Any, Optional, List
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time
import random
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

# configuring logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('raft_simulator.log')
    ]
)
logger = logging.getLogger(__name__)

class NodeState(Enum):
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"
    LEADER = "LEADER"

class ChaosType(Enum):
    KILL_NODE = "KILL_NODE"
    PARTITION = "PARTITION"
    RESTORE_ALL = "RESTORE_ALL"
    NETWORK_DELAY = "NETWORK_DELAY"

@dataclass
class SimulationState:
    #Thread-safe simulation state management
    simulation: Optional[Any] = None
    thread: Optional[threading.Thread] = None
    is_running: bool = False
    start_time: float = 0
    events: List[Dict[str, Any]] = field(default_factory=list)
    current_time: float = 0
    node_count: int = 5
    last_heartbeat: float = 0
    animation_speed: float = 1.0  # Speed multiplier for animations

class RaftNode:
    #has timing and state transitions
    def __init__(self, node_id: str, simulation=None):
        self.id = node_id
        self.state = "FOLLOWER"
        self.term = 0
        self.alive = True
        self.last_heartbeat = time.time()
        self.simulation = simulation
        
        #timing controls
        self.last_state_change = time.time()
        self.election_timeout = random.uniform(3, 6)  # made 3-6 seconds for visibility
        self.heartbeat_interval = 1.0  # 1 second heartbeats
        self.state_transition_delay = 0.5  # minimum delay between state changes
        
        #visual state tracking
        self.is_transitioning = False
        self.transition_start_time = 0
        
    def get_state_info(self) -> Dict[str, Any]:
        #get the current node state information with data
        try:
            current_time = time.time()
            
            #this checks for natural state transitions with proper timing
            if self.alive and current_time - self.last_state_change > self.state_transition_delay:
                self._maybe_transition(current_time)
            
            return {
                'state': self.state,
                'current_term': self.term,
                'id': self.id,
                'alive': self.alive,
                'last_heartbeat': self.last_heartbeat,
                'is_transitioning': self.is_transitioning,
                'time_since_last_heartbeat': current_time - self.last_heartbeat,
                'election_timeout': self.election_timeout
            }
        except Exception as e:
            logger.error(f"Error getting state info for node {self.id}: {e}")
            return {
                'state': 'FOLLOWER',  # Default to FOLLOWER, not UNKNOWN
                'current_term': 0,
                'id': self.id,
                'alive': False,
                'last_heartbeat': 0,
                'is_transitioning': False
            }
    
    def _maybe_transition(self, current_time: float):
        #simulate realistic RAFT state transitions with the right timing
        if not self.alive:
            return
            
        time_since_last_change = current_time - self.last_state_change
        
        if self.state == "FOLLOWER":
            #if no heartbeat received within timeout then start election. this is when one goes yellow
            if current_time - self.last_heartbeat > self.election_timeout:
                self._start_transition("CANDIDATE")
                self.term += 1
                logger.info(f"Node {self.id} became CANDIDATE in term {self.term}")
                
        elif self.state == "CANDIDATE":
            #election duration (2-4 seconds)
            if time_since_last_change > random.uniform(2, 4):
                # 60% chance to become leader, 40% to go back to follower
                if random.random() < 0.6:
                    self._start_transition("LEADER")
                    logger.info(f"Node {self.id} became LEADER in term {self.term}")
                else:
                    self._start_transition("FOLLOWER")
                    logger.info(f"Node {self.id} failed election, back to FOLLOWER")
                    
        elif self.state == "LEADER":
            #the leader will occasionally step down or crash
            if time_since_last_change > 8 and random.random() < 0.05:  # 5% chance every 8+ seconds
                self._start_transition("FOLLOWER")
                logger.info(f"Node {self.id} stepped down from LEADER")
    
    def _start_transition(self, new_state: str):
        #state transition with visual feedback
        self.state = new_state
        self.last_state_change = time.time()
        self.is_transitioning = True
        self.transition_start_time = time.time()
        
        #transition flag after animation duration
        threading.Timer(1.0, self._clear_transition).start()
        
        #update heartbeat for new state
        if new_state == "LEADER":
            self.last_heartbeat = time.time()
    
    def _clear_transition(self):
        #clear transition flag after animation
        self.is_transitioning = False
    
    def is_alive(self) -> bool:
        return self.alive
    
    def recover(self):
        #failed node state reset
        self.alive = True
        self.state = "FOLLOWER"
        self.last_heartbeat = time.time()
        self.last_state_change = time.time()
        self.election_timeout = random.uniform(3, 6)
        self._start_transition("FOLLOWER")
        logger.info(f"Node {self.id} recovered")
    
    def kill(self):
        #kill node with state cleanup
        self.alive = False
        self.is_transitioning = False
        logger.info(f"Node {self.id} killed")
    
    def send_heartbeat(self):
        #send heartbeat as leader
        if self.state == "LEADER" and self.alive:
            self.last_heartbeat = time.time()
            return True
        return False

class Simulation:
    def __init__(self, config=None):
        self.config = config or {}
        self.nodes: Dict[str, RaftNode] = {}
        self.current_time = 0
        self.running = False
        self.start_time = time.time()
        self.messages = []
        self.lock = threading.Lock()
        self.step_interval = 0.5  # 500ms steps for smooth animation
        
    def add_node(self, node_id: str) -> RaftNode:
        #add node to simulation
        with self.lock:
            node = RaftNode(node_id, self)
            self.nodes[node_id] = node
            logger.info(f"Added node {node_id} to simulation")
            return node
    
    def run(self, max_time: float = 60):
        #run simulation with pacing
        try:
            self.running = True
            self.start_time = time.time()
            logger.info(f"Starting simulation for {max_time} seconds with {self.step_interval}s steps")
            
            while self.running and (time.time() - self.start_time) < max_time:
                self.current_time = time.time() - self.start_time
                self._simulation_step()
                
                #controlled timing for observable changes since i had an issue of everything happening in like 2 seconds
                time.sleep(self.step_interval)
                
        except Exception as e:
            logger.error(f"Simulation error: {e}")
            logger.error(traceback.format_exc())
        finally:
            self.running = False
            logger.info("Simulation ended")
    
    def _simulation_step(self):
        #message generation
        with self.lock:
            current_time = time.time()
            
            #find current leader
            leader_nodes = [n for n in self.nodes.values() if n.state == "LEADER" and n.alive]
            
            if leader_nodes:
                leader = leader_nodes[0]
                # Leader sends heartbeats to all followers
                for node in self.nodes.values():
                    if node.id != leader.id and node.alive:
                        # Send heartbeat with visual delay
                        self.messages.append({
                            'from': int(leader.id),
                            'to': int(node.id),
                            'type': 'HEARTBEAT',
                            'timestamp': current_time,
                            'travel_time': 0.8  # 800ms travel time for visibility
                        })
                        
                        # Update follower's last heartbeat
                        node.last_heartbeat = current_time
                        
                #leader heartbeat
                leader.send_heartbeat()
            
            #generate vote messages for candidates
            candidate_nodes = [n for n in self.nodes.values() if n.state == "CANDIDATE" and n.alive]
            for candidate in candidate_nodes:
                for node in self.nodes.values():
                    if node.id != candidate.id and node.alive and random.random() < 0.3:
                        self.messages.append({
                            'from': int(candidate.id),
                            'to': int(node.id),
                            'type': 'VOTE_REQUEST',
                            'timestamp': current_time,
                            'travel_time': 0.6
                        })
            
            #clean old messages (keep for animation duration)
            self.messages = [m for m in self.messages if current_time - m['timestamp'] < 3.0]
    
    def inject_failure(self, failure_type: str, node_id: str = None, recovery_time: float = 10.0):
        #inject a failure into the simulation
        try:
            with self.lock:
                if failure_type == 'crash' and node_id and node_id in self.nodes:
                    self.nodes[node_id].kill()
                    
                    # Schedule recovery with proper timing
                    def recover_node():
                        time.sleep(recovery_time)
                        with self.lock:
                            if node_id in self.nodes:
                                self.nodes[node_id].recover()
                    
                    recovery_thread = threading.Thread(target=recover_node, daemon=True)
                    recovery_thread.start()
                    
                    logger.info(f"Injected {failure_type} failure for node {node_id}")
                    
        except Exception as e:
            logger.error(f"Error injecting failure: {e}")

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Global simulation state
sim_state = SimulationState()
sim_lock = threading.RLock()

def safe_log_event(event_type: str, message: str) -> None:
    #thread-safe event logging
    try:
        with sim_lock:
            event = {
                'timestamp': sim_state.current_time,
                'type': event_type,
                'message': message,
                'real_time': datetime.now().isoformat()
            }
            sim_state.events.append(event)
            
            #keep only last 1000 events so we're not having a spam or memory ish
            if len(sim_state.events) > 1000:
                sim_state.events = sim_state.events[-1000:]
                
            logger.info(f"Event logged: {event_type} - {message}")
    except Exception as e:
        logger.error(f"Error logging event: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    #health check endpoint
    try:
        with sim_lock:
            health_data = {
                'status': 'healthy',
                'service': 'raft-simulator',
                'version': '2.0.0',
                'timestamp': datetime.now().isoformat(),
                'simulation_running': sim_state.is_running,
                'node_count': len(sim_state.simulation.nodes) if sim_state.simulation else 0,
                'uptime': time.time() - sim_state.start_time if sim_state.start_time else 0
            }
        return jsonify(health_data)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/raft/status', methods=['GET'])
def get_raft_status():
    #get current RAFT cluster status with enhanced information
    try:
        with sim_lock:
            sim_state.last_heartbeat = time.time()
            
            if sim_state.simulation and hasattr(sim_state.simulation, 'nodes') and sim_state.simulation.nodes:
                nodes_data = []
                leader_id = None
                current_term = 0
                messages = []
                
                #collect enhanced node states
                for node_id, node in sim_state.simulation.nodes.items():
                    try:
                        info = node.get_state_info()
                        node_data = {
                            "id": int(node_id),
                            "state": info.get('state', 'FOLLOWER'),  #default to FOLLOWER
                            "term": info.get('current_term', 0),
                            "status": "HEALTHY" if info.get('alive', False) else "FAILED",
                            "is_transitioning": info.get('is_transitioning', False),
                            "time_since_last_heartbeat": info.get('time_since_last_heartbeat', 0)
                        }
                        nodes_data.append(node_data)
                        
                        #find leader
                        if info.get('state') == 'LEADER' and info.get('alive', False):
                            leader_id = int(node_id)
                            current_term = info.get('current_term', 0)
                            
                    except Exception as e:
                        logger.error(f"Error getting node {node_id} state: {e}")
                        #fallback node data
                        nodes_data.append({
                            "id": int(node_id),
                            "state": "FOLLOWER",
                            "term": 0,
                            "status": "FAILED",
                            "is_transitioning": False
                        })
                
                #get messages with info
                if hasattr(sim_state.simulation, 'messages'):
                    messages = sim_state.simulation.messages[-20:]  #last 20 messages, don't neeed spam
                
                #update current time
                sim_state.current_time = getattr(sim_state.simulation, 'current_time', 0)
                
                return jsonify({
                    "nodes": nodes_data,
                    "leader": leader_id,
                    "term": current_term,
                    "simulation_time": sim_state.current_time,
                    "running": sim_state.is_running,
                    "messages": messages,
                    "events": sim_state.events[-50:],
                    "heartbeat": sim_state.last_heartbeat,
                    "animation_speed": sim_state.animation_speed
                })
            else:
                # Return default state
                return jsonify({
                    "nodes": [
                        {"id": i, "state": "FOLLOWER", "term": 0, "status": "HEALTHY", "is_transitioning": False}
                        for i in range(sim_state.node_count)
                    ],
                    "leader": None,
                    "term": 0,
                    "simulation_time": 0.0,
                    "running": False,
                    "messages": [],
                    "events": [],
                    "heartbeat": time.time(),
                    "animation_speed": 1.0
                })
                
    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        return jsonify({
            "nodes": [],
            "leader": None,
            "term": 0,
            "simulation_time": 0.0,
            "running": False,
            "messages": [],
            "events": [],
            "error": str(e)
        }), 500

@app.route('/raft/start', methods=['POST'])
def start_simulation():
    #start simulation with parameters
    try:
        params = request.get_json() or {}
        node_count = min(max(params.get('nodeCount', 5), 3), 7)
        max_time = min(max(params.get('maxTime', 60), 10), 300)
        animation_speed = min(max(params.get('animationSpeed', 1.0), 0.5), 3.0)
        
        with sim_lock:
            # Stop existing simulation
            if sim_state.is_running:
                sim_state.is_running = False
                if sim_state.thread and sim_state.thread.is_alive():
                    sim_state.thread.join(timeout=3.0)
            
            #create simulation
            sim_state.simulation = Simulation()
            sim_state.events = []
            sim_state.start_time = time.time()
            sim_state.current_time = 0
            sim_state.node_count = node_count
            sim_state.animation_speed = animation_speed
            
            #adjust simulation timing based on animation speed
            sim_state.simulation.step_interval = 0.5 / animation_speed
            
            #create the nodes
            for i in range(node_count):
                sim_state.simulation.add_node(str(i))
            
            safe_log_event('SYSTEM', f'Simulation started with {node_count} nodes')
            
            #start the simulation thread
            def run_simulation_thread():
                try:
                    sim_state.is_running = True
                    logger.info(f"Starting simulation thread for {max_time} seconds")
                    sim_state.simulation.run(max_time=max_time)
                except Exception as e:
                    logger.error(f"Simulation thread error: {e}")
                    safe_log_event('ERROR', f'Simulation error: {str(e)}')
                finally:
                    with sim_lock:
                        sim_state.is_running = False
                        safe_log_event('SYSTEM', 'Simulation ended')
            
            sim_state.thread = threading.Thread(target=run_simulation_thread, daemon=True)
            sim_state.thread.start()
            
            return jsonify({
                'status': 'success',
                'message': f'Simulation started with {node_count} nodes',
                'params': {
                    'nodeCount': node_count,
                    'maxTime': max_time,
                    'animationSpeed': animation_speed
                }
            })
            
    except Exception as e:
        logger.error(f"Start simulation error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to start simulation: {str(e)}'
        }), 500

@app.route('/raft/stop', methods=['POST'])
def stop_simulation():
    try:
        with sim_lock:
            if sim_state.is_running:
                sim_state.is_running = False
                safe_log_event('SYSTEM', 'Simulation stopped by user')
                return jsonify({'status': 'success', 'message': 'Simulation stopped'})
            else:
                return jsonify({'status': 'warning', 'message': 'No simulation running'})
    except Exception as e:
        logger.error(f"Stop simulation error: {e}")
        return jsonify({'status': 'error', 'message': f'Failed to stop simulation: {str(e)}'})

@app.route('/raft/chaos', methods=['POST'])
def inject_chaos():
    #inject chaos events
    try:
        if not sim_state.simulation:
            return jsonify({'status': 'error', 'message': 'No simulation running'}), 400
        
        chaos_data = request.get_json() or {}
        chaos_type = chaos_data.get('type')
        node_id = chaos_data.get('nodeId')
        
        with sim_lock:
            if chaos_type == ChaosType.KILL_NODE.value:
                if node_id is not None:
                    sim_state.simulation.inject_failure('crash', node_id=str(node_id), recovery_time=15.0)
                    safe_log_event('CHAOS', f'Node {node_id} crashed')
                else:
                    #kill a random node
                    alive_nodes = [n for n, node in sim_state.simulation.nodes.items() if node.is_alive()]
                    if alive_nodes:
                        target = random.choice(alive_nodes)
                        sim_state.simulation.inject_failure('crash', node_id=target, recovery_time=15.0)
                        safe_log_event('CHAOS', f'Node {target} crashed (random)')
                        
            elif chaos_type == ChaosType.RESTORE_ALL.value:
                #restore all nodes
                for node_id, node in sim_state.simulation.nodes.items():
                    if not node.is_alive():
                        node.recover()
                        safe_log_event('RECOVERY', f'Node {node_id} recovered')
        
        return jsonify({'status': 'success', 'type': chaos_type})
        
    except Exception as e:
        logger.error(f"Chaos injection error: {e}")
        return jsonify({'status': 'error', 'message': f'Failed to inject chaos: {str(e)}'})

@app.after_request
def after_request(response):
#Add CORS headers
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    print("🚀 Starting Enhanced RAFT Distributed Systems Simulator...")
    print("📡 API available at: http://localhost:5000")
    print("🎥 Enhanced with proper timing and animations")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)