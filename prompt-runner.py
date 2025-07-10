# import os
# import requests

# # === 🔐 Configuration ===
# API_KEY = "sk-1d543ab9361542a4a0596e6b85fc715e"
# MODEL = "deepseek-chat"
# ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

# # === 🗂️ Project Files to Submit ===
# INPUT_FILES = [
#     "src/index.css",

# ]


# OUTPUT_FILE = "hmmm.txt"

# # === 📦 Load Code from Files ===
# def load_files(file_paths):
#     combined = ""
#     for path in file_paths:
#         if not os.path.exists(path):
#             print(f"⚠️ Skipping missing file: {path}")
#             continue
#         with open(path, "r", encoding="utf-8") as f:
#             combined += f"\n# ==== FILE: {path} ====\n"
#             combined += f.read() + "\n"
#     return combined

# code_context = load_files(INPUT_FILES)

# # === ✍️ Custom Refactoring Prompt ===
# refactor_prompt = f"""
# You are an expert software engineer reviewing a multi-file Python project built for distributed system simulation.
# Build a frontend React dashboard for a Flask-based distributed systems simulator called RAFT DSS (Distributed Systems Simulator). The simulator is a production-grade Python implementation of the RAFT consensus algorithm, capable of leader election, log replication, network partition simulation, and failure injection.
# The backend exposes REST endpoints like:
# GET /raft/status — returns current simulation state (nodes, terms, roles, etc.)
# GET /raft/events — returns or streams log of events
# POST /raft/start — starts a simulation run
# (Optional) WebSocket for real-time logs or visual updates
# Build a visually compelling, responsive React frontend with the goal of presenting RAFT mechanics in an educational, engineering-grade, and interactive way.

# 🎯 Features & Functional Goals
# 1. Cluster Visualisation (Canvas View)
# Visualise 3–7 nodes as circles in a ring or cluster layout

# Each node shows:
# Node ID
# Role (FOLLOWER, CANDIDATE, LEADER)
# Current term
# Leader visually stands out (gold glow or icon 👑)
# Failed or partitioned nodes gray out or pulse
# Animated messages (heartbeats, votes) as arrows between nodes
# 2. Event Timeline View
# Real-time event log panel (sidebar or bottom panel)
# Scrollable, readable log like:
# [01.2s] Node 3 became CANDIDATE (term 4)  
# [01.6s] Node 3 won election (term 4)  
# [03.3s] Partition between Node 2 and Node 0  
# Filterable by event type (election, replication, chaos)

# 3. Control Panel
# Start / Stop / Reset simulation

# Set parameters before run:

# Number of nodes

# Max time

# Message drop rate

# Buttons to inject chaos:

# Kill Node

# Partition Link

# Restore Node

# ⚙️ Suggested Component Structure
# <App>
# ├── <ClusterCanvas />     ← visual network map of nodes
# │   └── <Node />          ← renders a single node
# ├── <LogViewer />         ← timeline of consensus events
# ├── <ControlPanel />      ← simulation controls & chaos injection
# └── <StatusBar />         ← shows current leader, cluster term, etc.
# 🎨 Visual Design Requirements
# Theme: Dark mode preferred (suitable for engineers & researchers)

# Color roles:

# 🟢 LEADER

# 🔵 FOLLOWER

# 🟡 CANDIDATE

# 🔴 FAILED

# Smooth UI transitions (React Spring, Framer Motion, or CSS animations)

# Tooltips or modals on hover (node logs, metrics, election history)

# Responsive layout for 13"–15" laptop screens

# 🔌 Integration Details
# Connect to Flask backend via Axios or fetch

# Base URL from .env variable: REACT_APP_API_URL=http://localhost:5000

# You may use mock data to simulate Flask responses during development

# Feel free to use Tailwind, CSS Modules, or styled components

# 🧪 Bonus Suggestions (Use Your Judgement)
# You may invent or include other features you believe improve:

# Simulation observability

# Frontend responsiveness / clarity

# Debugging friendliness for engineers

# Educational insight into consensus under failure

# For example:

# Simulation playback or scrubbing

# Log compaction visualiser per node

# Split-brain animation mode

# Exportable timeline logs

# “Node health” dashboard with metrics

# ✳️ Don’t hesitate to add micro-interactions, polish, or thoughtful visual cues that make the dashboard feel like something from a distributed systems engineer’s toolkit — even if those features weren’t explicitly requested.

# 📦 Tech Stack Expectations
# React (Hooks preferred)

# Axios or fetch

# CSS Modules, TailwindCSS, or similar

# D3.js or SVG/canvas for message paths (optional)

# No Redux required — use Context or component state

# ✅ Final result should be a clean, component-based React app inside /frontend with mocked or real Flask connections that renders a live RAFT simulation dashboard.

# Below is the complete codebase. Reply with the fully updated and polished versions of **only** the files that were changed. Use clear `# ==== FILE: path ====` markers to segment your response.

# {code_context}
# """

# # === 📬 Compose Request Payload ===
# payload = {
#     "model": MODEL,
#     "temperature": 0.2,
#     "messages": [
#         {
#             "role": "system",
#             "content": (
#                 "You are a helpful assistant that always responds in English and returns clean, production-quality Python."
#             )
#         },
#         {
#             "role": "user",
#             "content": refactor_prompt
#         }
#     ]
# }

# headers = {
#     "Authorization": f"Bearer {API_KEY}",
#     "Content-Type": "application/json"
# }

# # === 🚀 Send Request to DeepSeek ===
# print("📡 Sending full project context to DeepSeek...\n")
# response = requests.post(ENDPOINT, headers=headers, json=payload)

# # === 📥 Handle the Response ===
# if response.status_code == 200:
#     result_text = response.json()["choices"][0]["message"]["content"]
    
#     print("✅ DeepSeek responded with proposed changes!\n")
#     print(result_text[:1000] + "\n...")  # Preview first 1000 characters

#     with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
#         out.write(result_text)
#     print(f"📁 Saved full response to: {OUTPUT_FILE}")

# else:
#     print(f"❌ DeepSeek API Error {response.status_code}:\n")
#     print(response.text)







# You're playing the role of a senior software developer refining an interactive distributed systems simulator. The system is built and running without errors. I want you to fully review, refactor, and optimize both the backend and frontend codebase for readability, maintainability, performance, and visual clarity.

# The frontend is built in React, with a canvas-based cluster visualization. The backend is a Flask service returning live status for RAFT-like node simulation. Your task is to bring it to production-grade quality and ensure it matches the spec below.

# You are free to improve styling, structure, component modularity, and simulation features where necessary — always keeping extensibility and clarity in mind.

# 🧭 Project Specification
# Project Name: RAFT DSS Summary: An educational dashboard and message simulator that visually represents distributed consensus and system state in real time.

# Purpose: To help engineers, students, and system designers explore fault tolerance, leader election, and event-driven architecture.

# Tech Stack:

# Layer	Tools
# Frontend UI	React (JavaScript), Canvas or SVG
# Backend Logic	Flask (Python), Flask-CORS
# Messaging Sim	Custom polling (optional future: WebSocket)
# Dev Tools	Git, VSCode, Postman
# Required MVP Features:

