import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { getPriorityColors } from '../../utils/priorityColors';

export default function SurvivorMarker({ signal, onClickDispatch, availableTeams, activeTeamAssigned }) {
  const isCritical = signal.priority_level === 'CRITICAL';
  const colors = getPriorityColors(signal.priority_level);

  let colorClass = 'bg-green-500';
  let ringClass = '';
  
  if (isCritical) {
    colorClass = 'bg-red-500 animate-pulse-critical';
    ringClass = 'pulse-ring-red';
  } else if (signal.priority_level === 'HIGH') {
    colorClass = 'bg-orange-500';
    ringClass = 'pulse-ring-orange';
  } else if (signal.priority_level === 'MEDIUM') {
    colorClass = 'bg-yellow-500';
  }

  const customIcon = L.divIcon({
    html: `
      <div class="custom-gps-blip relative flex items-center justify-center">
        ${ringClass ? `<div class="${ringClass}"></div>` : ''}
        <div class="w-6 h-6 rounded-full ${colorClass} border border-white flex items-center justify-center text-[10px] text-white font-extrabold shadow-2xl z-10">
          ${signal.survivor_count_estimate || 1}
        </div>
      </div>
    `,
    className: 'custom-sos-div-icon',
    iconSize: [28, 28],
    iconAnchor: [14, 14]
  });

  return (
    <Marker position={[signal.latitude, signal.longitude]} icon={customIcon}>
      <Popup>
        <div className="font-extrabold text-xs border-b border-gray-800 pb-1 mb-1 tracking-wider flex justify-between items-center">
          <span className={colors.text}>🚨 DISTRESS INCIDENT</span>
          <span className={`px-1.5 py-0.5 rounded text-[9px] border font-bold ${colors.badge}`}>
            {signal.priority_level}
          </span>
        </div>
        <div className="text-xs text-gray-100 font-semibold italic bg-gray-950 p-2 rounded my-2 border border-gray-800">
          "{signal.raw_message}"
        </div>
        <div className="text-[11px] text-gray-300">
          <div>Language: <span className="font-semibold text-white">{signal.language_detected}</span></div>
          <div>Survivors: <span className="font-semibold text-red-400">{signal.survivor_count_estimate}</span></div>
          <div>Location: <span className="font-semibold text-orange-300">{signal.location_extracted || 'Unknown'}</span></div>
        </div>
      </Popup>
    </Marker>
  );
}
