import React, { useState } from 'react';
import PropTypes from 'prop-types';

const ControlPanel = ({ onSimulationControl, onChaosEvent, isRunning }) => {
  const [params, setParams] = useState({
    nodeCount: 5,
    maxTime: 60,
    messageDropRate: 0.1
  });
  const [isExpanded, setIsExpanded] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const handleParamChange = (name, value) => {
    setParams(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAction = async (action) => {
    setIsLoading(true);
    try {
      await onSimulationControl(action, params);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChaos = (type, nodeId = null) => {
    onChaosEvent(type, nodeId);
  };

  return (
    <div className="control-panel">
      <div className="panel-header">
        <h3>🎮 Simulation Controls</h3>
        <button 
          className="expand-button"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-label={isExpanded ? 'Collapse' : 'Expand'}
        >
          {isExpanded ? '▼' : '▶'}
        </button>
      </div>
      
      {isExpanded && (
        <div className="panel-content">
          <div className="param-group">
            <label className="param-label">
              <span>Node Count</span>
              <div className="param-input-group">
                <input
                  type="range"
                  min="3"
                  max="7"
                  value={params.nodeCount}
                  onChange={(e) => handleParamChange('nodeCount', parseInt(e.target.value))}
                  className="param-range"
                  disabled={isRunning}
                />
                <span className="param-value">{params.nodeCount}</span>
              </div>
            </label>
            
            <label className="param-label">
              <span>Simulation Time (seconds)</span>
              <div className="param-input-group">
                <input
                  type="range"
                  min="10"
                  max="300"
                  step="10"
                  value={params.maxTime}
                  onChange={(e) => handleParamChange('maxTime', parseInt(e.target.value))}
                  className="param-range"
                  disabled={isRunning}
                />
                <span className="param-value">{params.maxTime}s</span>
              </div>
            </label>
            
            <label className="param-label">
              <span>Message Drop Rate</span>
              <div className="param-input-group">
                <input
                  type="range"
                  min="0"
                  max="0.5"
                  step="0.01"
                  value={params.messageDropRate}
                  onChange={(e) => handleParamChange('messageDropRate', parseFloat(e.target.value))}
                  className="param-range"
                />
                <span className="param-value">{(params.messageDropRate * 100).toFixed(0)}%</span>
              </div>
            </label>
          </div>
        </div>
      )}
      
      <div className="button-group">
        <button 
          onClick={() => handleAction('start')} 
          className="control-button start-button"
          disabled={isRunning || isLoading}
        >
          <span>▶</span> Start
        </button>
        <button 
          onClick={() => handleAction('stop')} 
          className="control-button stop-button"
          disabled={!isRunning || isLoading}
        >
          <span>⏸</span> Stop
        </button>
        <button 
          onClick={() => handleAction('reset')} 
          className="control-button reset-button"
          disabled={isLoading}
        >
          <span>🔄</span> Reset
        </button>
      </div>
      
      <div className="chaos-section">
        <h4>🌪️ Chaos Engineering</h4>
        <div className="chaos-grid">
          <button 
            onClick={() => handleChaos('KILL_NODE')}
            className="chaos-button danger"
            disabled={!isRunning}
          >
            <span>💀</span> Kill Random Node
          </button>
          <button 
            onClick={() => handleChaos('PARTITION')}
            className="chaos-button warning"
            disabled={!isRunning}
          >
            <span>🔌</span> Network Partition
          </button>
          <button 
            onClick={() => handleChaos('NETWORK_DELAY')}
            className="chaos-button warning"
            disabled={!isRunning}
          >
            <span>⏱️</span> Add Latency
          </button>
          <button 
            onClick={() => handleChaos('RESTORE_ALL')}
            className="chaos-button success"
            disabled={!isRunning}
          >
            <span>🔧</span> Restore All
          </button>
        </div>
      </div>
      
      {isLoading && (
        <div className="panel-loading">
          <div className="spinner-small"></div>
        </div>
      )}
    </div>
  );
};

ControlPanel.propTypes = {
  onSimulationControl: PropTypes.func.isRequired,
  onChaosEvent: PropTypes.func.isRequired,
  isRunning: PropTypes.bool.isRequired
};

export default ControlPanel;