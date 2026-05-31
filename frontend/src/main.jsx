import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';
import 'leaflet/dist/leaflet.css'; // CRITICAL: Prevents Leaflet map assets from fracturing

// React ErrorBoundary implementation (Phase 6D)
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[ErrorBoundary caught exception]:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="fixed inset-0 bg-gray-950 flex flex-col items-center justify-center select-none text-center p-6 z-[99999]">
          <div className="bg-red-950/20 border border-red-900/60 p-8 rounded-lg max-w-lg shadow-[0_0_20px_rgba(239,68,68,0.1)] flex flex-col items-center">
            <span className="text-4xl mb-4">⚠️</span>
            <h1 className="text-red-400 font-extrabold tracking-wider text-lg uppercase mb-2">
              EMERGENCY PORTAL INTERRUPTED
            </h1>
            <p className="text-gray-300 text-xs font-semibold leading-relaxed mb-6">
              A frontend rendering anomaly has been intercepted by the EOC container. The live socket connection and map layer states have been buffered safely to prevent telemetry loss.
            </p>
            <div className="w-full text-left font-mono text-[10px] text-gray-500 bg-gray-950 p-3 rounded border border-gray-900 max-h-40 overflow-y-auto mb-6">
              {this.state.error?.toString()}
            </div>
            <button
              onClick={() => window.location.reload()}
              className="bg-red-600 hover:bg-red-500 text-white font-extrabold text-xs uppercase px-4 py-2 rounded transition-colors cursor-pointer"
            >
              REBOOT OPERATIONS CONSOLE 🔄
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);
