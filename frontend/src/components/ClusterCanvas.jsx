import React, { useRef, useEffect, useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import EnhancedNode from './Node';

const ClusterCanvas = ({ nodes, messages, leaderId, animationSpeed = 1.0 }) => {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const animationRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  //calculates optimal positions for nodes in a circle
  const calculatePositions = useCallback((count, width, height) => {
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.3;
    
    return Array.from({ length: count }, (_, i) => {
      const angle = (2 * Math.PI * i) / count - Math.PI / 2;
      return {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      };
    });
  }, []);

  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setDimensions({ width: rect.width, height: rect.height });
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  //message animation
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    canvas.width = dimensions.width;
    canvas.height = dimensions.height;

    const ctx = canvas.getContext('2d');
    const positions = calculatePositions(nodes.length, dimensions.width, dimensions.height);
    
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      //draw connection network (faded)
      ctx.save();
      ctx.globalAlpha = 0.08;
      ctx.strokeStyle = '#333333';
      ctx.lineWidth = 1;
      
      for (let i = 0; i < positions.length; i++) {
        for (let j = i + 1; j < positions.length; j++) {
          ctx.beginPath();
          ctx.moveTo(positions[i].x, positions[i].y);
          ctx.lineTo(positions[j].x, positions[j].y);
          ctx.stroke();
        }
      }
      ctx.restore();
      
      //draw animated messages
      const currentTime = Date.now();
      
      messages.forEach(msg => {
        const fromNode = nodes.find(n => n.id === msg.from);
        const toNode = nodes.find(n => n.id === msg.to);
        if (!fromNode || !toNode || fromNode.id >= positions.length || toNode.id >= positions.length) return;

        const fromPos = positions[fromNode.id];
        const toPos = positions[toNode.id];
        
        //calculates animation progress
        const elapsed = (currentTime - msg.timestamp * 1000) * animationSpeed;
        const duration = (msg.travel_time || 1000) / animationSpeed;
        const progress = Math.min(elapsed / duration, 1);
        
        if (progress < 1) {
          const easeProgress = 1 - Math.pow(1 - progress, 3);
          
          //calculates the current position
          const currentX = fromPos.x + (toPos.x - fromPos.x) * easeProgress;
          const currentY = fromPos.y + (toPos.y - fromPos.y) * easeProgress;
          
          //draws message trail
          ctx.save();
          ctx.globalAlpha = 0.8 * (1 - progress * 0.5);
          
          //diff colours for different message types
          const messageColours = {
            'HEARTBEAT': '#22c55e',
            'VOTE_REQUEST': '#f59e0b',
            'VOTE_RESPONSE': '#3b82f6',
            'APPEND_ENTRIES': '#8b5cf6'
          };
          
          const colour = messageColours[msg.type] || '#666666';
          
          //draw animated dashed line
          ctx.beginPath();
          ctx.setLineDash([8, 4]);
          ctx.lineDashOffset = -((currentTime * animationSpeed) / 30) % 12;
          ctx.moveTo(fromPos.x, fromPos.y);
          ctx.lineTo(currentX, currentY);
          ctx.strokeStyle = colour;
          ctx.lineWidth = 3;
          ctx.stroke();
          
          //draw message packet
          ctx.beginPath();
          ctx.arc(currentX, currentY, 8, 0, 2 * Math.PI);
          ctx.fillStyle = colour;
          ctx.shadowColor = colour;
          ctx.shadowBlur = 10;
          ctx.fill();
          
          //draw message type indicator
          ctx.fillStyle = '#ffffff';
          ctx.font = '8px Inter';
          ctx.textAlign = 'center';
          ctx.fillText(msg.type.charAt(0), currentX, currentY + 3);
          
          ctx.restore();
        }
      });
      
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animate();
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [nodes, messages, dimensions, animationSpeed, calculatePositions]);

  const positions = calculatePositions(nodes.length, dimensions.width, dimensions.height);

  return (
    <div className="cluster-canvas" ref={containerRef}>
      <canvas 
        ref={canvasRef} 
        className="message-canvas"
        style={{ position: 'absolute', top: 0, left: 0, zIndex: 1 }}
      />
      
      <div className="nodes-container" style={{ position: 'relative', zIndex: 2 }}>
        {nodes.map((node, index) => (
          <EnhancedNode
            key={node.id}
            {...node}
            isLeader={node.id === leaderId}
            animationSpeed={animationSpeed}
            style={{
              position: 'absolute',
              left: `${positions[index]?.x || 0}px`,
              top: `${positions[index]?.y || 0}px`,
              transform: 'translate(-50%, -50%)'
            }}
          />
        ))}
      </div>
      
      <div className="cluster-info">
        <div className="network-stats">
          <div className="stat-item">
            <span className="stat-icon">🖥️</span>
            <span className="stat-value">{nodes.length}</span>
            <span className="stat-label">Nodes</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">📨</span>
            <span className="stat-value">{messages.length}</span>
            <span className="stat-label">Messages</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">🔗</span>
            <span className="stat-value">{leaderId !== null ? 'YES' : 'NO'}</span>
            <span className="stat-label">Consensus</span>
          </div>
        </div>
      </div>
    </div>
  );
};

ClusterCanvas.propTypes = {
  nodes: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      state: PropTypes.string.isRequired,
      term: PropTypes.number.isRequired,
      status: PropTypes.string.isRequired,
      is_transitioning: PropTypes.bool
    })
  ).isRequired,
  messages: PropTypes.arrayOf(
    PropTypes.shape({
      from: PropTypes.number.isRequired,
      to: PropTypes.number.isRequired,
      type: PropTypes.string.isRequired,
      timestamp: PropTypes.number.isRequired,
      travel_time: PropTypes.number
    })
  ).isRequired,
  leaderId: PropTypes.number,
  animationSpeed: PropTypes.number
};

export default ClusterCanvas;