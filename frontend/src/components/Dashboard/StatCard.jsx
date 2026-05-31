import React, { useEffect, useState } from 'react';

export default function StatCard({ value, label, icon, color, trend }) {
  const [displayValue, setDisplayValue] = useState(0);

  // Smooth counting transition effect when telemetry values fluctuate
  useEffect(() => {
    let start = 0;
    const end = parseInt(value) || 0;
    
    if (end === 0) {
      setDisplayValue(0);
      return;
    }
    
    const duration = 800; // milliseconds
    const increment = Math.ceil(end / (duration / 30));
    
    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        clearInterval(timer);
        setDisplayValue(end);
      } else {
        setDisplayValue(start);
      }
    }, 30);

    return () => clearInterval(timer);
  }, [value]);

  const getColorClasses = () => {
    switch (color) {
      case 'red':
        return {
          bg: 'bg-red-950/20 border-red-900/40 hover:border-red-500/30',
          text: 'text-red-400',
          glow: 'shadow-[0_0_15px_rgba(239,68,68,0.05)]'
        };
      case 'orange':
        return {
          bg: 'bg-orange-950/20 border-orange-900/40 hover:border-orange-500/30',
          text: 'text-orange-400',
          glow: 'shadow-[0_0_15px_rgba(249,115,22,0.05)]'
        };
      case 'cyan':
        return {
          bg: 'bg-cyan-950/20 border-cyan-900/40 hover:border-cyan-500/30',
          text: 'text-cyan-400',
          glow: 'shadow-[0_0_15px_rgba(6,182,212,0.05)]'
        };
      case 'green':
        return {
          bg: 'bg-green-950/20 border-green-900/40 hover:border-green-500/30',
          text: 'text-green-400',
          glow: 'shadow-[0_0_15px_rgba(34,197,94,0.05)]'
        };
      default:
        return {
          bg: 'bg-gray-900 border-gray-800 hover:border-gray-700',
          text: 'text-gray-100',
          glow: 'shadow-none'
        };
    }
  };

  const style = getColorClasses();

  return (
    <div className={`flex items-center justify-between p-4 rounded-lg border transition-all ${style.bg} ${style.glow} select-none`}>
      <div className="flex flex-col">
        <span className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mb-1">
          {label}
        </span>
        <div className="flex items-baseline gap-2">
          <span className={`text-2xl font-black font-mono tracking-tight ${style.text}`}>
            {displayValue.toLocaleString()}
          </span>
          {trend && (
            <span className={`text-[10px] font-bold ${trend.startsWith('↑') ? 'text-red-400 animate-pulse' : 'text-green-400'}`}>
              {trend}
            </span>
          )}
        </div>
      </div>
      <div className="text-2xl opacity-85 select-none filter drop-shadow-md">
        {icon}
      </div>
    </div>
  );
}
