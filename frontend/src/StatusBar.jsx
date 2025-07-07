import React from 'react';
import PropTypes from 'prop-types';
import styles from './StatusBar.module.css';

const StatusBar = ({ currentTerm, leaderId, simulationTime, isRunning }) => {
  return (
    <div className={styles.statusBar}>
      <div className={styles.statusItem}>
        <span className={styles.label}>Status:</span>
        <span className={`${styles.value} ${isRunning ? styles.running : styles.stopped}`}>
          {isRunning ? 'RUNNING' : 'STOPPED'}
        </span>
      </div>
      <div className={styles.statusItem}>
        <span className={styles.label}>Time:</span>
        <span className={styles.value}>{simulationTime.toFixed(1)}s</span>
      </div>
      <div className={styles.statusItem}>
        <span className={styles.label}>Term:</span>
        <span className={styles.value}>{currentTerm}</span>
      </div>
      <div className={styles.statusItem}>
        <span className={styles.label}>Leader:</span>
        <span className={styles.value}>
          {leaderId !== null ? `Node ${leaderId}` : 'None'}
        </span>
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