# ⬤ Node ring visualization with clear state and ID

# ⬤ Status bar showing leader ID and term

# ⬤ Chaos control panel (start/stop/reset/failure triggers)

# ⬤ Message arrows between nodes with animation

# ⬤ Scrollable log viewer with live events

# ✨ Stretch Goals:

# Replayable timeline

# Drop/latency simulation

# Configurable node count and message behavior

# Snapshot graph of node states over time

# 🎨 Styling Requests
# Increase default text size slightly — the layout is spacious and has limited content.

# Apply a cohesive dark theme across canvas and controls.

# Animate glowing outlines for leader nodes, dashed message lines with pulse effects.

# Hover effects and tooltips for nodes are welcome.

# Responsive layout for different screen sizes.

# Visually balance dashboard sections: status bar, controls, canvas, log viewer.

# 📁 Folder Structure
# plaintext
# DSS/
# ├── backend/
# │   ├── app.py
# │   ├── requirements.txt
# │   └── simulation/
# │       └── engine.py  # optional
# ├── frontend/
# │   ├── .env
# │   ├── package.json
# │   └── src/
# │       ├── index.js
# │       ├── App.js
# │       ├── StatusBar.jsx
# │       ├── index.css
# │       └── components/
# │           ├── ClusterCanvas.jsx
# │           ├── Node.jsx
# │           ├── ControlPanel.jsx
# │           └── LogViewer.jsx
# 📦 Your Task
# ✅ Refactor all code for modular clarity, style consistency, and extensibility.

# ✅ Ensure feature completeness against the spec above.

# ✅ Improve visuals (layout, animations, responsiveness, make the text slightly larger since the page is big but kinda empty).

# ✅ Address missing pieces (e.g. chaos simulation hooks, message fade-in/out).

# ✅ Suggest and implement improvements where helpful — even beyond the brief.
# oh and make sure the spelling is british


# Here are the relevant files

# // File: backend/app.py
# import sys
# import os
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# import threading
# import time
# import random



# sys.path.insert(0, os.path.dirname(__file__))

# from config import Config
# from simulation.simulation import Simulation
# from nodes.raft_node import RaftNode

# app = Flask(__name__)
# CORS(app)  # Enable CORS for React frontend

# # Global simulation state
# simulation = None
# simulation_thread = None
# simulation_running = False

# @app.route('/health')
# def health_check():
#     return jsonify({'status': 'ok'})

# @app.route('/raft/status')
# def get_raft_status():
#     global simulation
    
#     if simulation and simulation.nodes:
#         # Get real data from simulation
#         nodes_data = []
#         leader_id = None
#         current_term = 0
        
#         for node_id, node in simulation.nodes.items():
#             if hasattr(node, 'get_state_info'):
#                 info = node.get_state_info()
#                 nodes_data.append({
#                     "id": int(node_id),
#                     "state": info['state'],
#                     "term": info['current_term']
#                 })
                
#                 if info['state'] == 'LEADER':
#                     leader_id = int(node_id)
#                     current_term = info['current_term']
        
#         return jsonify({
#             "nodes": nodes_data,
#             "leader": leader_id,
#             "term": max([n['term'] for n in nodes_data]) if nodes_data else 0,
#             "simulation_time": simulation.current_time,
#             "running": simulation_running
#         })
#     else:
#         # Return dummy data if simulation not running
#         return jsonify({
#             "nodes": [
#                 {"id": 0, "state": "FOLLOWER", "term": 1},
#                 {"id": 1, "state": "FOLLOWER", "term": 1},
#                 {"id": 2, "state": "LEADER", "term": 1},
#                 {"id": 3, "state": "FOLLOWER", "term": 1},
#                 {"id": 4, "state": "FOLLOWER", "term": 1}
#             ],
#             "leader": 2,
#             "term": 1,
#             "simulation_time": 0.0,
#             "running": False
#         })

# @app.route('/raft/start', methods=['POST'])
# def start_simulation():
#     global simulation, simulation_thread, simulation_running
    
#     try:
#         # Get parameters from request
#         params = request.json or {}
#         node_count = params.get('nodeCount', 5)
#         max_time = params.get('maxTime', 60)
#         message_drop_rate = params.get('messageDropRate', 0.1)
        
#         # Stop existing simulation
#         if simulation_running:
#             simulation_running = False
#             if simulation_thread:
#                 simulation_thread.join(timeout=1.0)
        
#         # Create new simulation
#         config = Config()
#         config.node_count = node_count
#         config.message_drop_rate = message_drop_rate
        
#         simulation = Simulation(config)
        
#         # Create RAFT nodes
#         for i in range(node_count):
#             RaftNode(str(i), simulation)
        
#         # Start simulation in background thread
#         def run_simulation():
#             global simulation_running
#             simulation_running = True
#             try:
#                 simulation.run(max_time=max_time)
#             except Exception as e:
#                 print(f"Simulation error: {e}")
#             finally:
#                 simulation_running = False
        
#         simulation_thread = threading.Thread(target=run_simulation)
#         simulation_thread.daemon = True
#         simulation_thread.start()
        
#         return jsonify({'status': 'started', 'message': 'Simulation started successfully'})
    
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# @app.route('/raft/stop', methods=['POST'])
# def stop_simulation():
#     global simulation_running
#     simulation_running = False
#     return jsonify({'status': 'stopped', 'message': 'Simulation stopped'})

# @app.route('/raft/reset', methods=['POST'])
# def reset_simulation():
#     global simulation, simulation_running
#     simulation_running = False
#     simulation = None
#     return jsonify({'status': 'reset', 'message': 'Simulation reset'})

# @app.route('/raft/chaos', methods=['POST'])
# def inject_chaos():
#     global simulation
    
#     if not simulation:
#         return jsonify({'status': 'error', 'message': 'No simulation running'}), 400
    
#     try:
#         chaos_data = request.json or {}
#         chaos_type = chaos_data.get('type')
#         node_id = chaos_data.get('nodeId')
        
#         if chaos_type == 'KILL_NODE' and node_id is not None:
#             simulation.inject_failure('crash', node_id=str(node_id), recovery_time=10.0)
#         elif chaos_type == 'RESTORE_ALL':
#             # Restore all nodes (simplified)
#             for node in simulation.nodes.values():
#                 if not node.is_alive():
#                     node.recover()
        
#         return jsonify({'status': 'chaos_injected', 'type': chaos_type})
    
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# if __name__ == '__main__':
#     print("🚀 Starting RAFT Simulator Backend...")
#     print("📡 API will be available at: http://localhost:5000")
#     print("🔗 Frontend should connect to: http://localhost:5000")
#     app.run(debug=True, host='0.0.0.0', port=5000)

# // File: frontend/.env
# REACT_APP_API_URL=http://localhost:5000


