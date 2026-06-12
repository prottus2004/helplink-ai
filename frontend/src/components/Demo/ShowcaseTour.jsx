import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const TOUR_STEPS = [
  {
    step: 1,
    title: "Loading Wayanad Disaster Scenario",
    description: "Loading July 2024 Wayanad flash flood data — satellite zones, SOS signals, and rescue teams",
    action: async () => {
      await axios.post(`${API_BASE}/api/demo/load-scenario/wayanad`);
    },
    duration: 3000,
    highlight: "map"
  },
  {
    step: 2,
    title: "Satellite SAR Analysis",
    description: "ESA Sentinel-1 SAR imagery has identified 3 inundation zones in Wayanad. Flood severity: 92% in Meppadi, 78% in Vythiri.",
    action: null,
    duration: 4000,
    highlight: "satellite"
  },
  {
    step: 3,
    title: "AI Processing 8 SOS Signals",
    description: "NLP engine classified distress messages in Malayalam, Hindi, Tamil, Kannada, and English. 48 survivors estimated across 3 critical hotspots.",
    action: null,
    duration: 4000,
    highlight: "sos"
  },
  {
    step: 4,
    title: "Priority Engine Calculating",
    description: "Fusing satellite severity (35%) + SOS density (40%) + cellular dead zones (25%). Meppadi zone scores 92/100 — CRITICAL.",
    action: null,
    duration: 4000,
    highlight: "priority"
  },
  {
    step: 5,
    title: "Dispatching NDRF-KL-01 to Meppadi",
    description: "Nearest available NDRF team automatically routed to highest-priority survivor cluster. ETA: 12 minutes.",
    action: null,
    duration: 4000,
    highlight: "dispatch"
  },
  {
    step: 6,
    title: "System Operational",
    description: "4 rescue teams deployed. 3 critical hotspots covered. Real-time updates every 15 minutes via Sentinel-1. System fully operational.",
    action: null,
    duration: 5000,
    highlight: "complete"
  },
];

export default function ShowcaseTour({ onClose }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [completed, setCompleted] = useState(false);

  const runTour = useCallback(async () => {
    setIsRunning(true);
    setCurrentStep(0);
    setCompleted(false);

    for (let i = 0; i < TOUR_STEPS.length; i++) {
      setCurrentStep(i);
      const step = TOUR_STEPS[i];

      if (step.action) {
        try { await step.action(); } catch (e) { console.error(e); }
      }

      await new Promise(resolve => setTimeout(resolve, step.duration));
    }

    setCompleted(true);
    setIsRunning(false);
  }, []);

  const step = TOUR_STEPS[currentStep] || TOUR_STEPS[0];

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(4, 13, 26, 0.92)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 9999, fontFamily: 'sans-serif'
    }}>
      <div style={{
        background: '#0b1628', border: '1px solid rgba(29,114,245,0.3)',
        borderRadius: 16, padding: '32px 36px', maxWidth: 520, width: '90%',
        textAlign: 'center'
      }}>
        {/* Header */}
        <div style={{ marginBottom: 24 }}>
          <div style={{
            display: 'inline-block',
            background: 'rgba(29,114,245,0.12)',
            border: '1px solid rgba(29,114,245,0.3)',
            borderRadius: 4, padding: '3px 12px', marginBottom: 12,
            fontSize: 11, fontWeight: 700, color: '#5fa8f5',
            letterSpacing: '0.1em', textTransform: 'uppercase'
          }}>
            Samsung Solve for Tomorrow 2026 · Live Demo
          </div>
          <h2 style={{ color: '#eef4ff', fontSize: 22, margin: '0 0 6px', fontWeight: 700 }}>
            HelpLink AI Guided Demo Tour
          </h2>
          <p style={{ color: '#7788aa', fontSize: 13, margin: 0 }}>
            Watch the full disaster rescue coordination system in action
          </p>
        </div>

        {/* Step indicator */}
        {!completed && (
          <div style={{ display: 'flex', justifyContent: 'center', gap: 6, marginBottom: 24 }}>
            {TOUR_STEPS.map((s, i) => (
              <div key={i} style={{
                width: 28, height: 4, borderRadius: 2,
                background: i <= currentStep
                  ? '#1d72f5'
                  : 'rgba(255,255,255,0.08)',
                transition: 'background 0.3s'
              }} />
            ))}
          </div>
        )}

        {/* Content */}
        {!isRunning && !completed ? (
          <div>
            <div style={{ fontSize: 48, marginBottom: 16 }}>🗺️</div>
            <p style={{ color: '#aabbcc', fontSize: 14, lineHeight: 1.7, marginBottom: 28 }}>
              This guided tour automatically loads the Wayanad flood scenario,
              shows satellite flood zone detection, NLP classification of distress
              messages, and rescue team dispatch — in 6 steps, 24 seconds.
            </p>
            <button
              onClick={runTour}
              style={{
                background: '#1d72f5', color: 'white',
                border: 'none', borderRadius: 8,
                padding: '14px 32px', fontSize: 16,
                fontWeight: 700, cursor: 'pointer',
                marginBottom: 12, width: '100%'
              }}
            >
              ▶  START GUIDED DEMO TOUR
            </button>
            <button onClick={onClose} style={{
              background: 'none', border: '1px solid rgba(255,255,255,0.1)',
              color: '#7788aa', borderRadius: 6,
              padding: '8px 20px', fontSize: 12, cursor: 'pointer'
            }}>
              Cancel
            </button>
          </div>
        ) : completed ? (
          <div>
            <div style={{ fontSize: 48, marginBottom: 16 }}>✅</div>
            <h3 style={{ color: '#06d6a0', fontSize: 18, marginBottom: 8 }}>
              Demo Complete
            </h3>
            <p style={{ color: '#80c4aa', fontSize: 14, marginBottom: 24 }}>
              4 rescue teams deployed · 3 critical hotspots covered ·
              48 survivors located · System fully operational
            </p>
            <button onClick={onClose} style={{
              background: '#1d72f5', color: 'white',
              border: 'none', borderRadius: 8,
              padding: '12px 28px', fontSize: 14,
              fontWeight: 700, cursor: 'pointer'
            }}>
              View Live Dashboard →
            </button>
          </div>
        ) : (
          <div>
            <div style={{ fontSize: 36, marginBottom: 16 }}>
              {['🛰️','📡','🤖','⚡','🚁','✅'][currentStep] || '🔄'}
            </div>
            <div style={{
              fontSize: 11, color: '#1d72f5', textTransform: 'uppercase',
              letterSpacing: '0.1em', marginBottom: 8, fontWeight: 700
            }}>
              Step {step.step} of {TOUR_STEPS.length}
            </div>
            <h3 style={{ color: '#eef4ff', fontSize: 18, marginBottom: 10 }}>
              {step.title}
            </h3>
            <p style={{ color: '#7788aa', fontSize: 13, lineHeight: 1.7, marginBottom: 20 }}>
              {step.description}
            </p>
            <div style={{
              height: 4, background: 'rgba(255,255,255,0.08)',
              borderRadius: 2, overflow: 'hidden'
            }}>
              <div style={{
                height: '100%', background: '#1d72f5', borderRadius: 2,
                animation: `progress ${step.duration}ms linear`
              }} />
            </div>
            <style>{`@keyframes progress { from { width: 0% } to { width: 100% } }`}</style>
          </div>
        )}
      </div>
    </div>
  );
}
