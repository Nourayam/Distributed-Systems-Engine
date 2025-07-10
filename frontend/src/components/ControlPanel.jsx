import React, { useState } from 'react';
import PropTypes from 'prop-types';

const ControlPanel = ({ onSimulationControl, onChaosEvent, isRunning, animationSpeed = 1.0 }) => {
  const [params, setParams] = useState({
    nodeCount: 5,
    maxTime: 60,
    animationSpeed: 1.0
  });
  const [isExpanded, setIsExpanded] = useState(false);

  const handleStart = () => {
    onSimulationControl('start', params);
  };

  const handleChaos = (type) => {
    onChaosEvent(type);
  };

  return (
    <div className="control-panel">
      <div className="primary-controls">
        <button 
          onClick={handleStart}
          className="control-btn start-btn"
          disabled={isRunning}
        >
          <span className="btn-icon">▶</span>
          <span className="btn-text">Start</span>
        </button>
        
        <button 
          onClick={() => onSimulationControl('stop')}
          className="control-btn stop-btn"
          disabled={!isRunning}
        >
          <span className="btn-icon">⏸</span>
          <span className="btn-text">Stop</span>
        </button>
        
        <button 
          onClick={() => onSimulationControl('reset')}
          className="control-btn reset-btn"
        >
          <span className="btn-icon">🔄</span>
          <span className="btn-text">Reset</span>
        </button>
        
        <button 
          onClick={() => setIsExpanded(!isExpanded)}
          className="control-btn expand-btn"
        >
          <span className="btn-icon">{isExpanded ? '▲' : '▼'}</span>
          <span className="btn-text">Settings</span>
        </button>
      </div>
      
      {isExpanded && (
        <div className="expanded-controls">
          <div className="param-row">
            <label className="param-label">Nodes: {params.nodeCount}</label>
            <input
              type="range"
              min="3"
              max="7"
              value={params.nodeCount}
              onChange={(e) => setParams(prev => ({ ...prev, nodeCount: parseInt(e.target.value) }))}
              className="param-slider"
              disabled={isRunning}
            />
          </div>
          
          <div className="param-row">
            <label className="param-label">Time: {params.maxTime}s</label>
            <input
              type="range"
              min="30"
              max="180"
              step="10"
              value={params.maxTime}
              onChange={(e) => setParams(prev => ({ ...prev, maxTime: parseInt(e.target.value) }))}
              className="param-slider"
              disabled={isRunning}
            />
          </div>
          
          <div className="param-row">
            <label className="param-label">Speed: {params.animationSpeed.toFixed(1)}x</label>
            <input
              type="range"
              min="0.5"
              max="3"
              step="0.1"
              value={params.animationSpeed}
              onChange={(e) => setParams(prev => ({ ...prev, animationSpeed: parseFloat(e.target.value) }))}
              className="param-slider"
            />
          </div>
        </div>
      )}
      
      <div className="chaos-controls">
        <h4 className="chaos-title">🌪️ Chaos Engineering</h4>
        <div className="chaos-buttons">
          <button 
            onClick={() => handleChaos('KILL_NODE')}
            className="chaos-btn kill-btn"
            disabled={!isRunning}
          >
            <span className="btn-icon">💀</span>
            <span className="btn-text">Kill Node</span>
          </button>
          
          <button 
            onClick={() => handleChaos('RESTORE_ALL')}
            className="chaos-btn restore-btn"
            disabled={!isRunning}
          >
            <span className="btn-icon">🔧</span>
            <span className="btn-text">Restore All</span>
          </button>
        </div>
      </div>
    </div>
  );
};

ControlPanel.propTypes = {
  onSimulationControl: PropTypes.func.isRequired,
  onChaosEvent: PropTypes.func.isRequired,
  isRunning: PropTypes.bool.isRequired,
  animationSpeed: PropTypes.number
};

export default ControlPanel;