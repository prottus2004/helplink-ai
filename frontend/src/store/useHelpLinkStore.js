import { create } from 'zustand';

export const useHelpLinkStore = create((set) => ({
  // Core Operational States
  sosSignals: [],
  satelliteZones: [],
  cellularAnomalies: [],
  rescueTeams: [],
  summary: {
    total_sos: 0,
    critical_count: 0,
    high_count: 0,
    teams_deployed: 0,
    lives_estimated: 0,
    last_updated: '--'
  },
  isLive: false,
  timeline: [],
  focusedLocation: null,

  // Atomic Actions
  setFocusedLocation: (loc) => set({ focusedLocation: loc }),
  addTimelineEvent: (event) => set((state) => ({ timeline: [event, ...state.timeline].slice(0, 50) })),
  setTimeline: (events) => set({ timeline: events }),
  setSOSSignals: (signals) => set({ sosSignals: signals }),
  
  addNewSOS: (signal) => set((state) => {
    // Avoid duplicate insertions
    if (state.sosSignals.some(s => s.id === signal.id)) {
      return state;
    }
    
    const updatedSignals = [signal, ...state.sosSignals];
    
    // Increment local stats immediately to show zero-latency counts
    const countIncrement = signal.survivor_count_estimate || 1;
    const isCritical = signal.priority_level === 'CRITICAL';
    const isHigh = signal.priority_level === 'HIGH';

    return {
      sosSignals: updatedSignals,
      summary: {
        ...state.summary,
        total_sos: state.summary.total_sos + 1,
        critical_count: state.summary.critical_count + (isCritical ? 1 : 0),
        high_count: state.summary.high_count + (isHigh ? 1 : 0),
        lives_estimated: state.summary.lives_estimated + countIncrement,
        last_updated: new Date().toLocaleTimeString()
      }
    };
  }),
  
  removeSOS: (id) => set((state) => {
    const target = state.sosSignals.find(s => s.id === id);
    if (!target) return state;

    const countDecrement = target.survivor_count_estimate || 1;
    const isCritical = target.priority_level === 'CRITICAL';
    const isHigh = target.priority_level === 'HIGH';

    return {
      sosSignals: state.sosSignals.filter(s => s.id !== id),
      summary: {
        ...state.summary,
        total_sos: Math.max(state.summary.total_sos - 1, 0),
        critical_count: Math.max(state.summary.critical_count - (isCritical ? 1 : 0), 0),
        high_count: Math.max(state.summary.high_count - (isHigh ? 1 : 0), 0),
        lives_estimated: Math.max(state.summary.lives_estimated - countDecrement, 0)
      }
    };
  }),

  verifySOS: (id, newScore, newLevel) => set((state) => ({
    sosSignals: state.sosSignals.map(s => 
      s.id === id 
        ? { ...s, is_verified: true, priority_score: newScore, priority_level: newLevel }
        : s
    )
  })),

  setSatelliteZones: (zones) => set({ satelliteZones: zones }),
  setCellularAnomalies: (anoms) => set({ cellularAnomalies: anoms }),
  setRescueTeams: (teams) => set({ rescueTeams: teams }),
  
  updateTeam: (teamUpdate) => set((state) => {
    const updatedTeams = state.rescueTeams.map((team) => {
      if (team.id === teamUpdate.id) {
        return { ...team, ...teamUpdate };
      }
      return team;
    });

    // Re-calculate deployed count from current team states
    const deployedCount = updatedTeams.filter(t => t.status !== 'available').length;

    return {
      rescueTeams: updatedTeams,
      summary: {
        ...state.summary,
        teams_deployed: deployedCount
      }
    };
  }),

  setSummary: (summaryData) => set({ summary: summaryData }),
  setLive: (liveStatus) => set({ isLive: liveStatus })
}));
