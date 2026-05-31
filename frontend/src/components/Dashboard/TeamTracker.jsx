import React from 'react';
import { useHelpLinkStore } from '../../store/useHelpLinkStore';

export default function TeamTracker() {
  const { rescueTeams, sosSignals, setFocusedLocation } = useHelpLinkStore();

  const getStatusCapsule = (status) => {
    switch (status?.toLowerCase()) {
      case 'available':
        return 'bg-green-950/80 text-green-400 border-green-900/60';
      case 'en_route':
        return 'bg-orange-950/80 text-orange-400 border-orange-900/60 animate-pulse';
      case 'on_ground':
        return 'bg-red-950/80 text-red-400 border-red-900/60 animate-pulse-critical';
      case 'returning':
        return 'bg-blue-950/80 text-blue-400 border-blue-900/60';
      default:
        return 'bg-gray-950 text-gray-400 border-gray-800';
    }
  };

  const handleLocateTeam = (team) => {
    setFocusedLocation([team.current_lat, team.current_lng]);
    setTimeout(() => setFocusedLocation(null), 2500);
  };

  return (
    <div className="w-full h-full flex flex-col bg-gray-900 border border-gray-800 rounded-lg overflow-hidden glass-panel select-none">
      
      {/* Tracker Header */}
      <div className="px-4 py-3 bg-gray-950/80 border-b border-gray-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          <h2 className="text-gray-100 font-extrabold text-xs tracking-wider uppercase">
            RESCUE TASKFORCE MONITOR
          </h2>
        </div>
        <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">
          ACTIVE UNITS: {rescueTeams.length}
        </span>
      </div>

      {/* Grid container */}
      <div className="flex-1 overflow-auto">
        <table className="w-full text-left border-collapse text-xs select-none">
          <thead>
            <tr className="bg-gray-950/50 border-b border-gray-800/80 text-[10px] text-gray-500 font-bold uppercase tracking-wider">
              <th className="py-2.5 px-3">CODE</th>
              <th className="py-2.5 px-3">UNIT DETAILS</th>
              <th className="py-2.5 px-3">STATUS</th>
              <th className="py-2.5 px-3">ASSIGNMENT</th>
              <th className="py-2.5 px-3 text-right">LOCATE</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/60">
            {rescueTeams.length === 0 ? (
              <tr>
                <td colSpan="5" className="py-8 text-center text-gray-600 text-[11px] font-bold uppercase tracking-wider">
                  NO ACTIVE TASKFORCES DEPLOYED
                </td>
              </tr>
            ) : (
              rescueTeams.map((team) => {
                // Find assigned SOS signal info if any
                const assignedSig = team.assigned_signal_id 
                  ? sosSignals.find(s => s.id === team.assigned_signal_id)
                  : null;

                return (
                  <tr key={`team-row-${team.id}`} className="hover:bg-gray-800/20 transition-colors">
                    
                    {/* Team Code */}
                    <td className="py-2.5 px-3 font-mono font-black text-gray-200">
                      {team.team_code}
                    </td>

                    {/* Unit Name and Size */}
                    <td className="py-2.5 px-3">
                      <div className="font-semibold text-gray-100">{team.team_name}</div>
                      <div className="text-[10px] text-gray-500">
                        {team.unit_type} • {team.personnel_count} Rescuers
                      </div>
                    </td>

                    {/* Status Pill */}
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-[9px] font-black border uppercase tracking-wider ${getStatusCapsule(team.status)}`}>
                        {team.status.replace('_', ' ')}
                      </span>
                    </td>

                    {/* Assignment Destination */}
                    <td className="py-2.5 px-3">
                      {assignedSig ? (
                        <div className="flex flex-col">
                          <span className="font-bold text-cyan-400">
                            🚩 {assignedSig.location_extracted || 'Sector Coordinates'}
                          </span>
                          <span className="text-[10px] text-gray-500">
                            Targeting {assignedSig.survivor_count_estimate} survivors
                          </span>
                        </div>
                      ) : (
                        <span className="text-gray-600 font-semibold italic text-[10px] tracking-wide uppercase">
                          UNASSIGNED
                        </span>
                      )}
                    </td>

                    {/* Locate Button */}
                    <td className="py-2.5 px-3 text-right">
                      <button
                        onClick={() => handleLocateTeam(team)}
                        className="p-1 hover:bg-gray-800 rounded text-cyan-400 hover:text-cyan-300 transition-colors cursor-pointer"
                        title="Locate Unit on Map"
                      >
                        🎯
                      </button>
                    </td>

                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
