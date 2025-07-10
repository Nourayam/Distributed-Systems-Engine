import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';

const EnhancedNode = ({ 
  id, 
  state, 
  term, 
  status, 
  style, 
  isLeader,
  is_transitioning,
  animationSpeed = 1.0,
  onClick,
  onHover
}) => {
  const [isAnimating, setIsAnimating] = useState(false);
  const [lastState, setLastState] = useState(state);
  const [isHovered, setIsHovered] = useState(false);
  const nodeRef = useRef(null);

  // Handle state transitions
  useEffect(() => {
    if (state !== lastState || is_transitioning) {
      setIsAnimating(true);
      const duration = 1000 / animationSpeed;
      const timer = setTimeout(() => setIsAnimating(false), duration);
      setLastState(state);
      return () => clearTimeout(timer);
    }
  }, [state, lastState, is_transitioning, animationSpeed]);

  const getNodeClasses = () => {
    const classes = ['enhanced-node'];
    
    // State-based classes
    classes.push(`node-${state.toLowerCase()}`);
    
    // Status-based classes
    if (status !== 'HEALTHY') {
      classes.push(`node-${status.toLowerCase()}`);
    }
    
    // Animation classes
    if (isAnimating || is_transitioning) {
      classes.push('node-transitioning');
    }
    if (isHovered) {
      classes.push('node-hovered');
    }
    if (isLeader) {
      classes.push('node-is-leader');
    }
    
    return classes.join(' ');
  };

  const getStateEmoji = () => {
    if (status === 'FAILED') return '💀';
    if (status === 'PARTITIONED') return '🔌';
    
    switch (state) {
      case 'LEADER': return '👑';
      case 'CANDIDATE': return '🗳️';
      case 'FOLLOWER': return '🖥️';
      default: return '🖥️';
    }
  };

  const getStateColour = () => {
    if (status === 'FAILED') return '#ef4444';
    
    switch (state) {
      case 'LEADER': return '#22c55e';
      case 'CANDIDATE': return '#f59e0b';
      case 'FOLLOWER': return '#3b82f6';
      default: return '#666666';
    }
  };

  return (
    <div
      ref={nodeRef}
      className={getNodeClasses()}
      style={{
        ...style,
        '--node-colour': getStateColour(),
        '--animation-speed': `${animationSpeed}s`
      }}
      onClick={() => onClick && onClick(id)}
      onMouseEnter={() => {
        setIsHovered(true);
        onHover && onHover(id, true);
      }}
      onMouseLeave={() => {
        setIsHovered(false);
        onHover && onHover(id, false);
      }}
      title={`Node ${id} - ${state} (Term ${term})`}
    >
      <div className="node-content">
        <div className="node-emoji">{getStateEmoji()}</div>
        <div className="node-id">#{id}</div>
        <div className="node-term">T{term}</div>
        <div className="node-state-label">{state}</div>
      </div>
      
      {isLeader && (
        <div className="leader-crown">
          <span>👑</span>
        </div>
      )}
      
      {state === 'CANDIDATE' && (
        <div className="candidate-rings">
          <div className="ring ring-1"></div>
          <div className="ring ring-2"></div>
        </div>
      )}
      
      {(isAnimating || is_transitioning) && (
        <div className="transition-effect">
          <div className="pulse-ring"></div>
        </div>
      )}
    </div>
  );
};

EnhancedNode.propTypes = {
  id: PropTypes.number.isRequired,
  state: PropTypes.oneOf(['LEADER', 'FOLLOWER', 'CANDIDATE']).isRequired,
  term: PropTypes.number.isRequired,
  status: PropTypes.oneOf(['HEALTHY', 'FAILED', 'PARTITIONED']).isRequired,
  style: PropTypes.object,
  isLeader: PropTypes.bool,
  is_transitioning: PropTypes.bool,
  animationSpeed: PropTypes.number,
  onClick: PropTypes.func,
  onHover: PropTypes.func
};

export default EnhancedNode;