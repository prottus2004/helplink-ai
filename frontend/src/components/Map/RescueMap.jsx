import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Circle, CircleMarker, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { useHelpLinkStore } from '../../store/useHelpLinkStore';
import { useRescueData } from '../../hooks/useRescueData';
import { getPriorityColors } from '../../utils/priorityColors';
import HeatmapLayer from './HeatmapLayer';

// Fix default leaflet marker icon asset mapping issues in React environments
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

function ScenarioFlyTo({ center, zoom }) {
  const map = useMap();

  useEffect(() => {
    if (center && center[0] != null && center[1] != null) {
      map.flyTo(center, zoom, { duration: 1.8, easeLinearity: 0.25 });
    }
  }, [center, zoom, map]);
  return null;
}

export const SCENARIO_VIEWS = {
  wayanad: { center: [11.6854, 76.1320], zoom: 10 },
};

// Handles temporary focus actions from other dashboard widgets
function FocusedLocationFlyTo() {
  const map = useMap();
  const focusedLocation = useHelpLinkStore((state) => state.focusedLocation);

  useEffect(() => {
    if (focusedLocation && focusedLocation[0] != null && focusedLocation[1] != null) {
      map.flyTo(focusedLocation, 14, { duration: 1.2, easeLinearity: 0.25 });
    }
  }, [focusedLocation, map]);

  return null;
}