# // File: frontend/package.json
# {
#   "name": "raft-frontend",
#   "version": "0.1.0",
#   "private": true,
#   "dependencies": {
#     "axios": "^1.10.0",
#     "react": "^18.2.0",
#     "react-dom": "^18.2.0",
#     "react-scripts": "5.0.1",
#     "react-tooltip": "^5.24.0",
#     "web-vitals": "^5.0.3"
#   },
#   "scripts": {
#     "start": "react-scripts start",
#     "build": "react-scripts build",
#     "test": "react-scripts test",
#     "eject": "react-scripts eject"
#   },
#   "eslintConfig": {
#     "extends": [
#       "react-app",
#       "react-app/jest"
#     ]
#   },
#   "browserslist": {
#     "production": [
#       ">0.2%",
#       "not dead",
#       "not op_mini all"
#     ],
#     "development": [
#       "last 1 chrome version",
#       "last 1 firefox version",
#       "last 1 safari version"
#     ]
#   },
#   "proxy": "http://localhost:5000"
# }


# // File: frontend/src/index.js
# import React from 'react';
# import ReactDOM from 'react-dom/client';
# import './index.css';
# import App from './App';
# import reportWebVitals from './reportWebVitals';

# const root = ReactDOM.createRoot(document.getElementById('root'));
# root.render(
#   <React.StrictMode>
#     <App />
#   </React.StrictMode>
# );

# // If you want to start measuring performance in your app, pass a function
# // to log results (for example: reportWebVitals(console.log))
# // or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
# reportWebVitals();



# // File: frontend/src/index.css
# @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@300;400;500&display=swap');

# :root {
#   /* Color Palette */
#   --bg-primary: #0f0f0f;
#   --bg-secondary: #1a1a1a;
#   --bg-tertiary: #252525;
#   --bg-accent: #2d2d2d;
  
#   --text-primary: #ffffff;
#   --text-secondary: #b3b3b3;
#   --text-muted: #666666;
  
#   --leader-color: #10b981;
#   --leader-glow: #10b981;
#   --follower-color: #3b82f6;
#   --candidate-color: #f59e0b;
#   --failed-color: #ef4444;
#   --partition-color: #8b5cf6;
  
#   --success-color: #10b981;
#   --warning-color: #f59e0b;
#   --danger-color: #ef4444;
#   --info-color: #3b82f6;
  
#   /* Spacing */
#   --spacing-xs: 0.25rem;
#   --spacing-sm: 0.5rem;
#   --spacing-md: 1rem;
#   --spacing-lg: 1.5rem;
#   --spacing-xl: 2rem;
  
#   /* Border Radius */
#   --radius-sm: 4px;
#   --radius-md: 8px;
#   --radius-lg: 12px;
  
#   /* Shadows */
#   --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
#   --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
#   --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
#   --shadow-glow: 0 0 20px;
# }

# * {
#   margin: 0;
#   padding: 0;
#   box-sizing: border-box;
# }

# body {
#   font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
#   background-color: var(--bg-primary);
#   color: var(--text-primary);
#   line-height: 1.5;
#   overflow: hidden;
# }

# #root {
#   height: 100vh;
#   display: flex;
#   flex-direction: column;
# }

# /* App Layout */
# .app-container {
#   display: flex;
#   flex-direction: column;
#   height: 100vh;
#   background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
# }

# .app-header {
#   padding: var(--spacing-md) var(--spacing-xl);
#   background-color: var(--bg-secondary);
#   border-bottom: 1px solid var(--bg-accent);
#   box-shadow: var(--shadow-md);
# }

# .app-header h1 {
#   font-size: 1.5rem;
#   font-weight: 600;
#   margin-bottom: var(--spacing-sm);
#   background: linear-gradient(90deg, var(--leader-color), var(--follower-color));
#   -webkit-background-clip: text;
#   -webkit-text-fill-color: transparent;
#   background-clip: text;
# }

# .app-main {
#   display: flex;
#   flex: 1;
#   gap: var(--spacing-md);
#   padding: var(--spacing-md);
#   overflow: hidden;
# }

# .visualization-section {
#   flex: 2;
#   display: flex;
#   flex-direction: column;
#   gap: var(--spacing-md);
#   min-width: 0;
# }

# .events-section {
#   flex: 1;
#   min-width: 320px;
#   max-width: 400px;
#   background-color: var(--bg-secondary);
#   border-radius: var(--radius-lg);
#   overflow: hidden;
#   box-shadow: var(--shadow-lg);
# }

# /* Loading and Error States */
# .app-loading {
#   display: flex;
#   flex-direction: column;
#   align-items: center;
#   justify-content: center;
#   height: 100vh;
#   background-color: var(--bg-primary);
# }

# .spinner {
#   border: 3px solid rgba(255, 255, 255, 0.1);
#   border-left-color: var(--leader-color);
#   border-radius: 50%;
#   width: 40px;
#   height: 40px;
#   animation: spin 1s linear infinite;
#   margin-bottom: var(--spacing-md);
# }

# @keyframes spin {
#   to { transform: rotate(360deg); }
# }

# .app-error {
#   padding: var(--spacing-xl);
#   color: var(--danger-color);
#   text-align: center;
#   background-color: var(--bg-primary);
#   height: 100vh;
#   display: flex;
#   flex-direction: column;
#   align-items: center;
#   justify-content: center;
# }

# .app-error button {
#   background-color: var(--bg-accent);
#   color: var(--text-primary);
#   border: none;
#   padding: var(--spacing-sm) var(--spacing-md);
#   border-radius: var(--radius-md);
#   cursor: pointer;
#   margin-top: var(--spacing-md);
#   transition: background-color 0.2s;
# }

# .app-error button:hover {
#   background-color: var(--bg-tertiary);
# }

# /* Status Bar */
# .status-bar {
#   display: flex;
#   align-items: center;
#   justify-content: space-between;
#   gap: var(--spacing-lg);
#   flex-wrap: wrap;
# }

# .status-section {
#   display: flex;
#   align-items: center;
#   gap: var(--spacing-md);
# }

# .status-item {
#   display: flex;
#   align-items: center;
#   gap: var(--spacing-xs);
#   font-size: 0.875rem;
# }

# .status-item.primary {
#   font-weight: 500;
# }

# .status-label {
#   color: var(--text-secondary);
#   font-weight: 400;
# }

# .status-value {
#   color: var(--text-primary);
#   font-weight: 500;
# }

# .status-value.running {
#   color: var(--success-color);
# }

# .status-value.stopped {
#   color: var(--danger-color);
# }

# .term-badge {
#   background-color: var(--info-color);
#   color: white;
#   padding: 2px 6px;
#   border-radius: var(--radius-sm);
#   font-size: 0.75rem;
#   font-weight: 600;
# }

# .leader-badge {
#   background-color: var(--leader-color);
#   color: white;
#   padding: 2px 6px;
#   border-radius: var(--radius-sm);
#   font-size: 0.75rem;
#   font-weight: 600;
# }

# .network-health {
#   display: flex;
#   align-items: center;
#   gap: var(--spacing-xs);
# }

# .health-dots {
#   display: flex;
#   gap: 2px;
# }

