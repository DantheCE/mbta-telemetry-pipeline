import React, { useState, useEffect } from 'react';
import { Activity, Bus, Clock, Database, Server } from 'lucide-react';
import './index.css';

function App() {
  const [metrics, setMetrics] = useState({ 
    total_records: 0, 
    active_vehicles_24h: 0, 
    last_updated: null,
    ingestion_rate_5m: 0,
    average_latency_seconds: 0.0,
    consumer_status: 'Offline'
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";
        const res = await fetch(`${API_URL}/api/v1/metrics`);
        if (!res.ok) throw new Error("Failed to fetch from API");
        
        const data = await res.json();
        setMetrics(data.data);
      } catch (err) {
        console.error(err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="metrics-container">
      <header className="metrics-header">
        <Activity className="icon" size={24} />
        <h1>System Impact Metrics</h1>
        <div className="status-badge">
          <span className="live-indicator" style={{ backgroundColor: error || metrics.consumer_status === 'Offline' ? '#ff3333' : loading ? '#eab308' : metrics.consumer_status === 'Lagging' ? '#f97316' : '#10b981' }}></span> 
          {loading ? "Connecting..." : error || metrics.consumer_status === 'Offline' ? "Offline" : metrics.consumer_status === 'Lagging' ? "Degraded" : "System Live"}
        </div>
      </header>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-title">
            <Activity size={16} />
            Ingestion Rate (5m)
          </div>
          <div className="metric-value">
            {metrics.ingestion_rate_5m.toLocaleString()} <span style={{fontSize: '1rem', color: 'var(--text-muted)', marginLeft: '8px', fontWeight: '500', alignSelf: 'flex-end', marginBottom: '4px'}}>recs/5m</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-title">
            <Clock size={16} />
            Pipeline Latency
          </div>
          <div className="metric-value">
            {metrics.average_latency_seconds} <span style={{fontSize: '1rem', color: 'var(--text-muted)', marginLeft: '8px', fontWeight: '500', alignSelf: 'flex-end', marginBottom: '4px'}}>sec</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-title">
            <Database size={16} />
            Total Processed Records
          </div>
          <div className="metric-value">
            {metrics.total_records.toLocaleString()}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-title">
            <Server size={16} />
            Consumer Status
          </div>
          <div className="metric-value">
            {metrics.consumer_status}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-title">
            <Bus size={16} />
            Active Vehicles (24h)
          </div>
          <div className="metric-value">
            {metrics.active_vehicles_24h.toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
