import React, { useState, useEffect } from 'react';
import { Activity, Bus } from 'lucide-react';
import MapWidget from './components/MapWidget';
import './index.css';

function App() {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";
        const res = await fetch(`${API_URL}/api/v1/vehicles/latest`);
        if (!res.ok) throw new Error("Failed to fetch from API");
        const data = await res.json();
        setVehicles(data.data);
      } catch (err) {
        console.error(err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchVehicles();
    const interval = setInterval(fetchVehicles, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard-container">
      <div className="sidebar">
        <h1 style={{ marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Activity className="icon" size={28} />
          Transit Pulse
        </h1>

        <div className="stat-card">
          <div className="stat-title">System Status</div>
          <div className="stat-value" style={{ fontSize: '1.25rem' }}>
            <span className="live-indicator" style={{ backgroundColor: error ? '#ef4444' : loading ? '#eab308' : '#10b981' }}></span> 
            {loading ? "Connecting..." : error ? "Offline" : "Live"}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-title">Active Vehicles</div>
          <div className="stat-value">
            <Bus className="icon" size={24} />
            {vehicles.length}
          </div>
        </div>

        <div style={{ marginTop: 'auto' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center' }}>
            Data provided by MBTA GTFS Realtime
          </p>
        </div>
      </div>

      <div className="map-area">
        <MapWidget vehicles={vehicles} />
      </div>
    </div>
  );
}

export default App;