# .health-dot {
#   width: 6px;
#   height: 6px;
#   border-radius: 50%;
#   background-color: var(--text-muted);
# }

# .health-dot.healthy {
#   background-color: var(--success-color);
#   animation: pulse-dot 2s infinite;
# }

# @keyframes pulse-dot {
#   0%, 100% { opacity: 1; }
#   50% { opacity: 0.5; }
# }

# /* Cluster Canvas */
# .cluster-canvas {
#   position: relative;
#   background-color: var(--bg-secondary);
#   border-radius: var(--radius-lg);
#   overflow: hidden;
#   height: 400px;
#   box-shadow: var(--shadow-lg);
# }

# .message-canvas {
#   position: absolute;
#   top: 0;
#   left: 0;
#   width: 100%;
#   height: 100%;
#   pointer-events: none;
# }

# .cluster-info {
#   position: absolute;
#   top: var(--spacing-md);
#   left: var(--spacing-md);
#   background-color: rgba(0, 0, 0, 0.6);
#   padding: var(--spacing-sm);
#   border-radius: var(--radius-md);
#   backdrop-filter: blur(10px);
# }

# .cluster-stats {
#   display: flex;
#   gap: var(--spacing-md);
#   font-size: 0.75rem;
#   color: var(--text-secondary);
# }

# /* Node Styles */
# .node {
#   width: 80px;
#   height: 80px;
#   border-radius: 50%;
#   background-color: var(--bg-accent);
#   border: 3px solid;
#   cursor: pointer;
#   transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
#   user-select: none;
#   box-shadow: var(--shadow-md);
# }

# .node:hover {
#   transform: scale(1.1);
#   box-shadow: var(--shadow-lg);
# }

# .node-content {
#   display: flex;
#   flex-direction: column;
#   align-items: center;
#   justify-content: center;
#   height: 100%;
#   gap: 2px;
# }

# .node-emoji {
#   font-size: 1.5rem;
#   line-height: 1;
# }

# .node-id {
#   font-size: 0.75rem;
#   font-weight: 600;
#   color: var(--text-primary);
# }

# .node-term {
#   font-size: 0.625rem;
#   color: var(--text-secondary);
#   font-weight: 500;
# }

# .node-status {
#   font-size: 0.5rem;
#   color: var(--text-secondary);
#   text-transform: uppercase;
#   font-weight: 600;
#   letter-spacing: 0.5px;
# }

# /* Node States */
# .node-leader {
#   border-color: var(--leader-color);
#   background-color: rgba(16, 185, 129, 0.1);
#   box-shadow: var(--shadow-glow) var(--leader-glow);
# }

# .node-follower {
#   border-color: var(--follower-color);
#   background-color: rgba(59, 130, 246, 0.1);
# }

# .node-candidate {
#   border-color: var(--candidate-color);
#   background-color: rgba(245, 158, 11, 0.1);
#   animation: pulse 2s infinite;
# }

# .node-failed {
#   border-color: var(--failed-color);
#   background-color: rgba(239, 68, 68, 0.1);
#   opacity: 0.6;
# }

# .node-partitioned {
#   border-color: var(--partition-color);
#   background-color: rgba(139, 92, 246, 0.1);
#   border-style: dashed;
# }

# .node-transitioning {
#   animation: transition-glow 1s ease-out;
# }

# @keyframes pulse {
#   0%, 100% { 
#     transform: scale(1);
#     opacity: 1;
#   }
#   50% { 
#     transform: scale(1.05);
#     opacity: 0.9;
#   }
# }

# @keyframes transition-glow {
#   0% { box-shadow: var(--shadow-md); }
#   50% { box-shadow: var(--shadow-glow) var(--leader-glow); }
#   100% { box-shadow: var(--shadow-md); }
# }

# /* Control Panel */
# .control-panel {
#   background-color: var(--bg-secondary);
#   border-radius: var(--radius-lg);
#   padding: var(--spacing-md);
#   box-shadow: var(--shadow-lg);
# }

# .panel-header {
#   display: flex;
#   align-items: center;
#   justify-content: space-between;
#   margin-bottom: var(--spacing-md);
# }

# .panel-header h3 {
#   font-size: 1.1rem;
#   font-weight: 600;
#   color: var(--text-primary);
# }

# .expand-button {
#   background: none;
#   border: none;
#   color: var(--text-secondary);
#   cursor: pointer;
#   font-size: 1rem;
#   padding: var(--spacing-xs);
#   border-radius: var(--radius-sm);
#   transition: background-color 0.2s;
# }

# .expand-button:hover {
#   background-color: var(--bg-accent);
# }

# .panel-content {
#   margin-bottom: var(--spacing-md);
# }

# .param-group {
#   display: flex;
#   flex-direction: column;
#   gap: var(--spacing-md);
# }

# .param-label {
#   display: flex;
#   flex-direction: column;
#   gap: var(--spacing-xs);
#   font-size: 0.875rem;
#   color: var(--text-secondary);
# }

# .param-input {
#   background-color: var(--bg-accent);
#   border: 1px solid var(--bg-tertiary);
#   border-radius: var(--radius-md);
#   padding: var(--spacing-xs) var(--spacing-sm);
#   color: var(--text-primary);
#   font-size: 0.875rem;
# }

# .param-input:focus {
#   outline: none;
#   border-color: var(--leader-color);
#   box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
# }

# .range-container {
#   display: flex;
#   align-items: center;
#   gap: var(--spacing-sm);
# }

# .param-range {
#   flex: 1;
#   accent-color: var(--leader-color);
# }

# .range-value {
#   font-size: 0.75rem;
#   color: var(--text-primary);
#   font-weight: 500;
#   min-width: 30px;
# }

# .button-group {
#   display: flex;
#   gap: var(--spacing-sm);
#   margin-bottom: var(--spacing-lg);
# }

# .control-button {
#   flex: 1;
#   padding: var(--spacing-sm) var(--spacing-md);
#   border: none;
#   border-radius: var(--radius-md);
#   font-size: 0.875rem;
#   font-weight: 500;
#   cursor: pointer;
#   transition: all 0.2s;
#   display: flex;
#   align-items: center;
#   justify-content: center;
#   gap: var(--spacing-xs);
# }

# .start-button {
#   background-color: var(--success-color);
#   color: white;
# }

# .start-button:hover {
#   background-color: #059669;
# }

# .stop-button {
#   background-color: var(--danger-color);
#   color: white;
# }

# .stop-button:hover {
#   background-color: #dc2626;
# }

# .reset-button {
#   background-color: var(--bg-accent);
#   color: var(--text-primary);
#   border: 1px solid var(--bg-tertiary);
# }

# .reset-button:hover {
#   background-color: var(--bg-tertiary);
# }

# .chaos-section h4 {
#   font-size: 1rem;
#   font-weight: 600;
#   color: var(--text-primary);
#   margin-bottom: var(--spacing-sm);
# }

# .chaos-group {
#   display: flex;
#   flex-direction: column;
#   gap: var(--spacing-xs);
# }

