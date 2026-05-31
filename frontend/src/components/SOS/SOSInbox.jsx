import React, { useState } from 'react';
import { useHelpLinkStore } from '../../store/useHelpLinkStore';
import { useRescueData } from '../../hooks/useRescueData';
import { languageMap } from '../../utils/languageMap';
import SOSCard from './SOSCard';

export default function SOSInbox() {
  const { sosSignals, activeScenario } = useHelpLinkStore();
  const { submitManualSOS } = useRescueData();

  // Filters State
  const [filterLang, setFilterLang] = useState('ALL');
  const [filterPriority, setFilterPriority] = useState('ALL');
  const [filterVerified, setFilterVerified] = useState('ALL');

  // Manual SOS Form State
  const [showManualForm, setShowManualForm] = useState(false);
  const [manualMessage, setManualMessage] = useState('');
  const [manualLang, setManualLang] = useState('');
  const [manualLat, setManualLat] = useState('');
  const [manualLng, setManualLng] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Auto-generate coordinates near the active scenario center
  const fillMockCoordinates = () => {
    let lat = 11.6854;
    let lng = 76.1320; // Wayanad default
    
    if (activeScenario?.id === 'assam') {
      lat = 26.2006;
      lng = 92.9376;
    } else if (activeScenario?.id === 'bihar') {
      lat = 26.1197;
      lng = 85.5160;
    }

    // Add tiny randomized offsets
    const latOffset = (Math.random() - 0.5) * 0.05;
    const lngOffset = (Math.random() - 0.5) * 0.05;

    setManualLat((lat + latOffset).toFixed(6));
    setManualLng((lng + lngOffset).toFixed(6));
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault();
    if (!manualMessage || !manualLat || !manualLng) {
      alert('Please populate the message and both coordinate fields.');
      return;
    }

    setSubmitting(true);
    try {
      await submitManualSOS(
        manualMessage,
        parseFloat(manualLat),
        parseFloat(manualLng),
        manualLang || null
      );
      // Reset form on success
      setManualMessage('');
      setManualLat('');
      setManualLng('');
      setManualLang('');
      setShowManualForm(false);
    } catch (err) {
      alert(`Manual submission failed: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  // Filter Logic
  const filteredSignals = sosSignals.filter((sig) => {
    const matchLang = filterLang === 'ALL' || sig.language_detected === filterLang;
    const matchPriority = filterPriority === 'ALL' || sig.priority_level === filterPriority;
    
    let matchVerified = true;
    if (filterVerified === 'VERIFIED') matchVerified = sig.is_verified === true;
    else if (filterVerified === 'UNVERIFIED') matchVerified = sig.is_verified === false;

    return matchLang && matchPriority && matchVerified;
  });

  return (
    <div className="w-full h-full flex flex-col bg-gray-900 border border-gray-800 rounded-lg overflow-hidden glass-panel select-none">
      
      {/* Title Header */}
      <div className="px-4 py-3 bg-gray-950/80 border-b border-gray-800 flex items-center justify-between">
        <h2 className="text-gray-100 font-extrabold text-xs tracking-wider uppercase">
          🚨 CLASSIFIED SOS QUEUE
        </h2>
        <button
          onClick={() => {
            setShowManualForm(!showManualForm);
            if (!showManualForm && !manualLat) fillMockCoordinates();
          }}
          className="bg-red-600 hover:bg-red-500 text-white font-extrabold text-[9px] uppercase tracking-wider px-2 py-1 rounded cursor-pointer transition-colors"
        >
          {showManualForm ? 'CLOSE FORM' : 'MANUAL ENTRY +'}
        </button>
      </div>

      {/* Collapsible Manual Submission Form Panel */}
      {showManualForm && (
        <form onSubmit={handleManualSubmit} className="p-3 bg-gray-950/95 border-b border-gray-800 flex flex-col gap-2.5 animate-fade-in select-none">
          <h3 className="text-amber-400 font-bold text-[10px] tracking-wider uppercase">SUBMIT MANUAL COORDINATE DISPATCH</h3>
          
          <div>
            <label className="text-[9px] text-gray-500 uppercase tracking-widest font-black block mb-1">RAW SOS DISTRESS MESSAGE:</label>
            <textarea
              value={manualMessage}
              onChange={(e) => setManualMessage(e.target.value)}
              placeholder="Enter WhatsApp or wireless dispatch message here..."
              rows={2}
              className="w-full text-xs bg-gray-900 border border-gray-800 rounded p-2 text-gray-100 placeholder-gray-600 focus:outline-none focus:border-red-600 resize-none font-semibold"
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-[9px] text-gray-500 uppercase tracking-widest font-black block mb-1">DETECTED LANGUAGE (OPTIONAL):</label>
              <select
                value={manualLang}
                onChange={(e) => setManualLang(e.target.value)}
                className="w-full text-[11px] bg-gray-900 border border-gray-800 rounded p-1.5 text-gray-300 focus:outline-none focus:border-red-600 cursor-pointer"
              >
                <option value="">-- AUTO NLP --</option>
                {Object.keys(languageMap).map((l) => (
                  <option key={l} value={l}>{languageMap[l].flag} {l}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-[9px] text-gray-500 uppercase tracking-widest font-black block mb-1">COORDINATES AUTOFILL:</label>
              <button
                type="button"
                onClick={fillMockCoordinates}
                className="w-full text-[10px] font-bold bg-gray-800 hover:bg-gray-700 text-gray-300 rounded py-1.5 border border-gray-700 cursor-pointer"
              >
                📍 SCAFFOLD GPS
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-[9px] text-gray-500 uppercase tracking-widest font-black block mb-1">LATITUDE:</label>
              <input
                type="number"
                step="0.000001"
                value={manualLat}
                onChange={(e) => setManualLat(e.target.value)}
                placeholder="e.g. 11.6854"
                className="w-full text-xs bg-gray-900 border border-gray-800 rounded p-1.5 text-gray-200 focus:outline-none focus:border-red-600 font-mono"
              />
            </div>
            <div>
              <label className="text-[9px] text-gray-500 uppercase tracking-widest font-black block mb-1">LONGITUDE:</label>
              <input
                type="number"
                step="0.000001"
                value={manualLng}
                onChange={(e) => setManualLng(e.target.value)}
                placeholder="e.g. 76.1320"
                className="w-full text-xs bg-gray-900 border border-gray-800 rounded p-1.5 text-gray-200 focus:outline-none focus:border-red-600 font-mono"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-extrabold text-xs uppercase py-1.5 rounded disabled:opacity-50 cursor-pointer transition-colors"
          >
            {submitting ? 'CLASSIFYING SIGNALS...' : 'SUBMIT MANUAL SOS'}
          </button>
        </form>
      )}

      {/* Dynamic Filter Section */}
      <div className="p-3 bg-gray-950/40 border-b border-gray-800/80 flex flex-col gap-2 select-none">
        
        {/* Dropdown Filters */}
        <div className="grid grid-cols-3 gap-2">
          
          {/* Priority filter */}
          <div>
            <label className="text-[8px] text-gray-500 uppercase font-black tracking-widest block mb-0.5">PRIORITY</label>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="w-full text-[10px] bg-gray-950 border border-gray-800 rounded p-1 text-gray-300 focus:outline-none focus:border-blue-700 cursor-pointer"
            >
              <option value="ALL">ALL PRIORITY</option>
              <option value="CRITICAL">🔴 CRITICAL</option>
              <option value="HIGH">🟠 HIGH</option>
              <option value="MEDIUM">🟡 MEDIUM</option>
              <option value="LOW">🟢 LOW</option>
            </select>
          </div>

          {/* Language filter */}
          <div>
            <label className="text-[8px] text-gray-500 uppercase font-black tracking-widest block mb-0.5">LANGUAGE</label>
            <select
              value={filterLang}
              onChange={(e) => setFilterLang(e.target.value)}
              className="w-full text-[10px] bg-gray-950 border border-gray-800 rounded p-1 text-gray-300 focus:outline-none focus:border-blue-700 cursor-pointer"
            >
              <option value="ALL">ALL INDIC</option>
              {Object.keys(languageMap).map((l) => (
                <option key={`opt-${l}`} value={l}>
                  {languageMap[l].flag} {l}
                </option>
              ))}
            </select>
          </div>

          {/* Verification filter */}
          <div>
            <label className="text-[8px] text-gray-500 uppercase font-black tracking-widest block mb-0.5">VERIFY STATE</label>
            <select
              value={filterVerified}
              onChange={(e) => setFilterVerified(e.target.value)}
              className="w-full text-[10px] bg-gray-950 border border-gray-800 rounded p-1 text-gray-300 focus:outline-none focus:border-blue-700 cursor-pointer"
            >
              <option value="ALL">ALL RECORDS</option>
              <option value="VERIFIED">✓ VERIFIED ONLY</option>
              <option value="UNVERIFIED">✗ UNVERIFIED</option>
            </select>
          </div>

        </div>

      </div>

      {/* Cards list */}
      <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-3">
        {filteredSignals.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-gray-500 text-center py-16 px-4">
            <span className="text-3xl mb-1.5">📂</span>
            <p className="text-xs font-bold uppercase tracking-wider">NO INCIDENTS DETECTED</p>
            <p className="text-[10px] text-gray-600 mt-1">Adjust filters or load a different scenario.</p>
          </div>
        ) : (
          filteredSignals.map((sig) => (
            <SOSCard key={`sig-card-${sig.id}`} signal={sig} />
          ))
        )}
      </div>

      {/* Total indicators */}
      <div className="px-4 py-2 border-t border-gray-800 bg-gray-950/80 text-[10px] text-gray-500 flex justify-between font-semibold">
        <span>TOTAL INCOMING: {sosSignals.length}</span>
        <span>FILTERED INCIDENTS: {filteredSignals.length}</span>
      </div>

    </div>
  );
}
