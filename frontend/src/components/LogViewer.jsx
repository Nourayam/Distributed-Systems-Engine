import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';

const LogViewer = ({ events, isRunning }) => {
  const [filter, setFilter] = useState('ALL');
  const [autoScroll, setAutoScroll] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const logEndRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    if (autoScroll && logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [events, autoScroll]);

  const eventTypes = {
    ALL: { label: 'All Events', icon: '📋' },
    SYSTEM: { label: 'System', icon: '⚙️' },
    ELECTION: { label: 'Elections', icon: '🗳️' },
    LEADER_CHANGE: { label: 'Leader Changes', icon: '👑' },
    CHAOS: { label: 'Chaos Events', icon: '🌪️' },
    RECOVERY: { label: 'Recoveries', icon: '🔧' },
    ERROR: { label: 'Errors', icon: '❌' }
  };

  const getEventStyle = (type) => {
    const styles = {
      SYSTEM: 'log-system',
      ELECTION: 'log-election',
      LEADER_CHANGE: 'log-leader',
      CHAOS: 'log-chaos',
      RECOVERY: 'log-recovery',
      ERROR: 'log-error',
      DEFAULT: 'log-default'
    };
    return styles[type] || styles.DEFAULT;
  };

  const formatTimestamp = (timestamp) => {
    return `${timestamp.toFixed(2)}s`;
  };

  const filteredEvents = events.filter(event => {
    const matchesFilter = filter === 'ALL' || event.type === filter;
    const matchesSearch = !searchTerm || 
      event.message.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const handleClearLogs = () => {
    // This would typically call a parent method to clear logs
    console.log('Clear logs requested');
  };

  const handleExportLogs = () => {
    const logData = filteredEvents.map(e => 
      `[${formatTimestamp(e.timestamp)}] ${e.type}: ${e.message}`
    ).join('\n');
    
    const blob = new Blob([logData], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `raft-simulation-logs-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="log-viewer">
      <div className="log-header">
        <h3>📋 Event Log</h3>
        
        <div className="log-controls">
          <div className="log-search">
            <input
              type="text"
              placeholder="Search logs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          
          <select 
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="filter-select"
          >
            {Object.entries(eventTypes).map(([value, { label, icon }]) => (
              <option key={value} value={value}>
                {icon} {label}
              </option>
            ))}
          </select>
          
          <label className="auto-scroll-toggle">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
            />
            <span>Auto-scroll</span>
          </label>
          
          <button 
            onClick={handleExportLogs}
            className="log-action-button"
            title="Export logs"
          >
            📥
          </button>
          
          <button 
            onClick={handleClearLogs}
            className="log-action-button"
            title="Clear logs"
          >
            🗑️
          </button>
        </div>
      </div>
      
      <div className="log-container" ref={containerRef}>
        {filteredEvents.length === 0 ? (
          <div className="log-empty">
            <p>No events to display</p>
            <small>
              {isRunning ? 'Waiting for events...' : 'Start the simulation to see events'}
            </small>
          </div>
        ) : (
          <>
            {filteredEvents.map((event, index) => (
              <div 
                key={index} 
                className={`log-entry ${getEventStyle(event.type)}`}
              >
                <span className="log-icon">
                  {eventTypes[event.type]?.icon || '📝'}
                </span>
                <span className="log-timestamp">
                  [{formatTimestamp(event.timestamp)}]
                </span>
                <span className="log-type">{event.type}</span>
                <span className="log-message">{event.message}</span>
              </div>
            ))}
            <div ref={logEndRef} />
          </>
        )}
      </div>
      
      <div className="log-footer">
        <span className="log-count">
          {filteredEvents.length} {filter !== 'ALL' ? 'filtered' : 'total'} events
        </span>
        <span className="log-status">
          {isRunning ? '🟢 Live' : '🔴 Paused'}
        </span>
      </div>
    </div>
  );
};

LogViewer.propTypes = {
  events: PropTypes.arrayOf(
    PropTypes.shape({
      timestamp: PropTypes.number.isRequired,
      type: PropTypes.string.isRequired,
      message: PropTypes.string.isRequired
    })
  ).isRequired,
  isRunning: PropTypes.bool.isRequired
};

export default LogViewer;