# .chaos-button {
#   padding: var(--spacing-xs) var(--spacing-sm);
#   border: none;
#   border-radius: var(--radius-md);
#   font-size: 0.75rem;
#   font-weight: 500;
#   cursor: pointer;
#   transition: all 0.2s;
#   text-align: left;
# }

# .chaos-button.danger {
#   background-color: rgba(239, 68, 68, 0.1);
#   color: var(--danger-color);
#   border: 1px solid rgba(239, 68, 68, 0.2);
# }

# .chaos-button.warning {
#   background-color: rgba(245, 158, 11, 0.1);
#   color: var(--warning-color);
#   border: 1px solid rgba(245, 158, 11, 0.2);
# }

# .chaos-button.success {
#   background-color: rgba(16, 185, 129, 0.1);
#   color: var(--success-color);
#   border: 1px solid rgba(16, 185, 129, 0.2);
# }

# .chaos-button:hover {
#   opacity: 0.8;
#   transform: translateY(-1px);
# }

# /* Log Viewer */
# .log-viewer {
#   display: flex;
#   flex-direction: column;
#   height: 100%;
# }

# .log-header {
#   padding: var(--spacing-md);
#   border-bottom: 1px solid var(--bg-accent);
#   display: flex;
#   align-items: center;
#   justify-content: space-between;
#   gap: var(--spacing-md);
# }

# .log-header h3 {
#   font-size: 1.1rem;
#   font-weight: 600;
#   color: var(--text-primary);
# }

# .log-controls {
#   display: flex;
#   align-items: center;
#   gap: var(--spacing-sm);
# }

# .filter-select {
#   background-color: var(--bg-accent);
#   border: 1px solid var(--bg-tertiary);
#   border-radius: var(--radius-sm);
#   padding: var(--spacing-xs);
#   color: var(--text-primary);
#   font-size: 0.75rem;
# }

# .auto-scroll-toggle {
#   display: flex;
#   align-items: center;
#   gap: var(--spacing-xs);
#   font-size: 0.75rem;
#   color: var(--text-secondary);
#   cursor: pointer;
# }

# .log-container {
#   flex: 1;
#   overflow-y: auto;
#   padding: var(--spacing-sm);
#   font-family: 'Fira Code', monospace;
#   font-size: 0.75rem;
#   line-height: 1.4;
# }

# .log-empty {
#   display: flex;
#   flex-direction: column;
#   align-items: center;
#   justify-content: center;
#   height: 100%;
#   color: var(--text-muted);
#   text-align: center;
# }

# .log-entry {
#   display: flex;
#   align-items: flex-start;
#   gap: var(--spacing-xs);
#   padding: var(--spacing-xs) 0;
#   border-bottom: 1px solid rgba(255, 255, 255, 0.05);
# }

# .log-icon {
#   font-size: 0.75rem;
#   width: 20px;
#   text-align: center;
#   flex-shrink: 0;
# }

# .log-timestamp {
#   color: var(--text-muted);
#   font-weight: 500;
#   width: 60px;
#   flex-shrink: 0;
# }

# .log-message {
#   color: var(--text-secondary);
#   flex: 1;
#   word-break: break-word;
# }

# /* Log Entry Colors */
# .log-election .log-message {
#   color: var(--candidate-color);
# }

# .log-leader .log-message {
#   color: var(--leader-color);
# }

# .log-partition .log-message {
#   color: var(--partition-color);
# }

# .log-recovery .log-message {
#   color: var(--success-color);
# }

# .log-heartbeat .log-message {
#   color: var(--info-color);
# }

# .log-footer {
#   padding: var(--spacing-sm) var(--spacing-md);
#   border-top: 1px solid var(--bg-accent);
#   color: var(--text-muted);
#   font-size: 0.75rem;
# }

# /* Responsive Design */
# @media (max-width: 1024px) {
#   .app-main {
#     flex-direction: column;
#   }
  
#   .events-section {
#     min-width: auto;
#     max-width: none;
#     height: 300px;
#   }
  
#   .status-bar {
#     flex-direction: column;
#     align-items: flex-start;
#     gap: var(--spacing-sm);
#   }
# }

# @media (max-width: 768px) {
#   .app-header {
#     padding: var(--spacing-sm) var(--spacing-md);
#   }
  
#   .app-main {
#     padding: var(--spacing-sm);
#     gap: var(--spacing-sm);
#   }
  
#   .cluster-canvas {
#     height: 300px;
#   }
  
#   .node {
#     width: 60px;
#     height: 60px;
#   }
  
#   .button-group {
#     flex-direction: column;
#   }
  
#   .chaos-group {
#     grid-template-columns: 1fr;
#   }
# }

# /* Scrollbar Styling */
# ::-webkit-scrollbar {
#   width: 6px;
# }

# ::-webkit-scrollbar-track {
#   background: var(--bg-accent);
# }

# ::-webkit-scrollbar-thumb {
#   background: var(--bg-tertiary);
#   border-radius: 3px;
# }

# ::-webkit-scrollbar-thumb:hover {
#   background: #404040;
# }
# // File: frontend/src/App.js
# import React, { useState, useEffect, useCallback } from 'react';
# import axios from 'axios';
# import StatusBar from './StatusBar';
# import ClusterCanvas from './components/ClusterCanvas';
# import Node from './components/Node';
# import ControlPanel from './components/ControlPanel';
# import LogViewer from './components/LogViewer';
# import './index.css';

# const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

# const App = () => {
#   const [clusterState, setClusterState] = useState({
#     nodes: [],
#     leader: null,
#     term: 0
#   });
#   const [simulationState, setSimulationState] = useState({
#     isRunning: false,
#     time: 0,
#     events: []
#   });
#   const [messages, setMessages] = useState([]);
#   const [loading, setLoading] = useState(true);
#   const [error, setError] = useState(null);
#   const [logFilter, setLogFilter] = useState('ALL');

#   // Fetch cluster status from backend
#   const fetchClusterStatus = useCallback(async () => {
#     try {
#       const response = await axios.get(`${API_URL}/raft/status`);
#       const data = response.data;
      
#       // Transform backend data to frontend format
#       const transformedNodes = data.nodes.map(node => ({
#         id: node.id,
#         role: node.state,
#         term: node.term,
#         status: 'HEALTHY' // Default status, can be enhanced
#       }));

#       setClusterState({
#         nodes: transformedNodes,
#         leader: data.leader,
#         term: data.term
#       });

#       // Simulate some events for demonstration
#       if (simulationState.events.length === 0) {
#         setSimulationState(prev => ({
#           ...prev,
#           time: prev.time + 0.1,
#           events: [
#             { timestamp: 0.0, type: 'ELECTION', message: 'Initial leader election started' },
#             { timestamp: 1.2, type: 'LEADER_CHANGE', message: `Node ${data.leader} became leader for term ${data.term}` },
#             { timestamp: 2.1, type: 'RECOVERY', message: 'Cluster consensus established' }
#           ]
#         }));
#       }

#       setError(null);
#     } catch (err) {
#       console.error('Failed to fetch cluster status:', err);
#       setError('Failed to connect to RAFT simulation backend');
#     } finally {
#       setLoading(false);
#     }
#   }, [simulationState.events.length]);

