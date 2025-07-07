import React, { useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import Node from './Node';
import styles from './ClusterCanvas.module.css';

const ClusterCanvas = ({ nodes, messages }) => {
  const canvasRef = useRef(null);

  // Calculate positions for nodes in a circle
  const calculatePositions = (count, radius) => {
    const center = { x: 250, y: 250 };
    const angleStep = (2 * Math.PI) / count;
    return Array.from({ length: count }, (_, i) => ({
      x: center.x + radius * Math.cos(i * angleStep),
      y: center.y + radius * Math.sin(i * angleStep)
    }));
  };

  // Draw message arrows between nodes
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    messages.forEach(msg => {
      const fromNode = nodes.find(n => n.id === msg.from);
      const toNode = nodes.find(n => n.id === msg.to);
      if (!fromNode || !toNode) return;

      const positions = calculatePositions(nodes.length, 150);
      const fromPos = positions[fromNode.id];
      const toPos = positions[toNode.id];

      ctx.beginPath();
      ctx.moveTo(fromPos.x, fromPos.y);
      ctx.lineTo(toPos.x, toPos.y);
      ctx.strokeStyle = msg.type === 'HEARTBEAT' ? '#4ade80' : '#fbbf24';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Draw arrowhead
      const headLength = 10;
      const angle = Math.atan2(toPos.y - fromPos.y, toPos.x - fromPos.x);
      ctx.beginPath();
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
      ctx.fillStyle = msg.type === 'HEARTBEAT' ? '#4ade80' : '#fbbf24';
      ctx.fill();
    });
  }, [nodes, messages]);

  const positions = calculatePositions(nodes.length, 150);

  return (
    <div className={styles.clusterContainer}>
      <canvas 
        ref={canvasRef} 
        width={500} 
        height={500} 
        className={styles.messageCanvas}
      />
      {nodes.map((node, index) => (
        <Node
          key={node.id}
          id={node.id}
          role={node.role}
          term={node.term}
          status={node.status}
          style={{
            position: 'absolute',
            left: `${positions[index].x - 25}px`,
            top: `${positions[index].y - 25}px`
          }}
        />
      ))}
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