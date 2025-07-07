from flask import Flask, jsonify
from simulator.simulation.simulation import Simulation  # Adjust as needed

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({'status': 'ok'})

# Example: just return static RAFT state for now
@app.route('/raft/status')
def get_raft_status():
    dummy_data = {
        "nodes": [
            {"id": 0, "state": "FOLLOWER", "term": 5},
            {"id": 1, "state": "FOLLOWER", "term": 5},
            {"id": 2, "state": "LEADER",   "term": 5},
            {"id": 3, "state": "FOLLOWER", "term": 5},
            {"id": 4, "state": "FOLLOWER", "term": 5}
        ],
        "leader": 2,
        "term": 5
    }
    return jsonify(dummy_data)

if __name__ == '__main__':
    app.run(debug=True)