#   // Simulate message flow for visualization
#   const generateMessages = useCallback(() => {
#     if (clusterState.nodes.length === 0) return;

#     const leader = clusterState.nodes.find(n => n.role === 'LEADER');
#     if (!leader) return;

#     const followers = clusterState.nodes.filter(n => n.role === 'FOLLOWER');
#     const newMessages = followers.map(follower => ({
#       from: leader.id,
#       to: follower.id,
#       type: 'HEARTBEAT',
#       timestamp: Date.now()
#     }));

#     setMessages(newMessages);
    
#     // Clear messages after animation
#     setTimeout(() => setMessages([]), 1000);
#   }, [clusterState.nodes]);

#   // Polling effect
#   useEffect(() => {
#     fetchClusterStatus();
#     const interval = setInterval(fetchClusterStatus, 2000);
#     return () => clearInterval(interval);
#   }, [fetchClusterStatus]);

#   // Message generation effect
#   useEffect(() => {
#     if (simulationState.isRunning) {
#       const messageInterval = setInterval(generateMessages, 3000);
#       return () => clearInterval(messageInterval);
#     }
#   }, [simulationState.isRunning, generateMessages]);

#   // Event handlers
#   const handleSimulationChange = (action) => {
#     setSimulationState(prev => ({
#       ...prev,
#       isRunning: action === 'start',
#       time: action === 'reset' ? 0 : prev.time
#     }));

#     if (action === 'start') {
#       const startEvent = {
#         timestamp: simulationState.time,
#         type: 'ELECTION',
#         message: 'Simulation started'
#       };
#       setSimulationState(prev => ({
#         ...prev,
#         events: [...prev.events, startEvent]
#       }));
#     }
#   };

#   const handleChaosEvent = (type, nodeId) => {
#     const chaosEvent = {
#       timestamp: simulationState.time,
#       type: 'PARTITION',
#       message: `Chaos event: ${type}${nodeId !== null ? ` on Node ${nodeId}` : ''}`
#     };
    
#     setSimulationState(prev => ({
#       ...prev,
#       events: [...prev.events, chaosEvent]
#     }));
#   };

#   const filteredEvents = simulationState.events.filter(event => 
#     logFilter === 'ALL' || event.type === logFilter
#   );

#   if (loading) {
#     return (
#       <div className="app-loading">
#         <div className="spinner"></div>
#         <p>Connecting to RAFT simulation...</p>
#       </div>
#     );
#   }

#   if (error) {
#     return (
#       <div className="app-error">
#         <h2>Connection Error</h2>
#         <p>{error}</p>
#         <button onClick={fetchClusterStatus}>Retry Connection</button>
#       </div>
#     );
#   }

#   return (
#     <div className="app-container">
#       <header className="app-header">
#         <h1>RAFT Distributed Systems Simulator</h1>
#         <StatusBar
#           currentTerm={clusterState.term}
#           leaderId={clusterState.leader}
#           simulationTime={simulationState.time}
#           isRunning={simulationState.isRunning}
#         />
#       </header>

#       <main className="app-main">
#         <div className="visualization-section">
#           <ClusterCanvas 
#             nodes={clusterState.nodes} 
#             messages={messages}
#           />
#           <ControlPanel
#             onSimulationChange={handleSimulationChange}
#             onChaosEvent={handleChaosEvent}
#           />
#         </div>

#         <div className="events-section">
#           <LogViewer
#             events={filteredEvents}
#             onFilterChange={setLogFilter}
#           />
#         </div>
#       </main>
#     </div>
#   );
# };

# export default App;

# // File: frontend/src/StatusBar.jsx
# import React from 'react';
# import PropTypes from 'prop-types';

# const StatusBar = ({ currentTerm, leaderId, simulationTime, isRunning }) => {
#   const formatTime = (time) => {
#     return `${time.toFixed(1)}s`;
#   };

#   const getStatusIndicator = () => {
#     return isRunning ? '🟢' : '🔴';
#   };

#   return (
#     <div className="status-bar">
#       <div className="status-section">
#         <div className="status-item primary">
#           <span className="status-indicator">{getStatusIndicator()}</span>
#           <span className="status-label">Status:</span>
#           <span className={`status-value ${isRunning ? 'running' : 'stopped'}`}>
#             {isRunning ? 'RUNNING' : 'STOPPED'}
#           </span>
#         </div>
#       </div>
      
#       <div className="status-section">
#         <div className="status-item">
#           <span className="status-label">⏱ Time:</span>
#           <span className="status-value">{formatTime(simulationTime)}</span>
#         </div>
        
#         <div className="status-item">
#           <span className="status-label">📊 Term:</span>
#           <span className="status-value term-badge">{currentTerm}</span>
#         </div>
        
#         <div className="status-item">
#           <span className="status-label">👑 Leader:</span>
#           <span className="status-value leader-badge">
#             {leaderId !== null ? `Node ${leaderId}` : 'None'}
#           </span>
#         </div>
#       </div>
      
#       <div className="status-section">
#         <div className="network-health">
#           <span className="status-label">🌐 Network:</span>
#           <div className="health-dots">
#             <span className="health-dot healthy"></span>
#             <span className="health-dot healthy"></span>
#             <span className="health-dot healthy"></span>
#           </div>
#         </div>
#       </div>
#     </div>
#   );
# };

# StatusBar.propTypes = {
#   currentTerm: PropTypes.number.isRequired,
#   leaderId: PropTypes.number,
#   simulationTime: PropTypes.number.isRequired,
#   isRunning: PropTypes.bool.isRequired
# };

# StatusBar.defaultProps = {
#   leaderId: null
# };

# export default StatusBar;

# // File: frontend/src/components/ClusterCanvas.jsx
# import React, { useRef, useEffect } from 'react';
# import PropTypes from 'prop-types';
# import Node from './Node';

# const ClusterCanvas = ({ nodes, messages }) => {
#   const canvasRef = useRef(null);
#   const containerRef = useRef(null);

#   // Calculate positions for nodes in a circle
#   const calculatePositions = (count, containerWidth = 600, containerHeight = 400) => {
#     const centerX = containerWidth / 2;
#     const centerY = containerHeight / 2;
#     const radius = Math.min(containerWidth, containerHeight) / 3;
    
#     return Array.from({ length: count }, (_, i) => {
#       const angle = (2 * Math.PI * i) / count - Math.PI / 2; // Start from top
#       return {
#         x: centerX + radius * Math.cos(angle),
#         y: centerY + radius * Math.sin(angle)
#       };
#     });
#   };

#   // Draw message arrows between nodes
#   useEffect(() => {
#     const canvas = canvasRef.current;
#     const container = containerRef.current;
#     if (!canvas || !container) return;

#     const rect = container.getBoundingClientRect();
#     canvas.width = rect.width;
#     canvas.height = rect.height;

#     const ctx = canvas.getContext('2d');
#     ctx.clearRect(0, 0, canvas.width, canvas.height);

