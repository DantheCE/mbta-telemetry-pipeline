import React, { useRef, useEffect } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN || '';

const MapWidget = ({ vehicles }) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const markersRef = useRef({});

  useEffect(() => {
    if (map.current) return;
    
    if (!mapboxgl.accessToken) {
        console.warn("Mapbox token missing! Set VITE_MAPBOX_TOKEN.");
    }

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11', // Premium dark mode style
      center: [-71.0589, 42.3601], // Boston coordinates
      zoom: 11.5,
      pitch: 45, // 3D perspective
      bearing: -17.6,
    });

    map.current.on('load', () => {
      map.current.addLayer({
        'id': '3d-buildings',
        'source': 'composite',
        'source-layer': 'building',
        'filter': ['==', 'extrude', 'true'],
        'type': 'fill-extrusion',
        'minzoom': 15,
        'paint': {
          'fill-extrusion-color': '#aaa',
          'fill-extrusion-height': [
            'interpolate', ['linear'], ['zoom'],
            15, 0,
            15.05, ['get', 'height']
          ],
          'fill-extrusion-base': [
            'interpolate', ['linear'], ['zoom'],
            15, 0,
            15.05, ['get', 'min_height']
          ],
          'fill-extrusion-opacity': 0.6
        }
      });
    });
  }, []);

  useEffect(() => {
    if (!map.current) return;

    const currentEntityIds = new Set();

    vehicles.forEach((vehicle) => {
      currentEntityIds.add(vehicle.entity_id);

      if (markersRef.current[vehicle.entity_id]) {
        markersRef.current[vehicle.entity_id].setLngLat([vehicle.longitude, vehicle.latitude]);
      } else {
        const el = document.createElement('div');
        el.style.width = '12px';
        el.style.height = '12px';
        el.style.backgroundColor = 'var(--accent)';
        el.style.borderRadius = '50%';
        el.style.border = '2px solid white';
        el.style.boxShadow = '0 0 10px var(--accent)';
        el.style.transition = 'transform 0.2s';

        const popup = new mapboxgl.Popup({ offset: 15 })
            .setHTML(`<strong>Trip:</strong> ${vehicle.trip_id}<br/><strong>Bus:</strong> ${vehicle.vehicle_id}`);

        const marker = new mapboxgl.Marker(el)
          .setLngLat([vehicle.longitude, vehicle.latitude])
          .setPopup(popup)
          .addTo(map.current);

        markersRef.current[vehicle.entity_id] = marker;
      }
    });

    Object.keys(markersRef.current).forEach(entityId => {
        if (!currentEntityIds.has(entityId)) {
            markersRef.current[entityId].remove();
            delete markersRef.current[entityId];
        }
    });

  }, [vehicles]);

  return (
      <div style={{ width: '100%', height: '100%', position: 'relative' }}>
          {!mapboxgl.accessToken && (
              <div style={{ position: 'absolute', top: 20, right: 20, zIndex: 100, background: 'rgba(220, 38, 38, 0.9)', padding: '12px', borderRadius: '8px', color: 'white', fontWeight: 600 }}>
                  Please set VITE_MAPBOX_TOKEN in .env to render the map!
              </div>
          )}
          <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />
      </div>
  );
};

export default MapWidget;
