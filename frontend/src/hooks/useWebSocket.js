import { useEffect, useRef } from 'react';
import { useHelpLinkStore } from '../store/useHelpLinkStore';

export const useWebSocket = () => {
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);
  const {
    setLive,
    addNewSOS,
    removeSOS,
    verifySOS,
    updateTeam,
    setSummary,
    addTimelineEvent,
    setSatelliteZones,
    setCellularAnomalies
  } = useHelpLinkStore();

  const connect = () => {
    // Clear any existing reconnect triggers
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }

    // Smart URL: uses environment variable if set, otherwise uses relative path
    // In local dev, Vite proxy forwards /ws to localhost:8000
    const getWebSocketUrl = () => {
      if (import.meta.env.VITE_WS_URL) {
        return import.meta.env.VITE_WS_URL;
      }
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      return `${protocol}//${window.location.host}/ws`;
    };

    const wsUrl = getWebSocketUrl();
    console.log(`[WebSocket] Connecting to ${wsUrl}...`);
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('[WebSocket] Connected successfully! Telemetry live.');
      setLive(true);
    };

    ws.current.onclose = () => {
      console.warn('[WebSocket] Connection closed. Attempting reconnect in 5s...');
      setLive(false);
      reconnectTimeout.current = setTimeout(connect, 5000);
    };

    ws.current.onerror = (err) => {
      console.error('[WebSocket ERROR] Socket anomaly caught: ', err);
      ws.current.close();
    };

    ws.current.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const { type, data } = payload;
        
        console.log(`[WebSocket EVENT] Received: ${type}`, data);

        switch (type) {
          case 'new_sos':
            addNewSOS(data);
            // Append a timeline event for visibility
            addTimelineEvent({
              timestamp: new Date(data.created_at).toLocaleTimeString(),
              event_type: 'sos_received',
              title: `Live SOS: ${data.language_detected}`,
              description: `Location: ${data.location_extracted || 'Coordinates'}. Msg: ${data.raw_message.substring(0, 45)}...`,
              priority: data.priority_level
            });
            break;
            
          case 'sos_deleted':
            removeSOS(data.id);
            break;
            
          case 'sos_verified':
            verifySOS(data.id, data.priority_score, data.priority_level);
            break;
            
          case 'team_update':
            updateTeam(data);
            break;
            
          case 'summary_update':
            setSummary(data);
            break;
            
          case 'timeline_update':
            addTimelineEvent(data);
            break;

          case 'satellite_zones':
            setSatelliteZones(data);
            break;

          case 'cellular_anomalies':
            setCellularAnomalies(data);
            break;

          default:
            console.log(`[WebSocket] Unhandled payload type: ${type}`);
        }
      } catch (err) {
        console.error('[WebSocket ERROR] Failed to parse message body: ', err);
      }
    };
  };

  useEffect(() => {
    connect();
    
    return () => {
      if (ws.current) {
        // Remove close listener to prevent auto-reconnect on teardown
        ws.current.onclose = null;
        ws.current.close();
      }
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, []);

  return { isConnected: ws.current?.readyState === WebSocket.OPEN };
};
