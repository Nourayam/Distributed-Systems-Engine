import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Tooltip } from 'react-tooltip';
import styles from './Node.module.css';

const Node = ({ id, role, term, status, style }) => {
  const [isHovered, setIsHovered] = useState(false);

  const getNodeClasses = () => {
    const base = styles.node;
    const roleClass = styles[`node-${role.toLowerCase()}`];
    const statusClass = status !== 'HEALTHY' ? styles[`node-${status.toLowerCase()}`] : '';
    return `${base} ${roleClass} ${statusClass}`;
  };

  const getRoleEmoji = () => {
    if (status !== 'HEALTHY') return '💀';
    switch (role) {
      case 'LEADER': return '👑';
      case 'CANDIDATE': return '🗳️';
      default: return '🖥️';
    }
  };

  return (
    <>
      <div
        className={getNodeClasses()}
        style={style}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        data-tooltip-id={`node-tooltip-${id}`}
      >
        <div className={styles.nodeContent}>
          <span className={styles.nodeEmoji}>{getRoleEmoji()}</span>
          <span className={styles.nodeId}>#{id}</span>
          <span className={styles.nodeTerm}>T{term}</span>
        </div>
      </div>
      
      <Tooltip id={`node-tooltip-${id}`} place="top" className={styles.tooltip}>
        <div className={styles.tooltipContent}>
          <h4>Node {id}</h4>
          <p>Role: {role}</p>
          <p>Term: {term}</p>
          <p>Status: {status}</p>
          {isHovered && (
            <div className={styles.nodeMetrics}>
              <p>Last heartbeat: 1.2s ago</p>
              <p>Log length: 42 entries</p>
              <p>Commit index: 38</p>
            </div>
          )}
        </div>
      </Tooltip>
    </>
  );
};

Node.propTypes = {
  id: PropTypes.number.isRequired,
  role: PropTypes.oneOf(['LEADER', 'FOLLOWER', 'CANDIDATE']).isRequired,
  term: PropTypes.number.isRequired,
  status: PropTypes.oneOf(['HEALTHY', 'FAILED', 'PARTITIONED']).isRequired,
  style: PropTypes.object
};

Node.defaultProps = {
  style: {}
};

export default Node;