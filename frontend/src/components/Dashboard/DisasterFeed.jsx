import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = '/api';

const ALERT_COLORS = {
  Red: 'border-red-500 bg-red-950/40 text-red-300',
  Orange: 'border-orange-500 bg-orange-950/40 text-orange-300',
  Green: 'border-green-500 bg-green-950/40 text-green-300',
};

function DisasterCard({ event, variant = 'india' }) {
  const badgeClass = variant === 'india'
    ? 'bg-red-600 text-white text-[8px] font-black px-1.5 py-0.5 rounded uppercase tracking-wider'
    : 'bg-purple-600 text-white text-[8px] font-black px-1.5 py-0.5 rounded uppercase tracking-wider';

  const alertClass = ALERT_COLORS[event.alert] || ALERT_COLORS.Green;

  return (
    <div className={`border rounded p-2 ${alertClass}`}>
      <div className="flex items-center justify-between gap-1 mb-1">
        <span className={badgeClass}>
          {variant === 'india' ? '🇮🇳 India' : '🌏 South Asia'}
        </span>
        <span className="text-[8px] font-bold uppercase">{event.alert}</span>
      </div>
      <p className="text-[10px] font-bold leading-tight mb-1">{event.name}</p>
      <p className="text-[9px] opacity-75">{event.country} · {event.date?.slice(0, 10)}</p>
      {event.affected > 0 && (
        <p className="text-[9px] mt-0.5 font-semibold">
          👥 {event.affected.toLocaleString()} affected
        </p>
      )}
    </div>
  );
}

export default function DisasterFeed() {
  const [indiaEvents, setIndiaEvents] = useState([]);
  const [southAsiaEvents, setSouthAsiaEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDisasters = async () => {
      try {
        const res = await axios.get(`${API_BASE}/live/disasters`);
        setIndiaEvents(res.data.india_events || []);
        setSouthAsiaEvents(res.data.south_asia_events || []);
      } catch (err) {
        console.warn('[DisasterFeed] Failed to fetch disasters:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDisasters();
    const interval = setInterval(fetchDisasters, 60000); // refresh every minute
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-900 border border-gray-800 rounded-lg">
        <p className="text-[10px] text-gray-500 uppercase tracking-wider animate-pulse">Loading disasters...</p>
      </div>
    );
  }

  const hasIndia = indiaEvents.length > 0;
  const hasSouthAsia = southAsiaEvents.length > 0;

  return (
    <div className="w-full h-full flex flex-col bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
      <div className="px-3 py-2 bg-gray-950/80 border-b border-gray-800 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
        <h2 className="text-gray-100 font-extrabold text-[10px] tracking-wider uppercase">
          GDACS Disaster Feed
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-3">
        {/* India section */}
        {hasIndia ? (
          <div>
            <p className="text-[8px] font-black text-red-400 uppercase tracking-widest mb-1.5 px-1">
              🇮🇳 India Active Disasters
            </p>
            <div className="space-y-1.5">
              {indiaEvents.map((ev) => (
                <DisasterCard key={ev.id} event={ev} variant="india" />
              ))}
            </div>
          </div>
        ) : (
          <p className="text-[9px] text-gray-600 italic px-1">No active India disasters</p>
        )}

        {/* South Asia (neighbouring countries) section */}
        {hasSouthAsia ? (
          <div>
            <p className="text-[8px] font-black text-purple-400 uppercase tracking-widest mb-1.5 px-1">
              🌏 South Asia (Neighbouring Countries)
            </p>
            <div className="space-y-1.5">
              {southAsiaEvents.map((ev) => (
                <DisasterCard key={ev.id} event={ev} variant="south-asia" />
              ))}
            </div>
          </div>
        ) : (
          <p className="text-[9px] text-gray-600 italic px-1">No active South Asia disasters</p>
        )}

        {!hasIndia && !hasSouthAsia && (
          <p className="text-[9px] text-gray-600 italic text-center mt-2">
            No active GDACS disasters in this region
          </p>
        )}
      </div>
    </div>
  );
}