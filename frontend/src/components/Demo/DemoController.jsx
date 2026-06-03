import React, { useState, useEffect } from 'react';
import { useHelpLinkStore } from '../../store/useHelpLinkStore';
import axios from 'axios';

export default function DemoController() {
  const { sosSignals, rescueTeams } = useHelpLinkStore();
  const [dataStatus, setDataStatus] = useState(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await axios.get('/api/live/data-status');
        setDataStatus(res.data);
      } catch (err) {
        console.error('[API] Failed to fetch data status:', err);
      }
    };
    fetchStatus();
  }, []);

  const getSourceStatus = (source) => {
    if (!dataStatus) return 'unknown';
    const value = dataStatus[source];
    if (value === 'real' || value === 'live') return 'live';
    if (value === 'simulated') return 'demo';
    return value;
  };

  return (
    <div className="w-full h-full flex flex-col bg-gray-900 border border-gray-800 rounded-lg overflow-hidden glass-panel select-none">
      {/* Controller Header */}
      <div className="px-4 py-3 bg-gray-950/80 border-b border-gray-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          <h2 className="text-gray-100 font-extrabold text-xs tracking-wider uppercase">
            OPERATIONS DASHBOARD
          </h2>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
          <span className="text-[9px] text-green-400 font-bold uppercase tracking-wider">LIVE</span>
        </div>
      </div>

      <div className="flex-1 p-4 flex flex-col gap-3 justify-between overflow-y-auto">
        {/* Data Source Status */}
        <div className="flex flex-col gap-2 bg-gray-950/80 p-3 rounded border border-gray-800/80">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase tracking-widest text-cyan-400 font-black">
              REAL-TIME DATA SOURCES
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {[
              { label: 'GDACS Disasters', key: 'gdacs' },
              { label: 'Twitter/X SOS', key: 'tweets' },
              { label: 'Cell Towers', key: 'towers' },
              { label: 'Satellite SAR', key: 'satellite' },
            ].map(({ label, key }) => {
              const status = getSourceStatus(key);
              return (
                <div key={key} className="flex items-center justify-between text-[10px]">
                  <span className="text-gray-400 font-medium">{label}</span>
                  <span className={`font-black uppercase text-[9px] tracking-wider ${
                    status === 'live' ? 'text-green-400' : status === 'demo' ? 'text-amber-400' : 'text-gray-600'
                  }`}>
                    {status === 'live' ? '● LIVE' : status === 'demo' ? '◆ DEMO' : '○ OFF'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Operational Statistics */}
        <div className="grid grid-cols-2 gap-2 bg-gray-950/40 p-3 rounded border border-gray-800/40">
          <div className="flex flex-col border-r border-gray-850 pr-2">
            <span className="text-[8.5px] uppercase tracking-widest text-gray-500 font-bold mb-0.5">SOS Languages</span>
            <span className="text-sm font-black font-mono text-cyan-400">
              {new Set(sosSignals.map(s => s.language_detected)).size || 0} Dialects
            </span>
          </div>

          <div className="flex flex-col pl-2">
            <span className="text-[8.5px] uppercase tracking-widest text-gray-500 font-bold mb-0.5">SOS Signals</span>
            <span className="text-sm font-black font-mono text-red-400">
              {sosSignals.length} Active
            </span>
          </div>

          <div className="col-span-2 border-t border-gray-850/80 pt-2 flex flex-col">
            <span className="text-[8.5px] uppercase tracking-widest text-gray-500 font-bold mb-0.5">Rescue Teams</span>
            <span className="text-sm font-black font-mono text-green-400">
              {rescueTeams.length} Units
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
