import React from 'react'

export default function EmergencyReport(){
  const FORM_URL = import.meta.env.VITE_GOOGLE_FORM_URL || 'https://forms.gle/YOUR_FORM_ID_HERE'

  return (
    <div className="min-h-screen flex flex-col items-center justify-start bg-gray-950 text-gray-100 p-8">
      <div className="max-w-3xl w-full bg-gray-900 border border-gray-800 rounded-lg p-8 shadow-xl">
        <h1 className="text-2xl font-extrabold text-red-400 mb-2">🚨 EMERGENCY SOS — HELPLINK DISASTER RESPONSE</h1>
        <p className="text-sm text-gray-300 mb-4">Report an emergency using this public form. Your submission goes directly to HelpLink's AI intake and shows on the rescue dashboard.</p>

        <div className="mb-6">
          <a href={FORM_URL} target="_blank" rel="noreferrer" className="inline-block w-full text-center bg-red-600 hover:bg-red-700 text-white font-bold py-4 rounded-lg text-lg">
            🆘 SUBMIT EMERGENCY SOS NOW
          </a>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <h3 className="text-sm font-semibold text-gray-200">Instructions</h3>
            <ul className="text-xs text-gray-400 list-disc list-inside mt-2">
              <li>Fill the form in any language.</li>
              <li>Include location (village, landmark, district) where possible.</li>
              <li>Provide a contact number if available.</li>
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-gray-200">Languages</h3>
            <div className="flex flex-wrap gap-2 mt-2">
              {['हिंदी','Malayalam','தமிழ்','తెలుగు','বাংলা','English'].map((l) => (
                <span key={l} className="text-xs px-2 py-1 bg-gray-800 rounded-md">{l}</span>
              ))}
            </div>
          </div>
        </div>

        <p className="text-xs text-gray-500">Helplink AI · Powered by ESA Sentinel-1, GDACS, OpenCelliD</p>
      </div>
    </div>
  )
}
