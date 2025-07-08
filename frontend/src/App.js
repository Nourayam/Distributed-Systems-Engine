import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import StatusBar from './StatusBar';
import ClusterCanvas from './components/ClusterCanvas';
import Node from './components/Node';
import ControlPanel from './components/ControlPanel';
import LogViewer from './components/LogViewer';
import './index.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const App = () => {
  const [clusterState, setClusterState] = useState({
    nodes: [],
    leader: null,
    term: 0
  });
  const [simulationState, setSimulationState] = useState({
    isRunning: false,
    time: 0,
    events: []
  });
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [logFilter, setLogFilter] = useState('ALL');

  // Fetch cluster status from backend
  const fetchClusterStatus = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/raft/status`);
      const data = response.data;
      
      // Transform backend data to frontend format
      const transformedNodes = data.nodes.map(node => ({
        id: node.id,
        role: node.state,
        term: node.term,
        status: 'HEALTHY' // Default status, can be enhanced
      }));

      setClusterState({
        nodes: transformedNodes,
        leader: data.leader,
        term: data.term
      });

      // Simulate some events for demonstration
      if (simulationState.events.length === 0) {
        setSimulationState(prev => ({
          ...prev,
          time: prev.time + 0.1,
          events: [
            { timestamp: 0.0, type: 'ELECTION', message: 'Initial leader election started' },
            { timestamp: 1.2, type: 'LEADER_CHANGE', message: `Node ${data.leader} became leader for term ${data.term}` },
            { timestamp: 2.1, type: 'RECOVERY', message: 'Cluster consensus established' }
          ]
        }));
      }

      setError(null);
    } catch (err) {
      console.error('Failed to fetch cluster status:', err);
      setError('Failed to connect to RAFT simulation backend');
    } finally {
      setLoading(false);
    }
  }, [simulationState.events.length]);

  // Simulate message flow for visualization
  const generateMessages = useCallback(() => {
    if (clusterState.nodes.length === 0) return;

    const leader = clusterState.nodes.find(n => n.role === 'LEADER');
    if (!leader) return;

    const followers = clusterState.nodes.filter(n => n.role === 'FOLLOWER');
    const newMessages = followers.map(follower => ({
      from: leader.id,
      to: follower.id,
      type: 'HEARTBEAT',
      timestamp: Date.now()
    }));

    setMessages(newMessages);
    
    // Clear messages after animation
    setTimeout(() => setMessages([]), 1000);
  }, [clusterState.nodes]);

  // Polling effect
  useEffect(() => {
    fetchClusterStatus();
    const interval = setInterval(fetchClusterStatus, 2000);
    return () => clearInterval(interval);
  }, [fetchClusterStatus]);

  // Message generation effect
  useEffect(() => {
    if (simulationState.isRunning) {
      const messageInterval = setInterval(generateMessages, 3000);
      return () => clearInterval(messageInterval);
    }
  }, [simulationState.isRunning, generateMessages]);

  // Event handlers
  const handleSimulationChange = (action) => {
    setSimulationState(prev => ({
      ...prev,
      isRunning: action === 'start',
      time: action === 'reset' ? 0 : prev.time
    }));

    if (action === 'start') {
      const startEvent = {
        timestamp: simulationState.time,
        type: 'ELECTION',
        message: 'Simulation started'
      };
      setSimulationState(prev => ({
        ...prev,
        events: [...prev.events, startEvent]
      }));
    }
  };

  const handleChaosEvent = (type, nodeId) => {
    const chaosEvent = {
      timestamp: simulationState.time,
      type: 'PARTITION',
      message: `Chaos event: ${type}${nodeId !== null ? ` on Node ${nodeId}` : ''}`
    };
    
    setSimulationState(prev => ({
      ...prev,
      events: [...prev.events, chaosEvent]
    }));
  };

  const filteredEvents = simulationState.events.filter(event => 
    logFilter === 'ALL' || event.type === logFilter
  );

  if (loading) {
    return (
      <div className="app-loading">
        <div className="spinner"></div>
        <p>Connecting to RAFT simulation...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app-error">
        <h2>Connection Error</h2>
        <p>{error}</p>
        <button onClick={fetchClusterStatus}>Retry Connection</button>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>RAFT Distributed Systems Simulator</h1>
        <StatusBar
          currentTerm={clusterState.term}
          leaderId={clusterState.leader}
          simulationTime={simulationState.time}
          isRunning={simulationState.isRunning}
        />
      </header>

      <main className="app-main">
        <div className="visualization-section">
          <ClusterCanvas 
            nodes={clusterState.nodes} 
            messages={messages}
          />
          <ControlPanel
            onSimulationChange={handleSimulationChange}
            onChaosEvent={handleChaosEvent}
          />
        </div>

        <div className="events-section">
          <LogViewer
            events={filteredEvents}
            onFilterChange={setLogFilter}
          />
        </div>
      </main>
    </div>
  );
};

export default App;