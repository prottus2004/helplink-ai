import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function ScenarioPanel() {
  const [disasterData, setDisasterData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchLiveDisasters = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/live/disasters');
      setDisasterData(res.data);
    } catch (err) {
      console.error('[API] Failed to fetch live disasters:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLiveDisasters();
    // Refresh every 5 minutes
    const interval = setInterval(fetchLiveDisasters, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const totalEvents = disasterData?.total || 0;
  const indiaEvents = disasterData?.india_events?.length || 0;
  const southAsiaEvents = disasterData?.south_asia_events?.length || 0;

  const getAlertColor = (alert) => {
    switch (alert) {
      case 'Red': return 'bg-red-500';
      case 'Orange': return 'bg-orange-500';
      case 'Green': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="w-full bg-gray-900 border border-gray-800 rounded-lg p-4 flex flex-col md:flex-row gap-4 justify-between items-stretch select-none relative overflow-hidden">
      {/* Live Disaster Monitor */}
      <div className="flex-1 flex flex-col gap-2">
        <div className="flex items-center gap-2 mb-1">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          <h3 className="text-green-400 font-extrabold text-[10px] uppercase tracking-wider">
            LIVE DISASTER MONITOR — GDACS REAL-TIME FEED
          </h3>
        </div>

        <div className="grid grid-cols-3 gap-3">
          {/* India Events */}
          <div className="p-3 rounded border border-red-900/50 bg-red-950/10 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-100 font-extrabold text-[11px] uppercase tracking-wide">India</span>
                <span className="px-1 rounded text-[8px] border font-bold uppercase tracking-widest bg-red-950 text-red-400 border-red-900">
                  ACTIVE
                </span>
              </div>
              <div className="text-[10px] text-gray-500 font-semibold mb-1.5 uppercase">South Asia Region</div>
              <p className="text-[10px] text-gray-400 leading-normal font-medium mb-3">
                {indiaEvents} active event{indiaEvents !== 1 ? 's' : ''} detected across Indian territory via GDACS
              </p>
            </div>
            <div className="text-xl font-black text-red-400">{indiaEvents}</div>
          </div>

          {/* South Asia */}
          <div className="p-3 rounded border border-orange-900/50 bg-orange-950/10 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-100 font-extrabold text-[11px] uppercase tracking-wide">South Asia</span>
                <span className="px-1 rounded text-[8px] border font-bold uppercase tracking-widest bg-orange-950 text-orange-400 border-orange-900">
                  REGIONAL
                </span>
              </div>
              <div className="text-[10px] text-gray-500 font-semibold mb-1.5 uppercase">Multi-country Zone</div>
              <p className="text-[10px] text-gray-400 leading-normal font-medium mb-3">
                {southAsiaEvents} active event{southAsiaEvents !== 1 ? 's' : ''} across IND, LKA, BGD, NPL, PAK via GDACS
              </p>
            </div>
            <div className="text-xl font-black text-orange-400">{southAsiaEvents}</div>
          </div>

          {/* Global */}
          <div className="p-3 rounded border border-gray-800 bg-gray-950/40 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-100 font-extrabold text-[11px] uppercase tracking-wide">Global</span>
                <span className="px-1 rounded text-[8px] border font-bold uppercase tracking-widest bg-gray-800 text-gray-400 border-gray-700">
                  WORLDWIDE
                </span>
              </div>
              <div className="text-[10px] text-gray-500 font-semibold mb-1.5 uppercase">All Continents</div>
              <p className="text-[10px] text-gray-400 leading-normal font-medium mb-3">
                {totalEvents} total active disaster events monitored via GDACS Live API
              </p>
            </div>
            <div className="text-xl font-black text-gray-400">{totalEvents}</div>
          </div>
        </div>

        {/* Live event list */}
        {disasterData?.south_asia_events?.length > 0 && (
          <div className="mt-2 max-h-32 overflow-y-auto">
            <div className="text-[9px] text-gray-500 uppercase tracking-widest font-bold mb-1">Active Events</div>
            <div className="grid grid-cols-2 gap-1">
              {disasterData.south_asia_events.slice(0, 6).map((ev) => (
                <div key={ev.id} className="flex items-center gap-1.5 text-[9px] text-gray-300">
                  <span className={`w-1.5 h-1.5 rounded-full ${getAlertColor(ev.alert)}`}></span>
                  <span className="font-semibold">{ev.name}</span>
                  <span className="text-gray-500">{ev.country}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Data source info */}
      <div className="hidden md:flex w-56 flex-col justify-center gap-2 bg-gray-950/40 p-3 rounded border border-gray-800/50">
        <div className="text-[9px] uppercase tracking-widest text-gray-500 font-bold border-b border-gray-800 pb-1 mb-1">
          DATA SOURCES
        </div>
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-[10px] text-gray-400">
            <span>GDACS EU System:</span>
            <span className="text-green-400 font-bold">LIVE</span>
          </div>
          <div className="flex items-center justify-between text-[10px] text-gray-400">
            <span>Twitter/X SOS:</span>
            <span className="text-amber-400 font-bold">{
              import.meta.env.VITE_TWITTER_TOKEN ? 'CONFIGURED' : 'NO KEY'
            }</span>
          </div>
          <div className="flex items-center justify-between text-[10px] text-gray-400">
            <span>OpenCelliD Towers:</span>
            <span className="text-amber-400 font-bold">{
              import.meta.env.VITE_OPENCELLID_KEY ? 'CONFIGURED' : 'NO KEY'
            }</span>
          </div>
          <div className="flex items-center justify-between text-[10px] text-gray-400">
            <span>Copernicus SAR:</span>
            <span className="text-amber-400 font-bold">{
              import.meta.env.VITE_COPERNICUS_USER ? 'CONFIGURED' : 'NO KEY'
            }</span>
          </div>
        </div>
        <button
          onClick={fetchLiveDisasters}
          disabled={loading}
          className="w-full text-[9.5px] font-black uppercase bg-gray-800 hover:bg-gray-700 text-gray-300 rounded py-1.5 border border-gray-700 cursor-pointer mt-2"
        >
          REFRESH LIVE DATA
        </button>
      </div>

      {loading && (
        <div className="absolute inset-0 bg-gray-950/80 backdrop-blur-sm z-[999] flex items-center justify-center text-xs text-green-400 font-extrabold tracking-widest uppercase">
          <span className="animate-pulse">REFRESHING GDACS FEED...</span>
        </div>
      )}
    </div>
  );
}
