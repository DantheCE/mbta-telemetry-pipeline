import React, { useState, useEffect } from 'react';
import ParticleCanvas from './ParticleCanvas';

function App() {
  const [metrics, setMetrics] = useState({
    ingestionRate: 0,
    consumerStatus: 'Offline'
  });

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch('http://localhost:8080/api/v1/metrics');
        const json = await response.json();
        if (response.ok && json.data) {
          setMetrics({
            ingestionRate: json.data.ingestion_rate_5m || 0,
            consumerStatus: json.data.consumer_status || 'Offline'
          });
        }
      } catch (err) {
        setMetrics(prev => ({ ...prev, consumerStatus: 'Offline' }));
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  const getStatusClass = (status) => {
    switch (status) {
      case 'Healthy': return 'live';
      case 'Degraded': return 'degraded';
      default: return 'offline';
    }
  };

  return (
    <div className="dashboard-container">
      <header className="header">
        <div className="title-section">
          <h1>MBTA Telemetry Pipeline</h1>
          <p className="subtitle">Data Particle Flow Visualizer</p>
        </div>
        
        <div className="metrics-row">
          <div className="metric-pill">
            <span className="metric-label">Pipeline Status</span>
            <div className={`status-dot ${getStatusClass(metrics.consumerStatus)}`}></div>
            <span className="metric-value">{metrics.consumerStatus}</span>
          </div>
          <div className="metric-pill">
            <span className="metric-label">Ingestion Rate</span>
            <span className="metric-value">{metrics.ingestionRate} rec/s</span>
          </div>
        </div>
      </header>

      <div className="canvas-container">
        <ParticleCanvas 
          ingestionRate={metrics.ingestionRate} 
          consumerStatus={metrics.consumerStatus} 
        />
      </div>
    </div>
  );
}

export default App;
