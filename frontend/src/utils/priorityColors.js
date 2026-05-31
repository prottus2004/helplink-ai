export const getPriorityColors = (level) => {
  switch (level?.toUpperCase()) {
    case 'CRITICAL':
      return {
        bg: 'bg-red-950/70',
        text: 'text-red-400',
        border: 'border-red-900/50',
        hover: 'hover:bg-red-950/90',
        badge: 'bg-red-900/40 text-red-300 border-red-800',
        glow: 'shadow-[0_0_15px_rgba(239,68,68,0.3)]',
        colorCode: '#ef4444'
      };
    case 'HIGH':
      return {
        bg: 'bg-orange-950/70',
        text: 'text-orange-400',
        border: 'border-orange-900/50',
        hover: 'hover:bg-orange-950/90',
        badge: 'bg-orange-900/40 text-orange-300 border-orange-800',
        glow: 'shadow-[0_0_10px_rgba(249,115,22,0.2)]',
        colorCode: '#f97316'
      };
    case 'MEDIUM':
      return {
        bg: 'bg-yellow-950/70',
        text: 'text-yellow-400',
        border: 'border-yellow-900/50',
        hover: 'hover:bg-yellow-950/90',
        badge: 'bg-yellow-900/40 text-yellow-300 border-yellow-800',
        glow: 'shadow-[0_0_8px_rgba(234,179,8,0.15)]',
        colorCode: '#eab308'
      };
    case 'LOW':
    default:
      return {
        bg: 'bg-green-950/70',
        text: 'text-green-400',
        border: 'border-green-900/50',
        hover: 'hover:bg-green-950/90',
        badge: 'bg-green-900/40 text-green-300 border-green-800',
        glow: 'shadow-none',
        colorCode: '#22c55e'
      };
  }
};
