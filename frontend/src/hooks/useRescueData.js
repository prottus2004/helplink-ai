import axios from 'axios';
import { useHelpLinkStore } from '../store/useHelpLinkStore';
import { useCallback } from 'react';

// Relative paths leverage Vite dev server proxy to target http://localhost:8000
const API_BASE = '/api';

export const useRescueData = () => {
  const {
    setSOSSignals,
    setSatelliteZones,
    setCellularAnomalies,
    setRescueTeams,
    setSummary,
    setTimeline,
    setFocusedLocation
  } = useHelpLinkStore();

  const fetchSummary = useCallback(async () => {
    try {
      const res = await axios.get(`${API_BASE}/alerts/summary`);
      setSummary(res.data);
      return res.data;
    } catch (err) {
      console.error('[API ERROR] Failed to fetch summary counts:', err);
    }
  }, [setSummary]);

  const fetchSOSFeed = useCallback(async () => {
    try {
      const res = await axios.get(`${API_BASE}/sos/feed`);
      setSOSSignals(res.data);
      return res.data;
    } catch (err) {
      console.error('[API ERROR] Failed to fetch SOS signal feed:', err);
    }
  }, [setSOSSignals]);

  const fetchTeams = useCallback(async () => {
    try {
      const res = await axios.get(`${API_BASE}/teams/`);
      setRescueTeams(res.data);
      return res.data;
    } catch (err) {
      console.error('[API ERROR] Failed to fetch rescue teams:', err);
    }
  }, [setRescueTeams]);

  const fetchTimeline = useCallback(async () => {
    try {
      const res = await axios.get(`${API_BASE}/alerts/timeline`);
      setTimeline(res.data);
      return res.data;
    } catch (err) {
      console.error('[API ERROR] Failed to fetch operations logs timeline:', err);
    }
  }, [setTimeline]);

  const fetchMapLayers = useCallback(async () => {
    try {
      const satRes = await axios.get(`${API_BASE}/map/satellite-zones`);
      setSatelliteZones(satRes.data);
      
      const cellRes = await axios.get(`${API_BASE}/map/cellular-anomalies`);
      setCellularAnomalies(cellRes.data);
      
      // Return map coordinates
      return { 
        satellite: satRes.data, 
        cellular: cellRes.data 
      };
    } catch (err) {
      console.error('[API ERROR] Failed to fetch map layer vectors:', err);
    }
  }, [setSatelliteZones, setCellularAnomalies]);

  const fetchAllData = useCallback(async () => {
    console.log('[API] Loading HelpLink operations environment...');
    await Promise.all([
      fetchSummary(),
      fetchSOSFeed(),
      fetchTeams(),
      fetchTimeline(),
      fetchMapLayers()
    ]);
  }, [fetchSummary, fetchSOSFeed, fetchTeams, fetchTimeline, fetchMapLayers]);

  // Dispatch control actions
  const dispatchTeam = async (teamId, signalId) => {
    try {
      const res = await axios.post(`${API_BASE}/teams/dispatch`, {
        team_id: teamId,
        signal_id: signalId
      });
      // Team and timeline states are updated automatically via WebSockets broadcast
      return res.data;
    } catch (err) {
      console.error('[API ERROR] Rescue dispatch request failed:', err);
      throw err;
    }
  };

  const updateTeamStatus = async (teamId, newStatus) => {
    try {
      const res = await axios.put(`${API_BASE}/teams/${teamId}/status`, {
        status: newStatus
      });
      return res.data;
    } catch (err) {
      console.error('[API ERROR] Team status update failed:', err);
      throw err;
    }
  };

  const submitManualSOS = async (message, lat, lng, language = null) => {
    try {
      const res = await axios.post(`${API_BASE}/sos/submit`, {
        message,
        latitude: lat,
        longitude: lng,
        source: 'manual',
        language
      });
      // Added and broadcasted automatically via WebSocket
      return res.data;
    } catch (err) {
      console.error('[API ERROR] Manual SOS submission failed:', err);
      throw err;
    }
  };

  const verifySOSSignal = async (id) => {
    try {
      const res = await axios.put(`${API_BASE}/sos/${id}/verify`);
      return res.data;
    } catch (err) {
      console.error('[API ERROR] SOS verification update failed:', err);
      throw err;
    }
  };

  const dismissSOSSignal = async (id) => {
    try {
      const res = await axios.delete(`${API_BASE}/sos/${id}`);
      return res.data;
    } catch (err) {
      console.error('[API ERROR] SOS dismissal request failed:', err);
      throw err;
    }
  };

  return {
    fetchAllData,
    fetchSummary,
    fetchSOSFeed,
    fetchTeams,
    fetchTimeline,
    fetchMapLayers,
    dispatchTeam,
    updateTeamStatus,
    submitManualSOS,
    verifySOSSignal,
    dismissSOSSignal,
    setFocusedLocation
  };
};