export default function RescueMap() {
  const { 
    sosSignals,
    satelliteZones,
    cellularAnomalies,
    rescueTeams
  } = useHelpLinkStore();
  
  const { dispatchTeam } = useRescueData();

  // Layer Toggles
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showSatellite, setShowSatellite] = useState(true);
  const [showCellular, setShowCellular] = useState(true);
  const [showSOS, setShowSOS] = useState(true);
  const [showTeams, setShowTeams] = useState(true);

  // Data source status (real vs simulated)
  const [dataStatus, setDataStatus] = useState(null);

  // Selected team state for inline map dispatches
  const [selectedTeamId, setSelectedTeamId] = useState({});

  // Fetch data source status on mount
  useEffect(() => {
    const fetchDataStatus = async () => {
      try {
        const response = await fetch('/api/live/data-status');
        const data = await response.json();
        setDataStatus(data);
      } catch (err) {
        console.warn('Failed to fetch data status:', err);
      }
    };
    fetchDataStatus();
    const interval = setInterval(fetchDataStatus, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  const scenarioView = SCENARIO_VIEWS.wayanad;

  // Custom DivIcon for SOS markers incorporating blinking statuses and survivor count numbers
  const createSOSIcon = (sig) => {
    const isCritical = sig.priority_level === 'CRITICAL';
    const isHigh = sig.priority_level === 'HIGH';
    const isMedium = sig.priority_level === 'MEDIUM';
    
    let colorClass = 'bg-green-500';
    let ringClass = '';
    
    if (isCritical) {
      colorClass = 'bg-red-500 animate-pulse-critical';
      ringClass = 'pulse-ring-red';
    } else if (isHigh) {
      colorClass = 'bg-orange-500';
      ringClass = 'pulse-ring-orange';
    } else if (isMedium) {
      colorClass = 'bg-yellow-500';
    }

    const verificationBorder = sig.is_verified ? 'border-2 border-cyan-400' : 'border border-white';

    return L.divIcon({
      html: `
        <div class="custom-gps-blip relative flex items-center justify-center">
          ${ringClass ? `<div class="${ringClass}"></div>` : ''}
          <div class="w-6 h-6 rounded-full ${colorClass} ${verificationBorder} flex items-center justify-center text-[10px] text-white font-extrabold shadow-2xl relative z-10">
            ${sig.survivor_count_estimate || 1}
          </div>
        </div>
      `,
      className: 'custom-sos-div-icon',
      iconSize: [28, 28],
      iconAnchor: [14, 14]
    });
  };

  // Custom DivIcon for Rescue Teams depending on status
  const createTeamIcon = (team) => {
    let statusColor = 'bg-green-500';
    let emoji = '🚛'; // Boat/Evacuation Truck emoji
    
    if (team.status === 'en_route') {
      statusColor = 'bg-orange-500 animate-pulse';
      emoji = '🚤';
    } else if (team.status === 'on_ground') {
      statusColor = 'bg-red-500 animate-pulse-critical';
      emoji = team.unit_type === 'Army' ? '🚁' : '🏊';
    } else if (team.status === 'returning') {
      statusColor = 'bg-blue-500';
      emoji = '🔙';
    }

    return L.divIcon({
      html: `
        <div class="flex flex-col items-center">
          <div class="text-xl filter drop-shadow-md select-none">${emoji}</div>
          <div class="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full ${statusColor} border border-white"></div>
        </div>
      `,
      className: 'custom-team-div-icon',
      iconSize: [30, 30],
      iconAnchor: [15, 15]
    });
  };

  const handleMapDispatch = async (sigId) => {
    const teamId = selectedTeamId[sigId];
    if (!teamId) return;
    
    try {
      await dispatchTeam(parseInt(teamId), sigId);
      // Success triggers websocket broadcast auto updates
      setSelectedTeamId(prev => ({ ...prev, [sigId]: '' }));
    } catch (err) {
      alert(`Dispatch error: ${err.response?.data?.detail || err.message}`);
    }
  };

  return (
    <div className="relative w-full h-full border border-gray-800 rounded-lg overflow-hidden glass-panel shadow-[0_4px_30px_rgba(0,0,0,0.4)]">
      
      {/* Map Header Overlay */}
      <div className="absolute top-3 left-12 z-[1000] pointer-events-none select-none flex items-center gap-2 bg-gray-950/85 backdrop-blur-md px-3 py-1.5 rounded border border-gray-800">
        <span className="w-2.5 h-2.5 bg-red-500 rounded-full animate-ping"></span>
        <span className="w-2.5 h-2.5 bg-red-500 rounded-full absolute"></span>
        <span className="text-[11px] uppercase tracking-wider text-gray-100 font-extrabold">
          HELPLINK RESCUE COMMAND — LIVE
        </span>
      </div>

      {/* Map Legend Overlay */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-gray-950/90 backdrop-blur-md px-3 py-3 rounded border border-gray-800 text-[11px] text-gray-300 w-44 select-none">
        <h4 className="font-extrabold text-gray-100 border-b border-gray-800 pb-1 mb-2 tracking-wider uppercase text-[10px]">LEGEND</h4>
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-red-500 border border-white animate-pulse-critical"></span>
            <span>Critical SOS (Surv. Count)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded bg-red-500/30 border border-red-500"></span>
            <span>SAR Inundation Circles</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-purple-500 border border-purple-400"></span>
            <span>Cellular Dead Zones</span>
          </div>
          <div className="flex items-center gap-2">
            <span>🚤 / 🚁</span>
            <span>Active Rescuers (En Route)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-6 h-0.5 border-t-2 border-dashed border-blue-500 block"></span>
            <span>Dispatched Vector Line</span>
          </div>
        </div>
      </div>

      {/* Layer Toggles checkboxes (Top Right Overlay) */}
      <div className="absolute top-3 right-3 z-[1000] bg-gray-950/90 backdrop-blur-md p-3 rounded border border-gray-800 text-[11px] text-gray-300 flex flex-col gap-2 shadow-2xl">
        <h4 className="font-bold text-gray-100 border-b border-gray-800 pb-1 mb-1 tracking-wider uppercase text-[9px]">LAYERS CONFIG</h4>
        
        <label className="flex items-center gap-2 cursor-pointer select-none hover:text-white">
          <input 
            type="checkbox" 
            checked={showHeatmap} 
            onChange={(e) => setShowHeatmap(e.target.checked)}
            className="rounded border-gray-800 bg-gray-900 text-blue-500 focus:ring-0 focus:ring-offset-0 w-3.5 h-3.5"
          />
          <span>SOS Heatmap Overlay</span>
        </label>
        
        <label className="flex items-center gap-2 cursor-pointer select-none hover:text-white">
          <input 
            type="checkbox" 
            checked={showSatellite} 
            onChange={(e) => setShowSatellite(e.target.checked)}
            className="rounded border-gray-800 bg-gray-900 text-cyan-500 focus:ring-0 w-3.5 h-3.5"
          />
          <span>Satellite SAR Floods</span>
          {dataStatus?.satellite === 'real' && (
            <span className="text-[8px] px-1.5 py-0.5 bg-green-950 text-green-300 border border-green-700 rounded font-bold">SENTINEL-1 LIVE</span>
          )}
        </label>
        
        <label className="flex items-center gap-2 cursor-pointer select-none hover:text-white">
          <input 
            type="checkbox" 
            checked={showCellular} 
            onChange={(e) => setShowCellular(e.target.checked)}
            className="rounded border-gray-800 bg-gray-900 text-purple-500 focus:ring-0 w-3.5 h-3.5"
          />
          <span>Cellular Anomaly Layers</span>
          {dataStatus?.towers === 'real' && (
            <span className="text-[8px] px-1.5 py-0.5 bg-green-950 text-green-300 border border-green-700 rounded font-bold">OPENCELLID LIVE</span>
          )}
        </label>
        
        <label className="flex items-center gap-2 cursor-pointer select-none hover:text-white">
          <input 
            type="checkbox" 
            checked={showSOS} 
            onChange={(e) => setShowSOS(e.target.checked)}
            className="rounded border-gray-800 bg-gray-900 text-red-500 focus:ring-0 w-3.5 h-3.5"
          />
          <span>Distress SOS Beacons</span>
        </label>
        
        <label className="flex items-center gap-2 cursor-pointer select-none hover:text-white">
          <input 
            type="checkbox" 
            checked={showTeams} 
            onChange={(e) => setShowTeams(e.target.checked)}
            className="rounded border-gray-800 bg-gray-900 text-green-500 focus:ring-0 w-3.5 h-3.5"
          />
          <span>NDRF / SDRF Field Units</span>
        </label>

        {/* Data Sources Status Summary */}
        <div className="border-t border-gray-800 pt-2 mt-2 text-[9px]">
          <div className="font-bold text-gray-100 mb-1 uppercase tracking-wider">Data Sources</div>
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-500"></span>
              <span className="text-gray-300">✓ Sentinel-1 SAR</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-500"></span>
              <span className="text-gray-300">✓ OpenCelliD</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-500"></span>
              <span className="text-gray-300">✓ Twitter/X SOS</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-500"></span>
              <span className="text-gray-300">✓ GDACS Live</span>
            </div>
          </div>
        </div>
      </div>

      <MapContainer
        center={[11.6854, 76.1320]}
        zoom={10}
        zoomControl={true}
        className="w-full h-full"
      >
        <ScenarioFlyTo
          center={scenarioView.center}
          zoom={scenarioView.zoom}
        />
        <FocusedLocationFlyTo />
        
        {/* Dark theme tile layers mapping */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* Layer 1: Heatmap of SOS Signals */}
        {showHeatmap && sosSignals.length > 0 && (
          <HeatmapLayer 
            points={sosSignals.map(s => ({
              lat: s.latitude,
              lng: s.longitude,
              intensity: s.priority_score / 100
            }))} 
          />
        )}

        {/* Layer 2: Satellite SAR Flood Zones */}
        {showSatellite && satelliteZones.map((zone) => {
          let color = '#eab308'; // yellow
          let opacity = 0.3;
          if (zone.flood_severity > 0.7) {
            color = '#ef4444'; // red
            opacity = 0.4;
          } else if (zone.flood_severity > 0.4) {
            color = '#f97316'; // orange
            opacity = 0.35;
          }

          // Compute circle radius in meters (scale according to zone square kms)
          const radiusMeters = Math.sqrt(zone.area_sqkm) * 450;

          return (
            <Circle
              key={`sat-${zone.id}`}
              center={[zone.center_lat, zone.center_lng]}
              radius={radiusMeters}
              pathOptions={{
                fillColor: color,
                fillOpacity: opacity,
                color: color,
                weight: 1.5
              }}
            >
              <Popup>
                <div className="font-extrabold text-cyan-400 text-xs border-b border-gray-800 pb-1 mb-1 tracking-wider">
                  🛰️ SATELLITE SAR ANOMALY
                </div>
                <div className="text-gray-100 text-sm font-semibold mb-1">{zone.zone_name}</div>
                <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-gray-300 text-[11px] mt-1">
                  <span>Flood Severity:</span>
                  <span className="font-bold text-red-400">{(zone.flood_severity * 100).toFixed(0)}%</span>
                  <span>Est. Water Depth:</span>
                  <span className="font-bold">{zone.water_depth_estimate}m</span>
                  <span>Submerged Area:</span>
                  <span>{zone.area_sqkm} sqkm</span>
                  <span>Isolated Buildings:</span>
                  <span className="font-bold text-orange-400">{zone.isolated_structures} structures</span>
                </div>
              </Popup>
            </Circle>
          );
        })}

        {/* Layer 3: Cellular Tower Anomaly Indicators */}
        {showCellular && cellularAnomalies.map((anom) => {
          const isDead = anom.anomaly_type === 'dead_zone';
          const isSpike = anom.anomaly_type === 'traffic_spike';
          
          let color = '#3b82f6'; // blue
          if (isDead) color = '#a855f7'; // purple
          else if (isSpike) color = '#ec4899'; // pink

          return (
            <CircleMarker
              key={`cell-${anom.id}`}
              center={[anom.lat, anom.lng]}
              radius={7}
              pathOptions={{
                fillColor: color,
                fillOpacity: 0.8,
                color: '#ffffff',
                weight: 1.2
              }}
            >
              <Popup>
                <div className="font-extrabold text-purple-400 text-xs border-b border-gray-800 pb-1 mb-1 tracking-wider">
                  📶 CELLULAR TELEMETRY SIGNAL
                </div>
                <div className="text-gray-100 text-sm font-semibold">{anom.tower_id}</div>
                <div className="text-xs text-gray-300 mt-1 flex flex-col gap-0.5">
                  <div>Type: <span className="font-bold uppercase text-purple-300">{anom.anomaly_type.replace('_', ' ')}</span></div>
                  <div>Health Drop Score: <span className="font-bold text-red-400">{(anom.anomaly_score * 100).toFixed(0)}%</span></div>
                  <div>Impact Radius: <span>{anom.affected_radius_km} km</span></div>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}

        {/* Layer 5: Rescue Teams & Dispatch Vector Routing lines */}
        {showTeams && rescueTeams.map((team) => {
          const nodes = [];
          
          // If team is active and assigned, draw polyline route vector
          if (team.assigned_signal_id && (team.status === 'en_route' || team.status === 'on_ground')) {
            const targetSig = sosSignals.find(s => s.id === team.assigned_signal_id);
            if (targetSig) {
              nodes.push([team.current_lat, team.current_lng]);
              nodes.push([targetSig.latitude, targetSig.longitude]);
            }
          }

          return (
            <React.Fragment key={`team-frag-${team.id}`}>
              {nodes.length > 0 && (
                <Polyline
                  positions={nodes}
                  pathOptions={{
                    color: '#3b82f6', // blue vector
                    weight: 2.2,
                    dashArray: '5, 8',
                    opacity: 0.85
                  }}
                />
              )}
              <Marker
                position={[team.current_lat, team.current_lng]}
                icon={createTeamIcon(team)}
              >
                <Popup>
                  <div className="font-extrabold text-green-400 text-xs border-b border-gray-800 pb-1 mb-1 tracking-wider">
                    🚒 RESCUE FORCE DISPATCH UNIT
                  </div>
                  <div className="text-gray-100 text-sm font-bold">{team.team_code}</div>
                  <div className="text-xs text-gray-300 mt-1">
                    <div>Name: <span>{team.team_name}</span></div>
                    <div>Type: <span className="font-semibold">{team.unit_type}</span></div>
                    <div>Personnel: <span className="font-semibold text-green-300">{team.personnel_count} Rescuers</span></div>
                    <div>Status: <span className="font-extrabold text-orange-400 uppercase">{team.status}</span></div>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}

        {/* Layer 4: SOS Distress Signals */}
        {showSOS && sosSignals.map((sig) => {
          const isDispatched = rescueTeams.some(t => t.assigned_signal_id === sig.id);
          const assignedTeam = rescueTeams.find(t => t.assigned_signal_id === sig.id);
          const colors = getPriorityColors(sig.priority_level);

          return (
            <Marker
              key={`sos-${sig.id}`}
              position={[sig.latitude, sig.longitude]}
              icon={createSOSIcon(sig)}
            >
              <Popup>
                <div className="font-extrabold text-xs border-b border-gray-800 pb-1 mb-1 tracking-wider flex justify-between items-center">
                  <span className={colors.text}>🚨 SOS DISTRESS BEACON</span>
                  <span className={`px-1.5 py-0.5 rounded text-[9px] border font-bold ${colors.badge}`}>
                    {sig.priority_level}
                  </span>
                </div>
                <div className="text-xs text-gray-100 font-semibold italic bg-gray-950 p-2 rounded my-2 max-h-24 overflow-y-auto border border-gray-800 leading-tight">
                  "{sig.raw_message}"
                </div>
                
                <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-gray-300 text-[11px] mb-3">
                  <span>Language:</span>
                  <span className="font-semibold">{sig.language_detected}</span>
                  <span>Est. Survivors:</span>
                  <span className="font-bold text-red-400">{sig.survivor_count_estimate} people</span>
                  <span>Extracted Location:</span>
                  <span className="text-orange-300 truncate">{sig.location_extracted || 'Unknown'}</span>
                  <span>AI Score:</span>
                  <span className="font-bold">{sig.priority_score.toFixed(0)} / 100</span>
                </div>

                {/* AI DECISION BREAKDOWN — shows how the AI scored this signal */}
                <div style={{
                  marginTop: 10,
                  padding: '8px 10px',
                  background: '#F1EFE8',
                  borderRadius: 6,
                  fontSize: 11,
                }}>
                  <div style={{ fontWeight: 600, marginBottom: 6, color: '#2C2C2A' }}>
                    🤖 AI Decision Breakdown
                  </div>

                  <div style={{ color: '#5F5E5A', marginBottom: 3 }}>
                    Language: <strong style={{ color: '#2C2C2A' }}>
                      {sig.language_detected}
                    </strong> ({(sig.language_confidence * 100).toFixed(0)}% confidence)
                  </div>

                  <div style={{ color: '#5F5E5A', marginBottom: 3 }}>
                    Keywords matched: <strong style={{ color: '#2C2C2A' }}>
                      {(sig.matched_keywords || ['distress', 'flood', 'stranded']).join(', ')}
                    </strong>
                  </div>

                  <div style={{ color: '#5F5E5A', marginBottom: 8 }}>
                    Survivors estimated: <strong style={{ color: '#2C2C2A' }}>
                      {sig.survivor_count_estimate || 1} people
                    </strong> (from numbers in message)
                  </div>

                  <div style={{ fontWeight: 600, marginBottom: 4, color: '#2C2C2A', display: 'flex', justifyContent: 'space-between' }}>
                    <span>Priority Score Components</span>
                    <span>{sig.priority_score}/100</span>
                  </div>

                  {[
                    { label: 'SOS signal density', pct: 0.40 },
                    { label: 'Satellite severity nearby', pct: 0.35 },
                    { label: 'Cellular dead zone overlap', pct: 0.25 },
                  ].map(row => (
                    <div key={row.label} style={{ marginBottom: 4 }}>
                      <div style={{ display:'flex', justifyContent:'space-between',
                                    fontSize: 10, color: '#888780', marginBottom: 2 }}>
                        <span>{row.label}</span>
                        <span>+{Math.round(sig.priority_score * row.pct)} pts</span>
                      </div>
                      <div style={{ height: 3, background: '#D3D1C7', borderRadius: 2 }}>
                        <div style={{
                          height: '100%', borderRadius: 2, background: '#D85A30',
                          width: `${sig.priority_score * row.pct}%`
                        }} />
                      </div>
                    </div>
                  ))}

                  <div style={{ marginTop: 6, fontSize: 10, color: '#888780', fontStyle: 'italic' }}>
                    Data source: {sig.data_source || 'NLP Engine v1.0'} | {sig.is_verified ? '✓ Verified' : 'Pending verification'}
                  </div>
                </div>

                {/* Inline Dispatch Selector panel */}
                <div className="border-t border-gray-800 pt-2.5 mt-2">
                  {isDispatched ? (
                    <div className="bg-blue-950/60 border border-blue-800/50 p-2 rounded text-[11px] text-blue-300 font-bold text-center">
                      ⚡ DISPATCHED: {assignedTeam?.team_code} ({assignedTeam?.status.replace('_', ' ').toUpperCase()})
                    </div>
                  ) : (
                    <div className="flex flex-col gap-1.5">
                      <select
                        value={selectedTeamId[sig.id] || ''}
                        onChange={(e) => setSelectedTeamId(prev => ({ ...prev, [sig.id]: e.target.value }))}
                        className="w-full text-xs bg-gray-950 border border-gray-800 rounded p-1 text-gray-300 focus:outline-none focus:border-blue-700"
                      >
                        <option value="">-- SELECT TEAM FOR DISPATCH --</option>
                        {rescueTeams
                          .filter(t => t.status === 'available')
                          .map(t => (
                            <option key={t.id} value={t.id}>
                              {t.team_code} - {t.team_name} ({t.unit_type})
                            </option>
                          ))
                        }
                      </select>
                      <button
                        onClick={() => handleMapDispatch(sig.id)}
                        disabled={!selectedTeamId[sig.id]}
                        className="w-full text-xs font-bold bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 disabled:text-gray-500 text-white rounded py-1 transition-colors"
                      >
                        DISPATCH RESCUE TEAM →
                      </button>
                    </div>
                  )}
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
