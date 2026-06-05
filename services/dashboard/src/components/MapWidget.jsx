import React, { useRef, useEffect } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const MapWidget = ({ vehicles }) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const markersRef = useRef({});

  useEffect(() => {
    if (map.current) return; // initialize map only once

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      // Using Carto's premium Dark Matter vector tile theme. 100% free, no API key.
      style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
      center: [-71.0589, 42.3601],
      zoom: 11.5,
      pitch: 45, // 3D perspective
      bearing: -17.6,
    });

  }, []);

  // Update markers when vehicles change
  useEffect(() => {
    if (!map.current) return;

    const currentEntityIds = new Set();

    vehicles.forEach((vehicle) => {
      currentEntityIds.add(vehicle.entity_id);

      if (markersRef.current[vehicle.entity_id]) {
        // Update existing marker
        markersRef.current[vehicle.entity_id].setLngLat([vehicle.longitude, vehicle.latitude]);
      } else {
        // Create new marker
        const el = document.createElement('div');
        el.style.width = '12px';
        el.style.height = '12px';
        el.style.backgroundColor = 'var(--accent)';
        el.style.borderRadius = '50%';
        el.style.border = '2px solid white';
        el.style.boxShadow = '0 0 10px var(--accent)';
        el.style.transition = 'transform 0.2s';

        const popup = new maplibregl.Popup({ offset: 15 })
            .setHTML(`<strong>Trip:</strong> ${vehicle.trip_id}<br/><strong>Bus:</strong> ${vehicle.vehicle_id}`);

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([vehicle.longitude, vehicle.latitude])
          .setPopup(popup)
          .addTo(map.current);

        markersRef.current[vehicle.entity_id] = marker;
      }
    });

    // Clean up markers for vehicles that disappeared
    Object.keys(markersRef.current).forEach(entityId => {
        if (!currentEntityIds.has(entityId)) {
            markersRef.current[entityId].remove();
            delete markersRef.current[entityId];
        }
    });

  }, [vehicles]);

  return (
      <div style={{ width: '100%', height: '100%', position: 'relative' }}>
          <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />
      </div>
  );
};

export default MapWidget;