#     if (messages.length === 0) return;

#     const positions = calculatePositions(nodes.length, canvas.width, canvas.height);

#     messages.forEach(msg => {
#       const fromNode = nodes.find(n => n.id === msg.from);
#       const toNode = nodes.find(n => n.id === msg.to);
#       if (!fromNode || !toNode) return;

#       const fromPos = positions[fromNode.id];
#       const toPos = positions[toNode.id];

#       // Draw animated arrow
#       ctx.beginPath();
#       ctx.setLineDash([8, 4]);
#       ctx.lineDashOffset = -(Date.now() / 50) % 12;
#       ctx.moveTo(fromPos.x, fromPos.y);
#       ctx.lineTo(toPos.x, toPos.y);
      
#       // Color based on message type
#       switch (msg.type) {
#         case 'HEARTBEAT':
#           ctx.strokeStyle = '#4ade80';
#           break;
#         case 'VOTE_REQUEST':
#           ctx.strokeStyle = '#fbbf24';
#           break;
#         case 'VOTE_RESPONSE':
#           ctx.strokeStyle = '#60a5fa';
#           break;
#         default:
#           ctx.strokeStyle = '#9ca3af';
#       }
      
#       ctx.lineWidth = 2;
#       ctx.stroke();

#       // Draw arrowhead
#       const headLength = 12;
#       const angle = Math.atan2(toPos.y - fromPos.y, toPos.x - fromPos.x);
      
#       ctx.beginPath();
#       ctx.setLineDash([]);
#       ctx.moveTo(toPos.x, toPos.y);
#       ctx.lineTo(
#         toPos.x - headLength * Math.cos(angle - Math.PI / 6),
#         toPos.y - headLength * Math.sin(angle - Math.PI / 6)
#       );
#       ctx.lineTo(
#         toPos.x - headLength * Math.cos(angle + Math.PI / 6),
#         toPos.y - headLength * Math.sin(angle + Math.PI / 6)
#       );
#       ctx.closePath();
#       ctx.fillStyle = ctx.strokeStyle;
#       ctx.fill();
#     });
#   }, [nodes, messages]);

#   const positions = calculatePositions(
#     nodes.length, 
#     containerRef.current?.clientWidth || 600, 
#     containerRef.current?.clientHeight || 400
#   );

#   const handleNodeClick = (nodeId) => {
#     console.log(`Node ${nodeId} clicked`);
#     // Future: Add node inspection modal
#   };

#   return (
#     <div className="cluster-canvas" ref={containerRef}>
#       <canvas 
#         ref={canvasRef} 
#         className="message-canvas"
#       />
      
#       {nodes.map((node, index) => (
#         <Node
#           key={node.id}
#           id={node.id}
#           role={node.role}
#           term={node.term}
#           status={node.status}
#           onClick={handleNodeClick}
#           style={{
#             position: 'absolute',
#             left: `${positions[index]?.x - 40 || 0}px`,
#             top: `${positions[index]?.y - 40 || 0}px`,
#             transform: 'translate(-50%, -50%)'
#           }}
#         />
#       ))}
      
#       <div className="cluster-info">
#         <div className="cluster-stats">
#           <span>Nodes: {nodes.length}</span>
#           <span>Active Messages: {messages.length}</span>
#         </div>
#       </div>
#     </div>
#   );
# };

# ClusterCanvas.propTypes = {
#   nodes: PropTypes.arrayOf(
#     PropTypes.shape({
#       id: PropTypes.number.isRequired,
#       role: PropTypes.string.isRequired,
#       term: PropTypes.number.isRequired,
#       status: PropTypes.string.isRequired
#     })
#   ).isRequired,
#   messages: PropTypes.arrayOf(
#     PropTypes.shape({
#       from: PropTypes.number.isRequired,
#       to: PropTypes.number.isRequired,
#       type: PropTypes.string.isRequired
#     })
#   ).isRequired
# };

# export default ClusterCanvas;


# // File: frontend/src/components/Node.jsx

# import React, { useState, useEffect } from 'react';
# import PropTypes from 'prop-types';

# const Node = ({ id, role, term, status, style, onClick }) => {
#   const [isAnimating, setIsAnimating] = useState(false);
#   const [lastRole, setLastRole] = useState(role);

#   // Trigger animation on role change
#   useEffect(() => {
#     if (role !== lastRole) {
#       setIsAnimating(true);
#       const timer = setTimeout(() => setIsAnimating(false), 1000);
#       setLastRole(role);
#       return () => clearTimeout(timer);
#     }
#   }, [role, lastRole]);

#   const getNodeClasses = () => {
#     let classes = ['node', `node-${role.toLowerCase()}`];
    
#     if (status !== 'HEALTHY') {
#       classes.push(`node-${status.toLowerCase()}`);
#     }
    
#     if (isAnimating) {
#       classes.push('node-transitioning');
#     }
    
#     return classes.join(' ');
#   };

#   const getRoleEmoji = () => {
#     if (status === 'FAILED') return '💀';
#     if (status === 'PARTITIONED') return '🔌';
    
#     switch (role) {
#       case 'LEADER': return '👑';
#       case 'CANDIDATE': return '🗳️';
#       default: return '🖥️';
#     }
#   };

#   const getStatusText = () => {
#     switch (status) {
#       case 'FAILED': return 'CRASHED';
#       case 'PARTITIONED': return 'ISOLATED';
#       default: return role;
#     }
#   };

#   return (
#     <div
#       className={getNodeClasses()}
#       style={style}
#       onClick={() => onClick && onClick(id)}
#       title={`Node ${id} - ${getStatusText()} (Term ${term})`}
#     >
#       <div className="node-content">
#         <div className="node-emoji">{getRoleEmoji()}</div>
#         <div className="node-id">#{id}</div>
#         <div className="node-term">T{term}</div>
#         <div className="node-status">{getStatusText()}</div>
#       </div>
      
#       {role === 'LEADER' && (
#         <div className="node-glow"></div>
#       )}
      
#       {role === 'CANDIDATE' && (
#         <div className="node-pulse"></div>
#       )}
#     </div>
#   );
# };

# Node.propTypes = {
#   id: PropTypes.number.isRequired,
#   role: PropTypes.oneOf(['LEADER', 'FOLLOWER', 'CANDIDATE']).isRequired,
#   term: PropTypes.number.isRequired,
#   status: PropTypes.oneOf(['HEALTHY', 'FAILED', 'PARTITIONED']).isRequired,
#   style: PropTypes.object,
#   onClick: PropTypes.func
# };

# Node.defaultProps = {
#   style: {},
#   onClick: null
# };

# export default Node;


# // File: frontend/src/components/ControlPanel.jsx
# import React, { useState } from 'react';
# import PropTypes from 'prop-types';

# const ControlPanel = ({ onSimulationChange, onChaosEvent }) => {
#   const [params, setParams] = useState({
#     nodeCount: 5,
#     maxTime: 60,
#     messageDropRate: 0.1
#   });
#   const [isExpanded, setIsExpanded] = useState(false);

