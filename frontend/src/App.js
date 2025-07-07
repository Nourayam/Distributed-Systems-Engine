// Write the main App component for a distributed systems dashboard frontend using React. It should:

// Import and render components like <ClusterCanvas />, <LogViewer />, <ControlPanel />, and <StatusBar />

// Fetch cluster status from the Flask API (/raft/status) on load

// Organise layout using a clean structure (flex or grid) for engineers

// Handle loading/error states gracefully

// Read backend URL from .env via process.env.REACT_APP_API_URL



import { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [nodes, setNodes] = useState([]);

  useEffect(() => {
    axios.get(`${process.env.REACT_APP_API_URL}/raft/status`)
      .then(res => setNodes(res.data.nodes))
      .catch(err => console.error(err));
  }, []);

  return (
    <div style={{ padding: '2rem' }}>
      <h1>RAFT Cluster Status</h1>
      <ul>
        {nodes.map((node) => (
          <li key={node.id}>
            Node {node.id} — {node.state} (term {node.term})
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
