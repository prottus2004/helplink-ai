import React, { useEffect, useMemo, useState } from 'react';
import { useHelpLinkStore } from '../../store/useHelpLinkStore';
import { getPriorityColors } from '../../utils/priorityColors';
import { getLanguageFlag } from '../../utils/languageMap';

function formatAge(createdAt) {
  const diffMs = Date.now() - new Date(createdAt).getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  return `${Math.floor(diffMins / 60)}h ago`;
}

function formatCoords(lat, lng) {
  if (typeof lat !== 'number' || typeof lng !== 'number') return '--';
  return `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
}

export default function AlertFeed() {
  const { sosSignals, setFocusedLocation, isLive } = useHelpLinkStore();
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => setTick((prev) => prev + 1), 30000);
    return () => clearInterval(interval);
  }, []);

  const activeFeed = useMemo(() => sosSignals.slice(0, 20), [sosSignals, tick]);

  const focusSignal = (signal) => {
    setFocusedLocation([signal.latitude, signal.longitude]);
    setTimeout(() => setFocusedLocation(null), 2500);
  };

  return (
    <div className="w-full h-full flex flex-col bg-gray-900 border border-gray-800 rounded-lg overflow-hidden glass-panel select-none">
      <div className="px-4 py-3 bg-gray-950/80 border-b border-gray-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse-cyan" />
          <h2 className="text-gray-100 font-extrabold text-xs tracking-wider uppercase">
            Live Alert Feed
          </h2>
        </div>
        <span className="text-[9px] font-black tracking-wider uppercase text-amber-400">
          {isLive ? 'Live Stream' : 'Static Feed'}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {activeFeed.length === 0 ? (
          <div className="h-full flex items-center justify-center text-center text-gray-500">
            <p className="text-xs font-semibold uppercase tracking-wider">No SOS alerts yet</p>
          </div>
        ) : (
          activeFeed.map((signal) => {
            const colors = getPriorityColors(signal.priority_level);
            const preview =
              signal.raw_message?.length > 58
                ? `${signal.raw_message.slice(0, 58)}...`
                : signal.raw_message;

            return (
              <article
                key={`feed-${signal.id}`}
                className={`border rounded-md p-2.5 ${colors.border} ${colors.bg} ${colors.glow}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs">{getLanguageFlag(signal.language_detected)}</span>
                      <span className={`text-[9px] font-black px-1.5 py-0.5 rounded border ${colors.badge}`}>
                        {signal.priority_level}
                      </span>
                      <span className="text-[9px] text-gray-500 font-semibold">
                        #{signal.id}
                      </span>
                    </div>
                    <p className="text-[11px] text-gray-200 mt-1 leading-snug">{preview}</p>
                  </div>

                  <button
                    type="button"
                    onClick={() => focusSignal(signal)}
                    className="shrink-0 text-[9px] px-2 py-1 rounded border border-gray-700 text-gray-300 hover:text-white hover:bg-gray-800 cursor-pointer uppercase tracking-wide"
                  >
                    View
                  </button>
                </div>

                <div className="mt-2 text-[9px] text-gray-500 grid grid-cols-2 gap-y-1">
                  <span>Age: {formatAge(signal.created_at)}</span>
                  <span className={colors.text}>Score: {Math.round(signal.priority_score || 0)}</span>
                  <span className="col-span-2">
                    Coords: {formatCoords(signal.latitude, signal.longitude)}
                  </span>
                </div>
              </article>
            );
          })
        )}
      </div>

      <div className="px-4 py-2 border-t border-gray-800 bg-gray-950/70 text-[10px] text-gray-500 flex justify-between font-semibold">
        <span>Total Alerts: {sosSignals.length}</span>
        <span>Showing: {activeFeed.length}</span>
      </div>
    </div>
  );
}
