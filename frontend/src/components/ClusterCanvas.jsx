import React, { useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import Node from './Node';

const ClusterCanvas = ({ nodes, messages }) => {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);

  // Calculate positions for nodes in a circle
  const calculatePositions = (count, containerWidth = 600, containerHeight = 400) => {
    const centerX = containerWidth / 2;
    const centerY = containerHeight / 2;
    const radius = Math.min(containerWidth, containerHeight) / 3;
    
    return Array.from({ length: count }, (_, i) => {
      const angle = (2 * Math.PI * i) / count - Math.PI / 2; // Start from top
      return {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      };
    });
  };

  // Draw message arrows between nodes
  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const rect = container.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (messages.length === 0) return;

    const positions = calculatePositions(nodes.length, canvas.width, canvas.height);

    messages.forEach(msg => {
      const fromNode = nodes.find(n => n.id === msg.from);
      const toNode = nodes.find(n => n.id === msg.to);
      if (!fromNode || !toNode) return;

      const fromPos = positions[fromNode.id];
      const toPos = positions[toNode.id];

      // Draw animated arrow
      ctx.beginPath();
      ctx.setLineDash([8, 4]);
      ctx.lineDashOffset = -(Date.now() / 50) % 12;
      ctx.moveTo(fromPos.x, fromPos.y);
      ctx.lineTo(toPos.x, toPos.y);
      
      // Color based on message type
      switch (msg.type) {
        case 'HEARTBEAT':
          ctx.strokeStyle = '#4ade80';
          break;
        case 'VOTE_REQUEST':
          ctx.strokeStyle = '#fbbf24';
          break;
        case 'VOTE_RESPONSE':
          ctx.strokeStyle = '#60a5fa';
          break;
        default:
          ctx.strokeStyle = '#9ca3af';
      }
      
      ctx.lineWidth = 2;
      ctx.stroke();

      // Draw arrowhead
      const headLength = 12;
      const angle = Math.atan2(toPos.y - fromPos.y, toPos.x - fromPos.x);
      
      ctx.beginPath();
      ctx.setLineDash([]);
      ctx.moveTo(toPos.x, toPos.y);
      ctx.lineTo(
        toPos.x - headLength * Math.cos(angle - Math.PI / 6),
        toPos.y - headLength * Math.sin(angle - Math.PI / 6)
      );
      ctx.lineTo(
        toPos.x - headLength * Math.cos(angle + Math.PI / 6),
        toPos.y - headLength * Math.sin(angle + Math.PI / 6)
      );
      ctx.closePath();
      ctx.fillStyle = ctx.strokeStyle;
      ctx.fill();
    });
  }, [nodes, messages]);

  const positions = calculatePositions(
    nodes.length, 
    containerRef.current?.clientWidth || 600, 
    containerRef.current?.clientHeight || 400
  );

  const handleNodeClick = (nodeId) => {
    console.log(`Node ${nodeId} clicked`);
    // Future: Add node inspection modal
  };

  return (
    <div className="cluster-canvas" ref={containerRef}>
      <canvas 
        ref={canvasRef} 
        className="message-canvas"
      />
      
      {nodes.map((node, index) => (
        <Node
          key={node.id}
          id={node.id}
          role={node.role}
          term={node.term}
          status={node.status}
          onClick={handleNodeClick}
          style={{
            position: 'absolute',
            left: `${positions[index]?.x - 40 || 0}px`,
            top: `${positions[index]?.y - 40 || 0}px`,
            transform: 'translate(-50%, -50%)'
          }}
        />
      ))}
      
      <div className="cluster-info">
        <div className="cluster-stats">
          <span>Nodes: {nodes.length}</span>
          <span>Active Messages: {messages.length}</span>
        </div>
      </div>
    </div>
  );
};

ClusterCanvas.propTypes = {
  nodes: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      role: PropTypes.string.isRequired,
      term: PropTypes.number.isRequired,
      status: PropTypes.string.isRequired
    })
  ).isRequired,
  messages: PropTypes.arrayOf(
    PropTypes.shape({
      from: PropTypes.number.isRequired,
      to: PropTypes.number.isRequired,
      type: PropTypes.string.isRequired
    })
  ).isRequired
};

export default ClusterCanvas;