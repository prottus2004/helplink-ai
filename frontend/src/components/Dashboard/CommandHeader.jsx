import React, { useState, useEffect } from 'react';
import { useHelpLinkStore } from '../../store/useHelpLinkStore';

export default function CommandHeader() {
  const { isLive } = useHelpLinkStore();
  const [time, setTime] = useState(new Date());
  const [liveDisaster, setLiveDisaster] = useState(null);

  // Tick clock every second
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchLiveDisaster = async () => {
      try {
        const response = await fetch('/api/live/disaster-status');
        const data = await response.json();
        setLiveDisaster(data);
      } catch (err) {
        console.warn('Failed to fetch live disaster status:', err);
      }
    };

    fetchLiveDisaster();
    const interval = setInterval(fetchLiveDisaster, 120000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="w-full bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center justify-between select-none relative z-50">

      {/* Left: Branding */}
      <div className="flex items-center gap-3">
        <div className="bg-red-600 text-white font-black px-2.5 py-1 rounded text-base tracking-wider flex items-center justify-center shadow-lg">
          HL
        </div>
        <div>
          <h1 className="text-gray-100 font-extrabold text-lg leading-tight tracking-wider uppercase">
            HelpLink<span className="text-red-500 font-black">.AI</span>
          </h1>
          <p className="text-gray-500 text-[9px] uppercase tracking-widest font-bold">
            Samsung Solve for Tomorrow 2026 | Disaster Operations
          </p>
        </div>
      </div>

      {/* Center: Live digital ticking clock and live disaster status */}
      <div className="flex flex-col items-center">
        <div className="text-gray-100 text-lg font-bold tracking-widest font-mono">
          {time.toLocaleTimeString()}
        </div>
        {liveDisaster?.active_india_disaster ? (
          <div className="text-red-400 text-[10px] tracking-widest uppercase font-black bg-red-950/40 px-2 py-0.5 rounded border border-red-900/30">
            LIVE: {liveDisaster.critical_count} ACTIVE DISASTER(S) IN INDIA
          </div>
        ) : (
          <div className="text-green-400 text-[10px] tracking-widest uppercase font-bold">
            ALL SYSTEMS LIVE
          </div>
        )}
      </div>

      {/* Right: Socket Status */}
      <div className="flex items-center gap-4">
        {/* Connection Beacon */}
        <div className="flex items-center gap-2 bg-gray-950 px-3 py-1.5 rounded border border-gray-800">
          <span className={`w-2 h-2 rounded-full ${isLive ? 'bg-green-500 animate-pulse' : 'bg-red-500 animate-blink'}`} />
          <span className="text-[10px] uppercase tracking-widest font-extrabold text-gray-300">
            {isLive ? 'COM-LINK OK' : 'COM-LINK LOSS'}
          </span>
        </div>
      </div>
    </header>
  );
}
