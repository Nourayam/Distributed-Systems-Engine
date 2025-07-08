import sys
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time
import random

sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from simulation.simulation import Simulation
from nodes.raft_node import RaftNode

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global simulation state
simulation = None
simulation_thread = None
simulation_running = False

@app.route('/health')
def health_check():
    return jsonify({'status': 'ok'})

@app.route('/raft/status')
def get_raft_status():
    global simulation
    
    if simulation and simulation.nodes:
        # Get real data from simulation
        nodes_data = []
        leader_id = None
        current_term = 0
        
        for node_id, node in simulation.nodes.items():
            if hasattr(node, 'get_state_info'):
                info = node.get_state_info()
                nodes_data.append({
                    "id": int(node_id),
                    "state": info['state'],
                    "term": info['current_term']
                })
                
                if info['state'] == 'LEADER':
                    leader_id = int(node_id)
                    current_term = info['current_term']
        
        return jsonify({
            "nodes": nodes_data,
            "leader": leader_id,
            "term": max([n['term'] for n in nodes_data]) if nodes_data else 0,
            "simulation_time": simulation.current_time,
            "running": simulation_running
        })
    else:
        # Return dummy data if simulation not running
        return jsonify({
            "nodes": [
                {"id": 0, "state": "FOLLOWER", "term": 1},
                {"id": 1, "state": "FOLLOWER", "term": 1},
                {"id": 2, "state": "LEADER", "term": 1},
                {"id": 3, "state": "FOLLOWER", "term": 1},
                {"id": 4, "state": "FOLLOWER", "term": 1}
            ],
            "leader": 2,
            "term": 1,
            "simulation_time": 0.0,
            "running": False
        })

@app.route('/raft/start', methods=['POST'])
def start_simulation():
    global simulation, simulation_thread, simulation_running
    
    try:
        # Get parameters from request
        params = request.json or {}
        node_count = params.get('nodeCount', 5)
        max_time = params.get('maxTime', 60)
        message_drop_rate = params.get('messageDropRate', 0.1)
        
        # Stop existing simulation
        if simulation_running:
            simulation_running = False
            if simulation_thread:
                simulation_thread.join(timeout=1.0)
        
        # Create new simulation
        config = Config()
        config.node_count = node_count
        config.message_drop_rate = message_drop_rate
        
        simulation = Simulation(config)
        
        # Create RAFT nodes
        for i in range(node_count):
            RaftNode(str(i), simulation)
        
        # Start simulation in background thread
        def run_simulation():
            global simulation_running
            simulation_running = True
            try:
                simulation.run(max_time=max_time)
            except Exception as e:
                print(f"Simulation error: {e}")
            finally:
                simulation_running = False
        
        simulation_thread = threading.Thread(target=run_simulation)
        simulation_thread.daemon = True
        simulation_thread.start()
        
        return jsonify({'status': 'started', 'message': 'Simulation started successfully'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/raft/stop', methods=['POST'])
def stop_simulation():
    global simulation_running
    simulation_running = False
    return jsonify({'status': 'stopped', 'message': 'Simulation stopped'})

@app.route('/raft/reset', methods=['POST'])
def reset_simulation():
    global simulation, simulation_running
    simulation_running = False
    simulation = None
    return jsonify({'status': 'reset', 'message': 'Simulation reset'})

@app.route('/raft/chaos', methods=['POST'])
def inject_chaos():
    global simulation
    
    if not simulation:
        return jsonify({'status': 'error', 'message': 'No simulation running'}), 400
    
    try:
        chaos_data = request.json or {}
        chaos_type = chaos_data.get('type')
        node_id = chaos_data.get('nodeId')
        
        if chaos_type == 'KILL_NODE' and node_id is not None:
            simulation.inject_failure('crash', node_id=str(node_id), recovery_time=10.0)
        elif chaos_type == 'RESTORE_ALL':
            # Restore all nodes (simplified)
            for node in simulation.nodes.values():
                if not node.is_alive():
                    node.recover()
        
        return jsonify({'status': 'chaos_injected', 'type': chaos_type})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting RAFT Simulator Backend...")
    print("📡 API will be available at: http://localhost:5000")
    print("🔗 Frontend should connect to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)