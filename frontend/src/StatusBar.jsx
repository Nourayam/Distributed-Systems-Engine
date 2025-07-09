import React from 'react';
import PropTypes from 'prop-types';

const StatusBar = ({ 
  currentTerm, 
  leaderId, 
  simulationTime, 
  isRunning,
  nodeCount 
}) => {
  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = (time % 60).toFixed(1);
    return minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
  };

  const getNetworkHealth = () => {
    return isRunning ? 
      { status: 'healthy', colour: '#22c55e' } : 
      { status: 'inactive', colour: '#666666' };
  };

  const networkHealth = getNetworkHealth();

  return (
    <div className="status-bar">
      <div className="status-section">
        <div className="status-item primary">
          <span className="status-indicator">
            {isRunning ? '🟢' : '🔴'}
          </span>
          <span className="status-label">Status:</span>
          <span className={`status-value ${isRunning ? 'running' : 'stopped'}`}>
            {isRunning ? 'RUNNING' : 'STOPPED'}
          </span>
        </div>
      </div>
      
      <div className="status-section">
        <div className="status-item">
          <span className="status-label">⏱️ Time:</span>
          <span className="status-value">{formatTime(simulationTime)}</span>
        </div>
        
        <div className="status-item">
          <span className="status-label">📊 Term:</span>
          <span className="status-value status-badge term-badge">
            {currentTerm}
          </span>
        </div>
        
        <div className="status-item">
          <span className="status-label">👑 Leader:</span>
          <span className="status-value status-badge leader-badge">
            {leaderId !== null ? `Node ${leaderId}` : 'None'}
          </span>
        </div>
        
        <div className="status-item">
          <span className="status-label">🖥️ Nodes:</span>
          <span className="status-value">{nodeCount}</span>
        </div>
      </div>
      
      <div className="status-section">
        <div className="network-health">
          <span className="status-label">🌐 Network:</span>
          <div className="health-indicator">
            <div 
              className="health-dot"
              style={{ backgroundColor: networkHealth.colour }}
            />
            <span className="health-text">{networkHealth.status}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

StatusBar.propTypes = {
  currentTerm: PropTypes.number.isRequired,
  leaderId: PropTypes.number,
  simulationTime: PropTypes.number.isRequired,
  isRunning: PropTypes.bool.isRequired,
  nodeCount: PropTypes.number.isRequired
};

StatusBar.defaultProps = {
  leaderId: null
};

export default StatusBar;