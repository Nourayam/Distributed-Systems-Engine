import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';

const LogViewer = ({ events, onFilterChange }) => {
  const [filter, setFilter] = useState('ALL');
  const [autoScroll, setAutoScroll] = useState(true);
  const logEndRef = useRef(null);

  // Auto-scroll to bottom when new events arrive
  useEffect(() => {
    if (autoScroll && logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [events, autoScroll]);

  const handleFilterChange = (newFilter) => {
    setFilter(newFilter);
    onFilterChange(newFilter);
  };

  const getEventIcon = (type) => {
    const icons = {
      ELECTION: '🗳️',
      LEADER_CHANGE: '👑',
      PARTITION: '🔌',
      RECOVERY: '🔧',
      HEARTBEAT: '💓',
      VOTE: '✋',
      DEFAULT: '📝'
    };
    return icons[type] || icons.DEFAULT;
  };

  const getEventColor = (type) => {
    const colors = {
      ELECTION: 'log-election',
      LEADER_CHANGE: 'log-leader',
      PARTITION: 'log-partition',
      RECOVERY: 'log-recovery',
      HEARTBEAT: 'log-heartbeat',
      VOTE: 'log-vote',
      DEFAULT: 'log-default'
    };
    return colors[type] || colors.DEFAULT;
  };

  const formatTimestamp = (timestamp) => {
    return `${timestamp.toFixed(2)}s`;
  };

  return (
    <div className="log-viewer">
      <div className="log-header">
        <h3>Event Log</h3>
        <div className="log-controls">
          <select 
            value={filter}
            onChange={(e) => handleFilterChange(e.target.value)}
            className="filter-select"
          >
            <option value="ALL">All Events</option>
            <option value="ELECTION">Elections</option>
            <option value="LEADER_CHANGE">Leader Changes</option>
            <option value="PARTITION">Partitions</option>
            <option value="RECOVERY">Recoveries</option>
          </select>
          
          <label className="auto-scroll-toggle">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
            />
            Auto-scroll
          </label>
        </div>
      </div>
      
      <div className="log-container">
        {events.length === 0 ? (
          <div className="log-empty">
            <p>No events to display</p>
            <small>Start the simulation to see RAFT consensus events</small>
          </div>
        ) : (
          events.map((event, index) => (
            <div 
              key={index} 
              className={`log-entry ${getEventColor(event.type)}`}
            >
              <span className="log-icon">{getEventIcon(event.type)}</span>
              <span className="log-timestamp">[{formatTimestamp(event.timestamp)}]</span>
              <span className="log-message">{event.message}</span>
            </div>
          ))
        )}
        <div ref={logEndRef} />
      </div>
      
      <div className="log-footer">
        <small>{events.length} total events</small>
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
  onFilterChange: PropTypes.func.isRequired
};

export default LogViewer;