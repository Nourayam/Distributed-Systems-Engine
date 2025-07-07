import React from 'react';
import PropTypes from 'prop-types';
import styles from './LogViewer.module.css';

const LogViewer = ({ events, onFilterChange }) => {
  const getEventColor = (type) => {
    const colors = {
      ELECTION: 'text-amber-400',
      LEADER_CHANGE: 'text-green-400',
      PARTITION: 'text-red-400',
      RECOVERY: 'text-blue-400',
      DEFAULT: 'text-gray-300'
    };
    return colors[type] || colors.DEFAULT;
  };

  return (
    <div className={styles.container}>
      <div className={styles.filterBar}>
        <select 
          onChange={(e) => onFilterChange(e.target.value)}
          className={styles.filterSelect}
        >
          <option value="ALL">All Events</option>
          <option value="ELECTION">Elections</option>
          <option value="LEADER_CHANGE">Leader Changes</option>
          <option value="PARTITION">Partitions</option>
          <option value="RECOVERY">Recoveries</option>
        </select>
      </div>
      <div className={styles.logContainer}>
        {events.map((event, index) => (
          <div 
            key={index} 
            className={`${styles.logEntry} ${getEventColor(event.type)}`}
          >
            <span className={styles.timestamp}>[{event.timestamp}s]</span>
            <span className={styles.message}>{event.message}</span>
          </div>
        ))}
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