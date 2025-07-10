import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import StatusBar from './StatusBar';
import ClusterCanvas from './components/ClusterCanvas';
import ControlPanel from './components/ControlPanel';
import LogViewer from './components/LogViewer';
import { useInterval } from './hooks/useInterval';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const App = () => {
  const [clusterState, setClusterState] = useState({
    nodes: [],
    leader: null,
    term: 0,
    messages: []
  });
  
  const [simulationState, setSimulationState] = useState({
    isRunning: false,
    time: 0,
    events: [],
    animationSpeed: 1.0
  });
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [connectionRetries, setConnectionRetries] = useState(0);
  
  const eventsRef = useRef([]);
  const lastEventTimestamp = useRef(0);

  const fetchClusterStatus = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/raft/status`, {
        timeout: 5000
      });
      
      const data = response.data;
      
      // Update cluster state
      setClusterState({
        nodes: data.nodes || [],
        leader: data.leader,
        term: data.term || 0,
        messages: data.messages || []
      });
      
      // Update simulation state
      setSimulationState(prev => ({
        isRunning: data.running || false,
        time: data.simulation_time || 0,
        events: data.events || prev.events,
        animationSpeed: data.animation_speed || 1.0
      }));
      
      // Process new events
      if (data.events && data.events.length > 0) {
        const newEvents = data.events.filter(
          e => e.timestamp > lastEventTimestamp.current
        );
        if (newEvents.length > 0) {
          eventsRef.current = [...eventsRef.current, ...newEvents].slice(-100);
          lastEventTimestamp.current = Math.max(
            ...newEvents.map(e => e.timestamp)
          );
        }
      }
      
      setError(null);
      setConnectionRetries(0);
    } catch (err) {
      console.error('Failed to fetch cluster status:', err);
      
      if (connectionRetries < 3) {
        setConnectionRetries(prev => prev + 1);
      } else {
        setError('Unable to connect to RAFT simulation backend.');
      }
    } finally {
      setLoading(false);
    }
  }, [connectionRetries]);

  // Faster polling for smoother animations
  useInterval(fetchClusterStatus, loading || error ? null : 250);

  useEffect(() => {
    fetchClusterStatus();
  }, [fetchClusterStatus]);

  const handleSimulationControl = useCallback(async (action, params = {}) => {
    try {
      const endpoint = `/raft/${action}`;
      const response = await axios.post(`${API_URL}${endpoint}`, params);
      
      if (response.data.status === 'success') {
        if (action === 'start') {
          setSimulationState(prev => ({ ...prev, isRunning: true }));
        } else if (action === 'stop') {
          setSimulationState(prev => ({ ...prev, isRunning: false }));
        } else if (action === 'reset') {
          setSimulationState({ isRunning: false, time: 0, events: [], animationSpeed: 1.0 });
          setClusterState({ nodes: [], leader: null, term: 0, messages: [] });
          eventsRef.current = [];
          lastEventTimestamp.current = 0;
        }
        
        setTimeout(fetchClusterStatus, 100);
      }
    } catch (err) {
      console.error(`Failed to ${action} simulation:`, err);
      setError(`Failed to ${action} simulation.`);
    }
  }, [fetchClusterStatus]);

  const handleChaosEvent = useCallback(async (type, nodeId = null) => {
    try {
      await axios.post(`${API_URL}/raft/chaos`, { type, nodeId });
      setTimeout(fetchClusterStatus, 100);
    } catch (err) {
      console.error('Failed to inject chaos:', err);
    }
  }, [fetchClusterStatus]);

  if (loading) {
    return (
      <div className="app-loading">
        <div className="spinner"></div>
        <p>Connecting to RAFT simulation...</p>
      </div>
    );
  }

  if (error && connectionRetries >= 3) {
    return (
      <div className="app-error">
        <h2>Connection Error</h2>
        <p>{error}</p>
        <button onClick={() => {
          setConnectionRetries(0);
          setError(null);
          fetchClusterStatus();
        }}>
          Retry Connection
        </button>
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
          nodeCount={clusterState.nodes.length}
        />
      </header>

      <main className="app-main">
        <div className="main-content">
          <div className="cluster-section">
            <ClusterCanvas 
              nodes={clusterState.nodes} 
              messages={clusterState.messages}
              leaderId={clusterState.leader}
              animationSpeed={simulationState.animationSpeed}
            />
          </div>
          
          <div className="control-section">
            <ControlPanel
              onSimulationControl={handleSimulationControl}
              onChaosEvent={handleChaosEvent}
              isRunning={simulationState.isRunning}
              animationSpeed={simulationState.animationSpeed}
            />
          </div>
        </div>

        <div className="events-section">
          <LogViewer
            events={eventsRef.current}
            isRunning={simulationState.isRunning}
          />
        </div>
      </main>
    </div>
  );
};

export default App;