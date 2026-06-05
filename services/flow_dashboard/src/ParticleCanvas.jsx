import React, { useEffect, useRef } from 'react';

const ParticleCanvas = ({ ingestionRate, consumerStatus }) => {
  const canvasRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let animationFrameId;
    
    // Resize canvas to match parent
    const resizeCanvas = () => {
      const parent = canvas.parentElement;
      canvas.width = parent.clientWidth;
      canvas.height = parent.clientHeight;
    };
    
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    
    // Nodes
    const nodes = [
      { id: 'mbta', label: 'MBTA API', x: 0.15, y: 0.5 },
      { id: 'kafka', label: 'REDPANDA KAFKA', x: 0.5, y: 0.5 },
      { id: 'db', label: 'SUPABASE POSTGRES', x: 0.85, y: 0.5 }
    ];
    
    // Particles array
    let particles = [];
    
    // Matrix Green Color
    const MATRIX_GREEN = '#00ff41';
    const DIM_GREEN = 'rgba(0, 255, 65, 0.2)';
    
    const drawNode = (node, width, height) => {
      const x = node.x * width;
      const y = node.y * height;
      
      // Draw outer glow
      ctx.beginPath();
      ctx.arc(x, y, 30, 0, Math.PI * 2);
      ctx.fillStyle = DIM_GREEN;
      ctx.fill();
      
      // Draw inner core
      ctx.beginPath();
      ctx.arc(x, y, 8, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.fill();
      
      // Draw text
      ctx.fillStyle = '#888888';
      ctx.font = '12px "Roboto Mono", monospace';
      ctx.textAlign = 'center';
      ctx.fillText(node.label, x, y - 45);
    };
    
    const drawConnection = (node1, node2, width, height) => {
      const x1 = node1.x * width;
      const y1 = node1.y * height;
      const x2 = node2.x * width;
      const y2 = node2.y * height;
      
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.strokeStyle = '#1a1a1a';
      ctx.lineWidth = 2;
      ctx.stroke();
    };
    
    class Particle {
      constructor(startNode, endNode, width, height, speed) {
        this.startX = startNode.x * width;
        this.startY = startNode.y * height;
        this.endX = endNode.x * width;
        this.endY = endNode.y * height;
        this.progress = 0;
        this.speed = speed;
        // Jitter for organic look
        this.offsetY = (Math.random() - 0.5) * 40; 
        this.size = Math.random() * 2 + 1.5;
        this.opacity = Math.random() * 0.5 + 0.5;
      }
      
      update() {
        this.progress += this.speed;
        return this.progress >= 1;
      }
      
      draw(ctx) {
        const x = this.startX + (this.endX - this.startX) * this.progress;
        
        // Sine wave interpolation for natural flow
        const arc = Math.sin(this.progress * Math.PI);
        const y = this.startY + (this.endY - this.startY) * this.progress + (this.offsetY * arc);
        
        ctx.beginPath();
        ctx.arc(x, y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0, 255, 65, ${this.opacity})`;
        ctx.shadowBlur = 10;
        ctx.shadowColor = MATRIX_GREEN;
        ctx.fill();
        ctx.shadowBlur = 0; // reset
      }
    }
    
    let lastSpawnTime = 0;
    
    const render = (time) => {
      ctx.fillStyle = '#000000';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Draw Connections
      drawConnection(nodes[0], nodes[1], canvas.width, canvas.height);
      drawConnection(nodes[1], nodes[2], canvas.width, canvas.height);
      
      // Draw Nodes
      nodes.forEach(n => drawNode(n, canvas.width, canvas.height));
      
      // Spawn particles based on ingestion rate
      // Base rate: 100 records = ~1 particle per 100ms
      const isHealthy = consumerStatus === 'Healthy';
      const spawnInterval = ingestionRate > 0 ? Math.max(10, 10000 / ingestionRate) : 500;
      
      if (isHealthy && time - lastSpawnTime > spawnInterval) {
        // Spawn MBTA -> Kafka
        particles.push(new Particle(nodes[0], nodes[1], canvas.width, canvas.height, 0.01 + Math.random()*0.01));
        
        // Spawn Kafka -> DB
        // Add a slight delay conceptually, but we just spawn independently
        particles.push(new Particle(nodes[1], nodes[2], canvas.width, canvas.height, 0.01 + Math.random()*0.01));
        
        lastSpawnTime = time;
      }
      
      // Update & Draw Particles
      particles = particles.filter(p => !p.update());
      particles.forEach(p => p.draw(ctx));
      
      animationFrameId = requestAnimationFrame(render);
    };
    
    animationFrameId = requestAnimationFrame(render);
    
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationFrameId);
    };
  }, [ingestionRate, consumerStatus]);

  return <canvas ref={canvasRef} />;
};

export default ParticleCanvas;
