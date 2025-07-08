import os
import requests

# === 🔐 Configuration ===
API_KEY = "sk-1d543ab9361542a4a0596e6b85fc715e"
MODEL = "deepseek-chat"
ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

# === 🗂️ Project Files to Submit ===
INPUT_FILES = [
    "src/index.css",

]


OUTPUT_FILE = "hmmm.txt"

# === 📦 Load Code from Files ===
def load_files(file_paths):
    combined = ""
    for path in file_paths:
        if not os.path.exists(path):
            print(f"⚠️ Skipping missing file: {path}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            combined += f"\n# ==== FILE: {path} ====\n"
            combined += f.read() + "\n"
    return combined

code_context = load_files(INPUT_FILES)

# === ✍️ Custom Refactoring Prompt ===
refactor_prompt = f"""
You are an expert software engineer reviewing a multi-file Python project built for distributed system simulation.
Build a frontend React dashboard for a Flask-based distributed systems simulator called RAFT DSS (Distributed Systems Simulator). The simulator is a production-grade Python implementation of the RAFT consensus algorithm, capable of leader election, log replication, network partition simulation, and failure injection.
The backend exposes REST endpoints like:
GET /raft/status — returns current simulation state (nodes, terms, roles, etc.)
GET /raft/events — returns or streams log of events
POST /raft/start — starts a simulation run
(Optional) WebSocket for real-time logs or visual updates
Build a visually compelling, responsive React frontend with the goal of presenting RAFT mechanics in an educational, engineering-grade, and interactive way.

🎯 Features & Functional Goals
1. Cluster Visualisation (Canvas View)
Visualise 3–7 nodes as circles in a ring or cluster layout

Each node shows:
Node ID
Role (FOLLOWER, CANDIDATE, LEADER)
Current term
Leader visually stands out (gold glow or icon 👑)
Failed or partitioned nodes gray out or pulse
Animated messages (heartbeats, votes) as arrows between nodes
2. Event Timeline View
Real-time event log panel (sidebar or bottom panel)
Scrollable, readable log like:
[01.2s] Node 3 became CANDIDATE (term 4)  
[01.6s] Node 3 won election (term 4)  
[03.3s] Partition between Node 2 and Node 0  
Filterable by event type (election, replication, chaos)

3. Control Panel
Start / Stop / Reset simulation

Set parameters before run:

Number of nodes

Max time

Message drop rate

Buttons to inject chaos:

Kill Node

Partition Link

Restore Node

⚙️ Suggested Component Structure
<App>
├── <ClusterCanvas />     ← visual network map of nodes
│   └── <Node />          ← renders a single node
├── <LogViewer />         ← timeline of consensus events
├── <ControlPanel />      ← simulation controls & chaos injection
└── <StatusBar />         ← shows current leader, cluster term, etc.
🎨 Visual Design Requirements
Theme: Dark mode preferred (suitable for engineers & researchers)

Color roles:

🟢 LEADER

🔵 FOLLOWER

🟡 CANDIDATE

🔴 FAILED

Smooth UI transitions (React Spring, Framer Motion, or CSS animations)

Tooltips or modals on hover (node logs, metrics, election history)

Responsive layout for 13"–15" laptop screens

🔌 Integration Details
Connect to Flask backend via Axios or fetch

Base URL from .env variable: REACT_APP_API_URL=http://localhost:5000

You may use mock data to simulate Flask responses during development

Feel free to use Tailwind, CSS Modules, or styled components

🧪 Bonus Suggestions (Use Your Judgement)
You may invent or include other features you believe improve:

Simulation observability

Frontend responsiveness / clarity

Debugging friendliness for engineers

Educational insight into consensus under failure

For example:

Simulation playback or scrubbing

Log compaction visualiser per node

Split-brain animation mode

Exportable timeline logs

“Node health” dashboard with metrics

✳️ Don’t hesitate to add micro-interactions, polish, or thoughtful visual cues that make the dashboard feel like something from a distributed systems engineer’s toolkit — even if those features weren’t explicitly requested.

📦 Tech Stack Expectations
React (Hooks preferred)

Axios or fetch

CSS Modules, TailwindCSS, or similar

D3.js or SVG/canvas for message paths (optional)

No Redux required — use Context or component state

✅ Final result should be a clean, component-based React app inside /frontend with mocked or real Flask connections that renders a live RAFT simulation dashboard.

Below is the complete codebase. Reply with the fully updated and polished versions of **only** the files that were changed. Use clear `# ==== FILE: path ====` markers to segment your response.

{code_context}
"""

# === 📬 Compose Request Payload ===
payload = {
    "model": MODEL,
    "temperature": 0.2,
    "messages": [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that always responds in English and returns clean, production-quality Python."
            )
        },
        {
            "role": "user",
            "content": refactor_prompt
        }
    ]
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# === 🚀 Send Request to DeepSeek ===
print("📡 Sending full project context to DeepSeek...\n")
response = requests.post(ENDPOINT, headers=headers, json=payload)

# === 📥 Handle the Response ===
if response.status_code == 200:
    result_text = response.json()["choices"][0]["message"]["content"]
    
    print("✅ DeepSeek responded with proposed changes!\n")
    print(result_text[:1000] + "\n...")  # Preview first 1000 characters

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write(result_text)
    print(f"📁 Saved full response to: {OUTPUT_FILE}")

else:
    print(f"❌ DeepSeek API Error {response.status_code}:\n")
    print(response.text)
