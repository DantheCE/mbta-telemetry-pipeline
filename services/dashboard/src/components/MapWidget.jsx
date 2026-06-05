import React, { useRef, useEffect } from 'react';

import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const MapWidget = ({ vehicles }) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const markersRef = useRef({});

  useEffect(() => {
    if (map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
      center: [-71.0589, 42.3601],
      zoom: 15, // Zoomed in closer by default to see buildings!
      pitch: 60, // Aggressive 3D pitch
      bearing: -20,
    });

    map.current.on('load', () => {
      // Find the primary vector tile source from the Carto style
      const style = map.current.getStyle();
      const vectorSourceId = Object.keys(style.sources).find(
        key => style.sources[key].type === 'vector'
      );

      if (vectorSourceId) {
        // Find the first symbol layer so we can insert buildings underneath labels
        let labelLayerId;
        for (let i = 0; i < style.layers.length; i++) {
          if (style.layers[i].type === 'symbol' && style.layers[i].layout && style.layers[i].layout['text-field']) {
            labelLayerId = style.layers[i].id;
            break;
          }
        }

        // Add 3D buildings! OpenMapTiles schema (which Carto uses) provides 'building' layer
        map.current.addLayer({
          'id': '3d-buildings',
          'source': vectorSourceId,
          'source-layer': 'building',
          'type': 'fill-extrusion',
          'minzoom': 14,
          'paint': {
            'fill-extrusion-color': '#1e293b', // Match our dark theme
            // OpenMapTiles uses 'render_height', fallback to 15m if not specified
            'fill-extrusion-height': [
              'coalesce',
              ['get', 'render_height'],
              ['get', 'height'],
              15
            ],
            'fill-extrusion-base': [
              'coalesce',
              ['get', 'render_min_height'],
              ['get', 'min_height'],
              0
            ],
            'fill-extrusion-opacity': 0.8
          }
        }, labelLayerId);
      }
    });

  }, []);

  // Update markers
  useEffect(() => {
    if (!map.current) return;

    const currentEntityIds = new Set();

    vehicles.forEach((vehicle) => {
      currentEntityIds.add(vehicle.entity_id);

      if (markersRef.current[vehicle.entity_id]) {
        markersRef.current[vehicle.entity_id].setLngLat([vehicle.longitude, vehicle.latitude]);
      } else {
        // Create an upgraded, animated marker to distinguish from the old Leaflet ones
        const el = document.createElement('div');
        el.className = 'maplibre-animated-marker';
        el.style.width = '14px';
        el.style.height = '14px';
        el.style.backgroundColor = '#10b981'; // Changed to Green to prove the update worked!
        el.style.borderRadius = '50%';
        el.style.border = '2px solid white';
        el.style.boxShadow = '0 0 15px #10b981';
        el.style.transition = 'transform 0.2s linear';

        const popup = new maplibregl.Popup({ offset: 15, className: 'dark-popup' })
            .setHTML(`<strong>Trip:</strong> ${vehicle.trip_id}<br/><strong>Bus:</strong> ${vehicle.vehicle_id}`);

        const marker = new maplibregl.Marker({ element: el })
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
          <div ref={mapContainer} style={{ width: '100%', height: '100%', position: 'absolute', top: 0, bottom: 0 }} />
      </div>
  );
};

export default MapWidget;
