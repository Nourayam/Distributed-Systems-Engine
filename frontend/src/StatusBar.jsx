import React from 'react';
import PropTypes from 'prop-types';

const StatusBar = ({ currentTerm, leaderId, simulationTime, isRunning }) => {
  const formatTime = (time) => {
    return `${time.toFixed(1)}s`;
  };

  const getStatusIndicator = () => {
    return isRunning ? '🟢' : '🔴';
  };

  return (
    <div className="status-bar">
      <div className="status-section">
        <div className="status-item primary">
          <span className="status-indicator">{getStatusIndicator()}</span>
          <span className="status-label">Status:</span>
          <span className={`status-value ${isRunning ? 'running' : 'stopped'}`}>
            {isRunning ? 'RUNNING' : 'STOPPED'}
          </span>
        </div>
      </div>
      
      <div className="status-section">
        <div className="status-item">
          <span className="status-label">⏱ Time:</span>
          <span className="status-value">{formatTime(simulationTime)}</span>
        </div>
        
        <div className="status-item">
          <span className="status-label">📊 Term:</span>
          <span className="status-value term-badge">{currentTerm}</span>
        </div>
        
        <div className="status-item">
          <span className="status-label">👑 Leader:</span>
          <span className="status-value leader-badge">
            {leaderId !== null ? `Node ${leaderId}` : 'None'}
          </span>
        </div>
      </div>
      
      <div className="status-section">
        <div className="network-health">
          <span className="status-label">🌐 Network:</span>
          <div className="health-dots">
            <span className="health-dot healthy"></span>
            <span className="health-dot healthy"></span>
            <span className="health-dot healthy"></span>
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
  isRunning: PropTypes.bool.isRequired
};

StatusBar.defaultProps = {
  leaderId: null
};

export default StatusBar;