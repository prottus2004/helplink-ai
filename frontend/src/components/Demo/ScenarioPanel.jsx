import React, { useState } from 'react';
import { useHelpLinkStore } from '../../store/useHelpLinkStore';
import { useRescueData } from '../../hooks/useRescueData';

export default function ScenarioPanel() {
  const { activeScenario } = useHelpLinkStore();
  const { triggerLoadScenario } = useRescueData();
  const [loading, setLoading] = useState(false);
  const [simulationSpeed, setSimulationSpeed] = useState(1);
  const [isSimulating, setIsSimulating] = useState(true);

  const scenariosList = [
    {
      id: 'wayanad',
      name: 'Wayanad Landslides',
      region: 'Kerala, India',
      severity: 'CATASTROPHIC',
      description: 'July 2024 massive cloudburst triggered major hill mudslides in Meppadi & Vythiri, separating communities.',
      color: 'border-red-900/50 hover:border-red-500 bg-red-950/10',
      badge: 'bg-red-950 text-red-400 border-red-900'
    },
    {
      id: 'assam',
      name: 'Brahmaputra Floods',
      region: 'Morigaon, Assam',
      severity: 'SEVERE',
      description: 'Major embankment breaches flooded agricultural lowlands. High speed currents and stranded clusters.',
      color: 'border-orange-900/50 hover:border-orange-500 bg-orange-950/10',
      badge: 'bg-orange-950 text-orange-400 border-orange-900'
    },
    {
      id: 'bihar',
      name: 'North Bihar Floods',
      region: 'Muzaffarpur, Bihar',
      severity: 'SEVERE',
      description: 'Overflow of Bagmati river submerged residential blocks, forcing thousands onto rooftops.',
      color: 'border-yellow-900/50 hover:border-yellow-500 bg-yellow-950/10',
      badge: 'bg-yellow-950 text-yellow-400 border-yellow-900'
    }
  ];

  const handleLoadScenario = async (id) => {
    setLoading(true);
    try {
      await triggerLoadScenario(id);
    } catch (err) {
      alert(`Failed to load scenario: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    if (activeScenario) {
      await handleLoadScenario(activeScenario.id);
    } else {
      await handleLoadScenario('wayanad');
    }
  };

  return (
    <div className="w-full bg-gray-900 border border-gray-800 rounded-lg p-4 glass-panel flex flex-col md:flex-row gap-4 justify-between items-stretch select-none relative overflow-hidden">
      
      {/* Scenario Selection Section */}
      <div className="flex-1 flex flex-col gap-2">
        <div className="flex items-center gap-2 mb-1">
          <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
          <h3 className="text-amber-400 font-extrabold text-[10px] uppercase tracking-wider">
            DEMO SCENARIOS & SIMULATION CONTROLS
          </h3>
        </div>

        {/* List of cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {scenariosList.map((sc) => {
            const isActive = activeScenario?.id === sc.id;
            return (
              <div
                key={`sc-card-${sc.id}`}
                className={`p-3 rounded border flex flex-col justify-between transition-all duration-300 ${sc.color} ${isActive ? 'ring-1 ring-amber-500 bg-amber-950/10 border-amber-800' : ''}`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-gray-100 font-extrabold text-[11px] uppercase tracking-wide">{sc.name}</span>
                    <span className={`px-1 rounded text-[8px] border font-bold uppercase tracking-widest ${sc.badge}`}>
                      {sc.severity}
                    </span>
                  </div>
                  <div className="text-[10px] text-gray-500 font-semibold mb-1.5 uppercase">{sc.region}</div>
                  <p className="text-[10px] text-gray-400 leading-normal font-medium mb-3">
                    {sc.description}
                  </p>
                </div>
                
                <button
                  type="button"
                  onClick={() => handleLoadScenario(sc.id)}
                  disabled={loading}
                  className={`w-full text-[9px] font-black uppercase py-1 rounded cursor-pointer transition-colors ${isActive ? 'bg-amber-600 text-white hover:bg-amber-500' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}`}
                >
                  {isActive ? '✓ CURRENT DISASTER' : 'LOAD SCENARIO'}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Vertical separation */}
      <div className="hidden md:block w-px bg-gray-800/80 self-stretch my-2"></div>

      {/* Simulator Control Section */}
      <div className="w-full md:w-56 flex flex-col justify-between gap-3 bg-gray-950/40 p-3 rounded border border-gray-800/50">
        <div>
          <h4 className="text-gray-300 font-extrabold text-[9px] uppercase tracking-wider mb-2 border-b border-gray-800 pb-1">
            SIMULATION SPEED
          </h4>
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between text-[10px] text-gray-400">
              <span>Dynamic Ticks:</span>
              <span className={`font-bold ${isSimulating ? 'text-green-400 animate-pulse' : 'text-gray-600'}`}>
                {isSimulating ? 'SIMULATING LIVE FEED' : 'PAUSED'}
              </span>
            </div>
            
            {/* Speed slider */}
            <div className="flex gap-1.5">
              {[1, 2, 5].map((speed) => (
                <button
                  key={`speed-${speed}`}
                  onClick={() => setSimulationSpeed(speed)}
                  className={`flex-1 text-[10px] font-black rounded py-1 cursor-pointer transition-colors ${simulationSpeed === speed ? 'bg-amber-600 text-white' : 'bg-gray-900 text-gray-400 hover:bg-gray-800'}`}
                >
                  {speed}x
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Global actions */}
        <div className="flex flex-col gap-1.5">
          <button
            onClick={() => setIsSimulating(!isSimulating)}
            className={`w-full text-[9.5px] font-black uppercase py-1.5 rounded cursor-pointer transition-colors ${isSimulating ? 'bg-red-950/70 border border-red-900 text-red-400 hover:bg-red-950' : 'bg-green-950/70 border border-green-900 text-green-400 hover:bg-green-950'}`}
          >
            {isSimulating ? 'PAUSE LIVE SIMULATION' : 'RESUME LIVE SIMULATION'}
          </button>
          
          <button
            onClick={handleReset}
            disabled={loading}
            className="w-full text-[9.5px] font-black uppercase bg-gray-800 hover:bg-gray-700 text-gray-300 rounded py-1.5 border border-gray-700 cursor-pointer"
          >
            RESET SCENARIO STATE 🔄
          </button>
        </div>
      </div>

      {/* Loading curtain */}
      {loading && (
        <div className="absolute inset-0 bg-gray-950/80 backdrop-blur-sm z-[999] flex items-center justify-center text-xs text-amber-400 font-extrabold tracking-widest uppercase select-none">
          <span className="animate-pulse">BOOTSTRAPPING GEOSPATIAL DATABASE LAYER...</span>
        </div>
      )}

    </div>
  );
}
