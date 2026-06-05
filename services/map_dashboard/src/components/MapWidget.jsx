import React from 'react';
import DeckGL from '@deck.gl/react';
import { ScatterplotLayer, TextLayer } from '@deck.gl/layers';
import { Map } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

// We use the absolute darkest Carto map for high contrast neon visualization
const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/dark-matter-nolabels-gl-style/style.json';

const INITIAL_VIEW_STATE = {
  longitude: -71.0589,
  latitude: 42.3601,
  zoom: 12.5,
  pitch: 45,
  bearing: -17.6
};

const MapWidget = ({ vehicles }) => {
  // Format data for Deck.gl
  const data = vehicles.map(v => ({
    position: [v.longitude, v.latitude],
    trip_id: v.trip_id,
    vehicle_id: v.vehicle_id,
    label: v.trip_id ? `Trip: ${v.trip_id}` : `Bus: ${v.vehicle_id}`
  }));

  const layers = [
    new ScatterplotLayer({
      id: 'neon-scatter-layer',
      data,
      radiusScale: 20,
      radiusMinPixels: 6,
      radiusMaxPixels: 20,
      getPosition: d => d.position,
      getFillColor: [16, 185, 129, 210], // Emerald Green glow
      getLineColor: [255, 255, 255, 255], // Solid white core
      lineWidthMinPixels: 2,
      stroked: true,
      pickable: true,
      autoHighlight: true,
      highlightColor: [255, 255, 255, 255],
      transitions: {
        getPosition: 600, // Buttery smooth glide between polling updates
      }
    }),
    new TextLayer({
      id: 'text-layer',
      data,
      pickable: false,
      getPosition: d => d.position,
      getText: d => d.label,
      getSize: 12,
      getColor: [255, 255, 255, 200],
      getPixelOffset: [0, -15],
      fontFamily: 'Inter, sans-serif',
      fontWeight: 'bold',
      transitions: {
        getPosition: 600,
      }
    })
  ];

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={layers}
        getTooltip={({object}) => object && `Trip: ${object.trip_id}\nBus: ${object.vehicle_id}`}
      >
        <Map mapStyle={MAP_STYLE} />
      </DeckGL>
    </div>
  );
};

export default MapWidget;
