import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

const Node = ({ id, role, term, status, style, onClick }) => {
  const [isAnimating, setIsAnimating] = useState(false);
  const [lastRole, setLastRole] = useState(role);

  // Trigger animation on role change
  useEffect(() => {
    if (role !== lastRole) {
      setIsAnimating(true);
      const timer = setTimeout(() => setIsAnimating(false), 1000);
      setLastRole(role);
      return () => clearTimeout(timer);
    }
  }, [role, lastRole]);

  const getNodeClasses = () => {
    let classes = ['node', `node-${role.toLowerCase()}`];
    
    if (status !== 'HEALTHY') {
      classes.push(`node-${status.toLowerCase()}`);
    }
    
    if (isAnimating) {
      classes.push('node-transitioning');
    }
    
    return classes.join(' ');
  };

  const getRoleEmoji = () => {
    if (status === 'FAILED') return '💀';
    if (status === 'PARTITIONED') return '🔌';
    
    switch (role) {
      case 'LEADER': return '👑';
      case 'CANDIDATE': return '🗳️';
      default: return '🖥️';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'FAILED': return 'CRASHED';
      case 'PARTITIONED': return 'ISOLATED';
      default: return role;
    }
  };

  return (
    <div
      className={getNodeClasses()}
      style={style}
      onClick={() => onClick && onClick(id)}
      title={`Node ${id} - ${getStatusText()} (Term ${term})`}
    >
      <div className="node-content">
        <div className="node-emoji">{getRoleEmoji()}</div>
        <div className="node-id">#{id}</div>
        <div className="node-term">T{term}</div>
        <div className="node-status">{getStatusText()}</div>
      </div>
      
      {role === 'LEADER' && (
        <div className="node-glow"></div>
      )}
      
      {role === 'CANDIDATE' && (
        <div className="node-pulse"></div>
      )}
    </div>
  );
};

Node.propTypes = {
  id: PropTypes.number.isRequired,
  role: PropTypes.oneOf(['LEADER', 'FOLLOWER', 'CANDIDATE']).isRequired,
  term: PropTypes.number.isRequired,
  status: PropTypes.oneOf(['HEALTHY', 'FAILED', 'PARTITIONED']).isRequired,
  style: PropTypes.object,
  onClick: PropTypes.func
};

Node.defaultProps = {
  style: {},
  onClick: null
};

export default Node;