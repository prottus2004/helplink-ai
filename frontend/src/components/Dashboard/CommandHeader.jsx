import React, { useState, useEffect } from 'react';
import { useHelpLinkStore } from '../../store/useHelpLinkStore';
import { useRescueData } from '../../hooks/useRescueData';

export default function CommandHeader() {
  const { activeScenario, isLive } = useHelpLinkStore();
  const { triggerLoadScenario } = useRescueData();
  const [time, setTime] = useState(new Date());
  const [loading, setLoading] = useState(false);
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

  const handleScenarioChange = async (e) => {
    const val = e.target.value;
    if (!val) return;
    
    setLoading(true);
    try {
      await triggerLoadScenario(val);
    } catch (err) {
      alert(`Failed to load scenario: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

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

      {/* Center: Live digital ticking clock and active scenario metadata */}
      <div className="flex flex-col items-center">
        <div className="text-gray-100 text-lg font-bold tracking-widest font-mono">
          {time.toLocaleTimeString()}
        </div>
        {activeScenario ? (
          <div className="text-amber-400 text-[10px] tracking-widest uppercase font-black bg-amber-950/40 px-2 py-0.5 rounded border border-amber-900/30">
            ACTIVE SITE: {activeScenario.scenario_name.split(',')[0]}
          </div>
        ) : (
          <div className="text-gray-500 text-[10px] tracking-widest uppercase font-bold">
            INITIALIZING CORE DATA STREAMS...
          </div>
        )}
      </div>

      {/* Right: Socket Status, Demo Mode selector */}
      <div className="flex items-center gap-4">
        {/* Connection Beacon */}
        <div className="flex items-center gap-2 bg-gray-950 px-3 py-1.5 rounded border border-gray-800">
          <span className={`w-2 h-2 rounded-full ${isLive ? 'bg-green-500 animate-pulse' : 'bg-red-500 animate-blink'}`} />
          <span className="text-[10px] uppercase tracking-widest font-extrabold text-gray-300">
            {isLive ? 'COM-LINK OK' : 'COM-LINK LOSS'}
          </span>
        </div>

        {/* Dynamic Scenario Swapper */}
        <div className="flex items-center gap-2">
          {liveDisaster?.active_india_disaster && (
            <div
              style={{
                background: '#FCEBEB',
                color: '#791F1F',
                border: '1px solid #F09595',
                borderRadius: 4,
                padding: '3px 10px',
                fontSize: 11,
                fontWeight: 600,
                animation: 'pulse 2s infinite',
              }}
            >
              LIVE: {liveDisaster.critical_count} ACTIVE DISASTER(S) IN INDIA
            </div>
          )}
          <select
            value={activeScenario?.id || 'wayanad'}
            onChange={handleScenarioChange}
            disabled={loading}
            className="bg-gray-950 border border-gray-800 rounded px-3 py-1.5 text-xs text-gray-300 focus:outline-none focus:border-red-600 cursor-pointer disabled:opacity-50"
          >
            <option value="wayanad">SITE 1: KERALA (WAYANAD LANDSLIDE)</option>
            <option value="assam">SITE 2: ASSAM (BRAHMAPUTRA FLOODS)</option>
            <option value="bihar">SITE 3: NORTH BIHAR FLASH FLOODS</option>
          </select>
        </div>
      </div>

      {/* Global Scenario loading curtain */}
      {loading && (
        <div className="absolute inset-0 bg-gray-950/80 backdrop-blur-sm z-[999] flex items-center justify-center text-xs text-amber-400 font-extrabold tracking-widest uppercase select-none">
          <span className="animate-pulse">BOOTSTRAPPING GEOSPATIAL DATABASE LAYER...</span>
        </div>
      )}
    </header>
  );
}
