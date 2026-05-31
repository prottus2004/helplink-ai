import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';

export default function HeatmapLayer({ points }) {
  const map = useMap();

  useEffect(() => {
    if (!map || !points || points.length === 0) return;

    // Convert point objects to L.heat format: [[lat, lng, intensity], ...]
    const heatPoints = points.map((p) => [p.lat, p.lng, p.intensity]);

    // Create the leaflet heat layer
    const heatLayer = L.heatLayer(heatPoints, {
      radius: 25,
      blur: 18,
      maxZoom: 15,
      gradient: {
        0.2: 'blue',
        0.4: 'cyan',
        0.6: 'lime',
        0.8: 'yellow',
        1.0: 'red'
      }
    });

    heatLayer.addTo(map);

    // Clean up on component unmount
    return () => {
      if (map && heatLayer) {
        map.removeLayer(heatLayer);
      }
    };
  }, [map, points]);

  return null;
}
