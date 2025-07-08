import React, { useState } from 'react';
import PropTypes from 'prop-types';

const ControlPanel = ({ onSimulationChange, onChaosEvent }) => {
  const [params, setParams] = useState({
    nodeCount: 5,
    maxTime: 60,
    messageDropRate: 0.1
  });
  const [isExpanded, setIsExpanded] = useState(false);

  const handleParamChange = (e) => {
    const { name, value, type } = e.target;
    setParams(prev => ({
      ...prev,
      [name]: type === 'number' ? 
        Math.min(Math.max(parseFloat(value), 0), name === 'nodeCount' ? 7 : Infinity) : 
        parseFloat(value)
    }));
  };

  const handleStart = () => {
    onSimulationChange('start');
  };

  const handleStop = () => {
    onSimulationChange('stop');
  };

  const handleReset = () => {
    onSimulationChange('reset');
  };

  const injectChaos = (type, nodeId = null) => {
    onChaosEvent(type, nodeId);
  };

  return (
    <div className="control-panel">
      <div className="panel-header">
        <h3>Simulation Controls</h3>
        <button 
          className="expand-button"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? '▼' : '▶'}
        </button>
      </div>
      
      {isExpanded && (
        <div className="panel-content">
          <div className="param-group">
            <label className="param-label">
              Node Count (3-7):
              <input
                type="number"
                name="nodeCount"
                min="3"
                max="7"
                value={params.nodeCount}
                onChange={handleParamChange}
                className="param-input"
              />
            </label>
            
            <label className="param-label">
              Max Time (s):
              <input
                type="number"
                name="maxTime"
                min="10"
                max="300"
                step="10"
                value={params.maxTime}
                onChange={handleParamChange}
                className="param-input"
              />
            </label>
            
            <label className="param-label">
              Message Drop Rate:
              <div className="range-container">
                <input
                  type="range"
                  name="messageDropRate"
                  min="0"
                  max="0.5"
                  step="0.01"
                  value={params.messageDropRate}
                  onChange={handleParamChange}
                  className="param-range"
                />
                <span className="range-value">{(params.messageDropRate * 100).toFixed(0)}%</span>
              </div>
            </label>
          </div>
        </div>
      )}
      
      <div className="button-group">
        <button onClick={handleStart} className="control-button start-button">
          ▶ Start
        </button>
        <button onClick={handleStop} className="control-button stop-button">
          ⏸ Stop
        </button>
        <button onClick={handleReset} className="control-button reset-button">
          🔄 Reset
        </button>
      </div>
      
      <div className="chaos-section">
        <h4>Chaos Engineering</h4>
        <div className="chaos-group">
          <button 
            onClick={() => injectChaos('KILL_NODE', Math.floor(Math.random() * params.nodeCount))}
            className="chaos-button danger"
          >
            💀 Kill Random Node
          </button>
          <button 
            onClick={() => injectChaos('PARTITION')}
            className="chaos-button warning"
          >
            🔌 Network Partition
          </button>
          <button 
            onClick={() => injectChaos('RESTORE_ALL')}
            className="chaos-button success"
          >
            🔧 Restore All
          </button>
        </div>
      </div>
    </div>
  );
};

ControlPanel.propTypes = {
  onSimulationChange: PropTypes.func.isRequired,
  onChaosEvent: PropTypes.func.isRequired
};

export default ControlPanel;