#   const handleParamChange = (e) => {
#     const { name, value, type } = e.target;
#     setParams(prev => ({
#       ...prev,
#       [name]: type === 'number' ? 
#         Math.min(Math.max(parseFloat(value), 0), name === 'nodeCount' ? 7 : Infinity) : 
#         parseFloat(value)
#     }));
#   };

#   const handleStart = () => {
#     onSimulationChange('start');
#   };

#   const handleStop = () => {
#     onSimulationChange('stop');
#   };

#   const handleReset = () => {
#     onSimulationChange('reset');
#   };

#   const injectChaos = (type, nodeId = null) => {
#     onChaosEvent(type, nodeId);
#   };

#   return (
#     <div className="control-panel">
#       <div className="panel-header">
#         <h3>Simulation Controls</h3>
#         <button 
#           className="expand-button"
#           onClick={() => setIsExpanded(!isExpanded)}
#         >
#           {isExpanded ? '▼' : '▶'}
#         </button>
#       </div>
      
#       {isExpanded && (
#         <div className="panel-content">
#           <div className="param-group">
#             <label className="param-label">
#               Node Count (3-7):
#               <input
#                 type="number"
#                 name="nodeCount"
#                 min="3"
#                 max="7"
#                 value={params.nodeCount}
#                 onChange={handleParamChange}
#                 className="param-input"
#               />
#             </label>
            
#             <label className="param-label">
#               Max Time (s):
#               <input
#                 type="number"
#                 name="maxTime"
#                 min="10"
#                 max="300"
#                 step="10"
#                 value={params.maxTime}
#                 onChange={handleParamChange}
#                 className="param-input"
#               />
#             </label>
            
#             <label className="param-label">
#               Message Drop Rate:
#               <div className="range-container">
#                 <input
#                   type="range"
#                   name="messageDropRate"
#                   min="0"
#                   max="0.5"
#                   step="0.01"
#                   value={params.messageDropRate}
#                   onChange={handleParamChange}
#                   className="param-range"
#                 />
#                 <span className="range-value">{(params.messageDropRate * 100).toFixed(0)}%</span>
#               </div>
#             </label>
#           </div>
#         </div>
#       )}
      
#       <div className="button-group">
#         <button onClick={handleStart} className="control-button start-button">
#           ▶ Start
#         </button>
#         <button onClick={handleStop} className="control-button stop-button">
#           ⏸ Stop
#         </button>
#         <button onClick={handleReset} className="control-button reset-button">
#           🔄 Reset
#         </button>
#       </div>
      
#       <div className="chaos-section">
#         <h4>Chaos Engineering</h4>
#         <div className="chaos-group">
#           <button 
#             onClick={() => injectChaos('KILL_NODE', Math.floor(Math.random() * params.nodeCount))}
#             className="chaos-button danger"
#           >
#             💀 Kill Random Node
#           </button>
#           <button 
#             onClick={() => injectChaos('PARTITION')}
#             className="chaos-button warning"
#           >
#             🔌 Network Partition
#           </button>
#           <button 
#             onClick={() => injectChaos('RESTORE_ALL')}
#             className="chaos-button success"
#           >
#             🔧 Restore All
#           </button>
#         </div>
#       </div>
#     </div>
#   );
# };

# ControlPanel.propTypes = {
#   onSimulationChange: PropTypes.func.isRequired,
#   onChaosEvent: PropTypes.func.isRequired
# };

# export default ControlPanel;



# // File: frontend/src/components/LogViewer.jsx
# import React, { useState, useEffect, useRef } from 'react';
# import PropTypes from 'prop-types';

# const LogViewer = ({ events, onFilterChange }) => {
#   const [filter, setFilter] = useState('ALL');
#   const [autoScroll, setAutoScroll] = useState(true);
#   const logEndRef = useRef(null);

#   // Auto-scroll to bottom when new events arrive
#   useEffect(() => {
#     if (autoScroll && logEndRef.current) {
#       logEndRef.current.scrollIntoView({ behavior: 'smooth' });
#     }
#   }, [events, autoScroll]);

#   const handleFilterChange = (newFilter) => {
#     setFilter(newFilter);
#     onFilterChange(newFilter);
#   };

#   const getEventIcon = (type) => {
#     const icons = {
#       ELECTION: '🗳️',
#       LEADER_CHANGE: '👑',
#       PARTITION: '🔌',
#       RECOVERY: '🔧',
#       HEARTBEAT: '💓',
#       VOTE: '✋',
#       DEFAULT: '📝'
#     };
#     return icons[type] || icons.DEFAULT;
#   };

#   const getEventColor = (type) => {
#     const colors = {
#       ELECTION: 'log-election',
#       LEADER_CHANGE: 'log-leader',
#       PARTITION: 'log-partition',
#       RECOVERY: 'log-recovery',
#       HEARTBEAT: 'log-heartbeat',
#       VOTE: 'log-vote',
#       DEFAULT: 'log-default'
#     };
#     return colors[type] || colors.DEFAULT;
#   };

#   const formatTimestamp = (timestamp) => {
#     return `${timestamp.toFixed(2)}s`;
#   };

#   return (
#     <div className="log-viewer">
#       <div className="log-header">
#         <h3>Event Log</h3>
#         <div className="log-controls">
#           <select 
#             value={filter}
#             onChange={(e) => handleFilterChange(e.target.value)}
#             className="filter-select"
#           >
#             <option value="ALL">All Events</option>
#             <option value="ELECTION">Elections</option>
#             <option value="LEADER_CHANGE">Leader Changes</option>
#             <option value="PARTITION">Partitions</option>
#             <option value="RECOVERY">Recoveries</option>
#           </select>
          
#           <label className="auto-scroll-toggle">
#             <input
#               type="checkbox"
#               checked={autoScroll}
#               onChange={(e) => setAutoScroll(e.target.checked)}
#             />
#             Auto-scroll
#           </label>
#         </div>
#       </div>
      
#       <div className="log-container">
#         {events.length === 0 ? (
#           <div className="log-empty">
#             <p>No events to display</p>
#             <small>Start the simulation to see RAFT consensus events</small>
#           </div>
#         ) : (
#           events.map((event, index) => (
#             <div 
#               key={index} 
#               className={`log-entry ${getEventColor(event.type)}`}
#             >
#               <span className="log-icon">{getEventIcon(event.type)}</span>
#               <span className="log-timestamp">[{formatTimestamp(event.timestamp)}]</span>
#               <span className="log-message">{event.message}</span>
#             </div>
#           ))
#         )}
#         <div ref={logEndRef} />
#       </div>
      
#       <div className="log-footer">
#         <small>{events.length} total events</small>
#       </div>
#     </div>
#   );
# };

# LogViewer.propTypes = {
#   events: PropTypes.arrayOf(
#     PropTypes.shape({
#       timestamp: PropTypes.number.isRequired,
#       type: PropTypes.string.isRequired,
#       message: PropTypes.string.isRequired
#     })
#   ).isRequired,
#   onFilterChange: PropTypes.func.isRequired
# };

# export default LogViewer;