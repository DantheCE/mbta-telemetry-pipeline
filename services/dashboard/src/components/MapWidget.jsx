import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet's default icon paths issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom Bus Icon matching our previous premium aesthetic
const createBusIcon = () => {
  return L.divIcon({
    className: 'custom-bus-icon',
    html: `<div style="width: 12px; height: 12px; background-color: var(--accent); border-radius: 50%; border: 2px solid white; box-shadow: 0 0 10px var(--accent); transition: transform 0.2s;"></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6],
    popupAnchor: [0, -10]
  });
};

const busIcon = createBusIcon();

const MapWidget = ({ vehicles }) => {
  return (
    <div style={{ width: '100%', height: '100%', zIndex: 1 }}>
      <MapContainer 
        center={[42.3601, -71.0589]} 
        zoom={12} 
        style={{ width: '100%', height: '100%', background: '#0f172a' }}
        zoomControl={true}
      >
        {/* CartoDB Dark Matter (Free, no API key needed, extremely premium dark look) */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        {vehicles.map(vehicle => (
          <Marker 
            key={vehicle.entity_id} 
            position={[vehicle.latitude, vehicle.longitude]}
            icon={busIcon}
          >
            <Popup>
              <strong>Trip:</strong> {vehicle.trip_id}<br/>
              <strong>Bus:</strong> {vehicle.vehicle_id}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default MapWidget;
