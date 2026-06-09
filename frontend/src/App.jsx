import React, { useEffect, useState } from 'react';
import CommandHeader from './components/Dashboard/CommandHeader';
import StatCard from './components/Dashboard/StatCard';
import SOSInbox from './components/SOS/SOSInbox';
import RescueMap from './components/Map/RescueMap';
import AlertFeed from './components/Dashboard/AlertFeed';
import TeamTracker from './components/Dashboard/TeamTracker';
import { useWebSocket } from './hooks/useWebSocket';
import { useRescueData } from './hooks/useRescueData';
import { useHelpLinkStore } from './store/useHelpLinkStore';
import EmergencyReport from './pages/EmergencyReport';

export default function App() {
  // Mount WebSocket Pipeline
  useWebSocket();
  
  const { fetchAllData } = useRescueData();
  const { summary } = useHelpLinkStore();
  const [showSplash, setShowSplash] = useState(true);

  // Load initial database metrics on EOC launch
  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // Loading screen splash timer (2 seconds)
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowSplash(false);
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  if (showSplash) {
    return (
      <div className="fixed inset-0 bg-gray-950 flex flex-col items-center justify-center z-[9999] select-none text-center p-6">
        
        {/* Glowing SFT logo container */}
        <div className="relative mb-6">
          <div className="absolute inset-0 bg-red-600 rounded-full blur-xl opacity-20 scale-150 animate-pulse"></div>
          <div className="w-20 h-20 bg-gradient-to-br from-red-600 to-red-800 text-white text-3xl font-black rounded-3xl flex items-center justify-center shadow-2xl relative border border-red-500/30">
            HL
          </div>
        </div>

        {/* Brand Title */}
        <h1 className="text-gray-100 text-3xl font-black tracking-widest uppercase mb-1">
          HelpLink<span className="text-red-500 font-extrabold">.AI</span>
        </h1>
        <p className="text-cyan-400 text-[10px] font-black uppercase tracking-widest mb-4">
          AI-Powered Disaster Rescue Coordination System
        </p>

        {/* Horizontal separator */}
        <div className="w-16 h-0.5 bg-gray-800 rounded mb-8"></div>

        {/* Showcase Badge */}
        <div className="bg-gray-900 border border-gray-800 rounded-lg px-4 py-2 mb-12 shadow-lg max-w-sm">
          <p className="text-[10px] text-gray-500 uppercase tracking-widest font-extrabold mb-0.5">National Presentation Entry</p>
          <p className="text-xs font-bold text-gray-300 uppercase tracking-wider">
            Samsung Solve for Tomorrow 2026
          </p>
          <p className="text-[9px] text-amber-500 uppercase tracking-widest font-black mt-0.5">
            AI Living for India | NDRF Operations Portal
          </p>
        </div>

        {/* Progress Bar Loader */}
        <div className="w-48 bg-gray-900 h-1 rounded-full overflow-hidden mb-2">
          <div className="bg-red-600 h-1 rounded-full animate-pulse" style={{ width: '100%', transition: 'width 2s ease-in-out' }}></div>
        </div>
        <p className="text-[9px] text-gray-600 font-semibold uppercase tracking-widest animate-blink">
          SYNCHRONIZING SATELLITE RADAR ARRAYS...
        </p>

      </div>
    );
  }

  // Simple pathname-based routing for public emergency intake page
  if (typeof window !== 'undefined' && (window.location.pathname === '/emergency' || window.location.pathname === '/emergency/')) {
    return <EmergencyReport />
  }

  return (
    <div className="w-screen h-screen flex flex-col bg-gray-950 text-gray-100 overflow-hidden">
      
      {/* 1. Global Navigation Command Header */}
      <CommandHeader />

      {/* 2. Main Dashboard Split Arena */}
      <main className="flex-1 min-h-0 p-4 grid grid-cols-1 lg:grid-cols-4 gap-4">
        
        {/* Column 1 (25%): Classified SOS Signals Inbox */}
        <section className="lg:col-span-1 h-full min-h-0">
          <SOSInbox />
        </section>

        {/* Column 2 & 3 (50%): Central Rescue Command Leaflet Map */}
        <section className="lg:col-span-2 h-full min-h-0">
          <RescueMap />
        </section>

        {/* Column 4 (25%): Live Feeds and Unit Trackers */}
        <section className="lg:col-span-1 h-full min-h-0 flex flex-col gap-4">
          <div className="flex-1 min-h-0">
            <AlertFeed />
          </div>
          <div className="h-48">
            <TeamTracker />
          </div>
        </section>

      </main>

      {/* 3. Ticking Statistical Counter Strip (Row below Split grid) */}
      <div className="px-4 py-2 border-t border-gray-800 bg-gray-950 select-none">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          
          <StatCard
            label="Total SOS Recd"
            value={summary.total_sos}
            icon="🚨"
            color="gray"
            trend="↑ Live"
          />

          <StatCard
            label="Critical Hotspots"
            value={summary.critical_count}
            icon="🔴"
            color="red"
            trend={summary.critical_count > 0 ? "↑ Urgent" : ""}
          />

          <StatCard
            label="Stranded Survivors"
            value={summary.lives_estimated}
            icon="👨‍👩‍👧‍👦"
            color="orange"
            trend={summary.lives_estimated > 0 ? `↑ ${summary.lives_estimated} At Risk` : ""}
          />

          <StatCard
            label="Deployed Teams"
            value={summary.teams_deployed}
            icon="🚤"
            color="cyan"
            trend={summary.teams_deployed > 0 ? "↑ Active" : ""}
          />

          <StatCard
            label="Estimated Coverage"
            value={100}
            icon="🛰️"
            color="green"
            trend="100% SAR"
          />

        </div>
      </div>

    </div>
  );
}
