import React, { useState } from 'react';
import { getPriorityColors } from '../../utils/priorityColors';
import { getLanguageLabel } from '../../utils/languageMap';
import { useHelpLinkStore } from '../../store/useHelpLinkStore';
import { useRescueData } from '../../hooks/useRescueData';

export default function SOSCard({ signal }) {
  const { rescueTeams } = useHelpLinkStore();
  const { verifySOSSignal, dismissSOSSignal, dispatchTeam, setFocusedLocation } = useRescueData();
  const [selectedTeamId, setSelectedTeamId] = useState('');
  const [isDispatching, setIsDispatching] = useState(false);

  const colors = getPriorityColors(signal.priority_level);
  const langLabel = getLanguageLabel(signal.language_detected);
  
  // Find if a team is already dispatched to this SOS signal
  const assignedTeam = rescueTeams.find(t => t.assigned_signal_id === signal.id);
  const isDispatched = !!assignedTeam;

  const handleVerify = async () => {
    try {
      await verifySOSSignal(signal.id);
    } catch (err) {
      alert(`Verification error: ${err.message}`);
    }
  };

  const handleDismiss = async () => {
    if (confirm('Are you sure you want to dismiss this distress signal as a false positive?')) {
      try {
        await dismissSOSSignal(signal.id);
      } catch (err) {
        alert(`Dismissal error: ${err.message}`);
      }
    }
  };

  const handleDispatch = async () => {
    if (!selectedTeamId) return;
    try {
      await dispatchTeam(parseInt(selectedTeamId), signal.id);
      setSelectedTeamId('');
      setIsDispatching(false);
    } catch (err) {
      alert(`Dispatch error: ${err.message}`);
    }
  };

  const handleFocus = () => {
    setFocusedLocation([signal.latitude, signal.longitude]);
    // Clear focus after 2.5 seconds to restore normal operation
    setTimeout(() => setFocusedLocation(null), 2500);
  };

  return (
    <div className={`p-4 rounded-lg border bg-gray-900/40 backdrop-blur transition-all flex flex-col gap-3 ${colors.border} ${colors.glow} hover:bg-gray-800/10`}>
      
      {/* Header Segment */}
      <div className="flex items-center justify-between">
        <span className={`px-2 py-0.5 rounded text-[9px] font-black border tracking-wider uppercase ${colors.badge}`}>
          {signal.priority_level}
        </span>
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-gray-500 font-mono font-semibold">
            ID: #{signal.id}
          </span>
          <button 
            onClick={handleFocus}
            className="text-xs hover:bg-gray-800 p-0.5 rounded cursor-pointer"
            title="Focus Map Coordinates"
          >
            🎯
          </button>
        </div>
      </div>

      {/* Raw message block */}
      <div className="text-gray-100 font-semibold italic text-[11px] leading-snug bg-gray-950/80 p-2.5 rounded border border-gray-800/50">
        "{signal.raw_message}"
      </div>

      {/* NLP Metadata breakdown */}
      <div className="flex flex-col gap-1 border-b border-gray-800/50 pb-2">
        <div className="flex items-center justify-between text-[10px]">
          <span className="text-gray-500 font-bold uppercase tracking-wider text-[9px]">Linguistic Flag:</span>
          <span className="text-gray-200 font-semibold">{langLabel}</span>
        </div>
        <div className="flex items-center justify-between text-[10px]">
          <span className="text-gray-500 font-bold uppercase tracking-wider text-[9px]">Survivor Count:</span>
          <span className="text-red-400 font-black font-mono">{signal.survivor_count_estimate || 1} Stranded</span>
        </div>
        <div className="flex items-center justify-between text-[10px]">
          <span className="text-gray-500 font-bold uppercase tracking-wider text-[9px]">AI Geoparsed Location:</span>
          <span className="text-orange-300 font-bold">{signal.location_extracted || 'Sector coordinates'}</span>
        </div>
        <div className="flex items-center justify-between text-[10px]">
          <span className="text-gray-500 font-bold uppercase tracking-wider text-[9px]">NLP Confidence Score:</span>
          <span className="text-cyan-400 font-mono font-bold">{(signal.language_confidence * 100).toFixed(0)}%</span>
        </div>
      </div>

      {/* Dispatching / verification state actions */}
      <div className="flex flex-col gap-2 pt-1">
        {isDispatched ? (
          <div className="bg-blue-950/50 border border-blue-900/60 rounded p-2 text-center text-blue-300 font-black uppercase text-[10px] tracking-wider">
            ⚡ DISPATCHED: {assignedTeam.team_code} ({assignedTeam.status.replace('_', ' ')})
          </div>
        ) : (
          <>
            {/* Inline Verify/Dismiss triggers */}
            <div className="flex items-center gap-2">
              {!signal.is_verified && (
                <button
                  onClick={handleVerify}
                  className="flex-1 bg-cyan-950/65 border border-cyan-800 text-cyan-400 hover:bg-cyan-950 hover:text-cyan-300 font-bold py-1 rounded text-[10px] uppercase cursor-pointer transition-colors"
                >
                  ✓ VERIFY
                </button>
              )}
              <button
                onClick={handleDismiss}
                className="flex-1 bg-red-950/45 border border-red-900 text-red-400 hover:bg-red-950 hover:text-red-300 font-bold py-1 rounded text-[10px] uppercase cursor-pointer transition-colors"
              >
                ✗ DISMISS
              </button>
              
              <button
                onClick={() => setIsDispatching(!isDispatching)}
                className="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-bold py-1 rounded text-[10px] uppercase cursor-pointer transition-colors"
              >
                DISPATCH →
              </button>
            </div>

            {/* Collapsible Dispatch panel */}
            {isDispatching && (
              <div className="flex flex-col gap-1.5 p-2 bg-gray-950 border border-gray-800 rounded animate-fade-in mt-1">
                <label className="text-[9px] uppercase tracking-wider text-gray-500 font-bold">Select Active NDRF Unit:</label>
                <select
                  value={selectedTeamId}
                  onChange={(e) => setSelectedTeamId(e.target.value)}
                  className="bg-gray-900 border border-gray-850 rounded p-1 text-[10px] text-gray-300 focus:outline-none focus:border-blue-600 w-full"
                >
                  <option value="">-- CHOOSE TEAM --</option>
                  {rescueTeams
                    .filter(t => t.status === 'available')
                    .map(t => (
                      <option key={t.id} value={t.id}>
                        {t.team_code} ({t.unit_type})
                      </option>
                    ))
                  }
                </select>
                <div className="flex gap-1">
                  <button
                    onClick={handleDispatch}
                    disabled={!selectedTeamId}
                    className="flex-1 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-850 disabled:text-gray-600 text-white text-[9px] font-black rounded py-1 cursor-pointer transition-colors"
                  >
                    CONFIRM DISPATCH
                  </button>
                  <button
                    onClick={() => setIsDispatching(false)}
                    className="bg-gray-800 hover:bg-gray-700 text-gray-300 text-[9px] font-black rounded px-2 py-1 cursor-pointer"
                  >
                    CANCEL
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
