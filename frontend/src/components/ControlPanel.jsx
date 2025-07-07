import React, { useState } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import styles from './ControlPanel.module.css';

const ControlPanel = ({ onSimulationChange, onChaosEvent }) => {
  const [params, setParams] = useState({
    nodeCount: 5,
    maxTime: 60,
    messageDropRate: 0.1
  });

  const handleParamChange = (e) => {
    const { name, value } = e.target;
    setParams(prev => ({
      ...prev,
      [name]: name === 'nodeCount' ? Math.min(Math.max(parseInt(value), 3), 7) : parseFloat(value)
    }));
  };

  const handleStart = async () => {
    try {
      await axios.post(`${process.env.REACT_APP_API_URL}/raft/start`, params);
      onSimulationChange('start');
    } catch (error) {
      console.error('Error starting simulation:', error);
    }
  };

  const handleStop = async () => {
    try {
      await axios.post(`${process.env.REACT_APP_API_URL}/raft/stop`);
      onSimulationChange('stop');
    } catch (error) {
      console.error('Error stopping simulation:', error);
    }
  };

  const handleReset = async () => {
    try {
      await axios.post(`${process.env.REACT_APP_API_URL}/raft/reset`);
      onSimulationChange('reset');
    } catch (error) {
      console.error('Error resetting simulation:', error);
    }
  };

  const injectChaos = async (type, nodeId = null) => {
    try {
      const payload = { type };
      if (nodeId !== null) payload.nodeId = nodeId;
      
      await axios.post(`${process.env.REACT_APP_API_URL}/raft/chaos`, payload);
      onChaosEvent(type, nodeId);
    } catch (error) {
      console.error('Error injecting chaos:', error);
    }
  };

  return (
    <div className={styles.panel}>
      <h3 className={styles.panelTitle}>Simulation Controls</h3>
      
      <div className={styles.paramGroup}>
        <label>
          Node Count (3-7):
          <input
            type="number"
            name="nodeCount"
            min="3"
            max="7"
            value={params.nodeCount}
            onChange={handleParamChange}
          />
        </label>
        
        <label>
          Max Time (s):
          <input
            type="number"
            name="maxTime"
            min="10"
            max="300"
            step="10"
            value={params.maxTime}
            onChange={handleParamChange}
          />
        </label>
        
        <label>
          Message Drop Rate:
          <input
            type="range"
            name="messageDropRate"
            min="0"
            max="0.5"
            step="0.05"
            value={params.messageDropRate}
            onChange={handleParamChange}
          />
          <span>{params.messageDropRate.toFixed(2)}</span>
        </label>
      </div>
      
      <div className={styles.buttonGroup}>
        <button onClick={handleStart} className={styles.startButton}>Start</button>
        <button onClick={handleStop} className={styles.stopButton}>Stop</button>
        <button onClick={handleReset} className={styles.resetButton}>Reset</button>
      </div>
      
      <h3 className={styles.chaosTitle}>Chaos Engineering</h3>
      <div className={styles.chaosGroup}>
        <button 
          onClick={() => injectChaos('KILL_NODE', Math.floor(Math.random() * params.nodeCount))}
          className={styles.chaosButton}
        >
          Kill Random Node
        </button>
        <button 
          onClick={() => injectChaos('PARTITION')}
          className={styles.chaosButton}
        >
          Random Partition
        </button>
        <button 
          onClick={() => injectChaos('RESTORE_ALL')}
          className={styles.chaosButton}
        >
          Restore All Nodes
        </button>
      </div>
    </div>
  );
};

ControlPanel.propTypes = {
  onSimulationChange: PropTypes.func.isRequired,
  onChaosEvent: PropTypes.func.isRequired
};

export default ControlPanel;
