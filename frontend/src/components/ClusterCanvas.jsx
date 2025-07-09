import React, { useRef, useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import Node from './Node';
import { useSimulation } from '../contexts/SimulationContext';

const ClusterCanvas = ({ nodes, messages, leaderId }) => {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const animationRef = useRef(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);

  // Calculate optimal positions for nodes
  const calculatePositions = (count, width, height) => {
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.35;
    
    return Array.from({ length: count }, (_, i) => {
      const angle = (2 * Math.PI * i) / count - Math.PI / 2;
      return {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      };
    });
  };

  // Animate messages with proper cleanup
  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const rect = container.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    const ctx = canvas.getContext('2d');
    let animationFrame;
    
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      if (messages.length > 0) {
        const positions = calculatePositions(nodes.length, canvas.width, canvas.height);
        
        // Draw connection lines first (behind messages)
        ctx.save();
        ctx.globalAlpha = 0.1;
        nodes.forEach((node, i) => {
          nodes.forEach((otherNode, j) => {
            if (i < j) {
              const from = positions[i];
              const to = positions[j];
              ctx.beginPath();
              ctx.moveTo(from.x, from.y);
              ctx.lineTo(to.x, to.y);
              ctx.strokeStyle = '#333333';
              ctx.lineWidth = 1;
              ctx.stroke();
            }
          });
        });
        ctx.restore();
        
        // Draw animated messages
        messages.forEach(msg => {
          const fromNode = nodes.find(n => n.id === msg.from);
          const toNode = nodes.find(n => n.id === msg.to);
          if (!fromNode || !toNode) return;

          const fromPos = positions[fromNode.id];
          const toPos = positions[toNode.id];
          
          // Calculate animation progress
          const elapsed = Date.now() - msg.timestamp;
          const duration = 1000;
          const progress = Math.min(elapsed / duration, 1);
          
          // Interpolate position
          const currentX = fromPos.x + (toPos.x - fromPos.x) * progress;
          const currentY = fromPos.y + (toPos.y - fromPos.y) * progress;
          
          // Draw message path
          ctx.save();
          ctx.globalAlpha = 1 - progress * 0.5;
          ctx.beginPath();
          ctx.setLineDash([12, 6]);
          ctx.lineDashOffset = -(Date.now() / 40) % 18;
          ctx.moveTo(fromPos.x, fromPos.y);
          ctx.lineTo(toPos.x, toPos.y);
          
          // Colour based on message type
          const colours = {
            HEARTBEAT: '#22c55e',
            VOTE_REQUEST: '#f59e0b',
            VOTE_RESPONSE: '#3b82f6',
            APPEND_ENTRIES: '#8b5cf6'
          };
          
          ctx.strokeStyle = colours[msg.type] || '#666666';
          ctx.lineWidth = 2;
          ctx.stroke();
          
          // Draw message packet
          ctx.beginPath();
          ctx.arc(currentX, currentY, 6, 0, 2 * Math.PI);
          ctx.fillStyle = ctx.strokeStyle;
          ctx.fill();
          
          ctx.restore();
        });
      }
      
      animationFrame = requestAnimationFrame(animate);
    };
    
    animate();
    
    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [nodes, messages]);

  const handleNodeClick = (nodeId) => {
    setSelectedNode(nodeId === selectedNode ? null : nodeId);
  };

  const handleNodeHover = (nodeId, isHovering) => {
    setHoveredNode(isHovering ? nodeId : null);
  };

  const positions = calculatePositions(
    nodes.length,
    containerRef.current?.clientWidth || 800,
    containerRef.current?.clientHeight || 500
  );

  return (
    <div className="cluster-canvas" ref={containerRef}>
      <canvas 
        ref={canvasRef} 
        className="message-canvas"
      />
      
      {nodes.map((node, index) => (
        <Node
          key={node.id}
          {...node}
          isLeader={node.id === leaderId}
          isSelected={node.id === selectedNode}
          isHovered={node.id === hoveredNode}
          onClick={handleNodeClick}
          onHover={handleNodeHover}
          style={{
            position: 'absolute',
            left: `${positions[index]?.x || 0}px`,
            top: `${positions[index]?.y || 0}px`,
            transform: 'translate(-50%, -50%)'
          }}
        />
      ))}
      
      <div className="cluster-info">
        <div className="cluster-stats">
          <span>🖥️ Nodes: {nodes.length}</span>
          <span>📨 Messages: {messages.length}</span>
          <span>🔗 Consensus: {leaderId !== null ? 'Established' : 'Pending'}</span>
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
      status: PropTypes.string.isRequired
    })
  ).isRequired,
  messages: PropTypes.arrayOf(
    PropTypes.shape({
      from: PropTypes.number.isRequired,
      to: PropTypes.number.isRequired,
      type: PropTypes.string.isRequired,
      timestamp: PropTypes.number.isRequired
    })
  ).isRequired,
  leaderId: PropTypes.number
};

export default ClusterCanvas;