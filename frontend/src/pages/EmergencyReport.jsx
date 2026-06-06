import { useState } from 'react';

export default function EmergencyReport() {
  const FORM_URL = "https://forms.gle/zESR46gaimxAKEsg9";
  const [copied, setCopied] = useState(false);

  const copyLink = () => {
    navigator.clipboard.writeText(FORM_URL);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{
      background: "#040d1a", minHeight: "100vh",
      display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      padding: "2rem", fontFamily: "sans-serif", color: "#dde8f5"
    }}>
      <div style={{ maxWidth: 560, width: "100%", textAlign: "center" }}>

        <div style={{
          background: "rgba(255,59,59,0.15)", border: "1px solid rgba(255,59,59,0.4)",
          borderRadius: 8, padding: "10px 20px", marginBottom: 24,
          fontSize: 13, fontWeight: 700, letterSpacing: "0.12em",
          color: "#ff6b6b", textTransform: "uppercase"
        }}>
          HelpLink — Emergency SOS Intake
        </div>

        <div style={{ fontSize: 40, marginBottom: 12 }}>🆘</div>
        <h1 style={{ color: "#eef4ff", fontSize: 26, marginBottom: 8, fontWeight: 700 }}>
          Report a Disaster Emergency
        </h1>
        <p style={{ color: "#7788aa", fontSize: 14, marginBottom: 28, lineHeight: 1.7 }}>
          Fill this form in ANY language. Your report goes directly to NDRF rescue
          coordinators on the HelpLink AI dashboard within 60 seconds.
        </p>

        {/* Language chips */}
        <div style={{ display: "flex", gap: 8, justifyContent: "center",
                      flexWrap: "wrap", marginBottom: 28 }}>
          {["हिंदी","Malayalam","தமிழ்","తెలుగు","বাংলা","ਪੰਜਾਬੀ","English"].map(lang => (
            <span key={lang} style={{
              background: "rgba(29,114,245,0.12)",
              color: "#5fa8f5",
              border: "1px solid rgba(29,114,245,0.25)",
              borderRadius: 99, padding: "4px 14px", fontSize: 13
            }}>{lang}</span>
          ))}
        </div>

        {/* Main CTA */}
        <a href={FORM_URL} target="_blank" rel="noreferrer" style={{
          display: "block", background: "#ff3b3b",
          color: "white", borderRadius: 10,
          padding: "18px 32px", fontSize: 18, fontWeight: 700,
          textDecoration: "none", marginBottom: 12,
          boxShadow: "0 4px 24px rgba(255,59,59,0.3)"
        }}>
          SUBMIT EMERGENCY SOS NOW
        </a>

        <button onClick={copyLink} style={{
          background: "rgba(255,255,255,0.05)",
          border: "1px solid rgba(255,255,255,0.1)",
          color: "#7788aa", borderRadius: 6,
          padding: "8px 20px", fontSize: 12,
          cursor: "pointer", marginBottom: 32
        }}>
          {copied ? "Link copied!" : "Copy form link to share"}
        </button>

        {/* Instructions */}
        <div style={{
          background: "#0b1628", border: "1px solid rgba(255,255,255,0.06)",
          borderRadius: 10, padding: "18px 20px", textAlign: "left", marginBottom: 20
        }}>
          <p style={{ color: "#a8c0e8", fontSize: 13, fontWeight: 600, marginBottom: 12 }}>
            What to write in the form:
          </p>
          {[
            ["Location", "Village name, nearest landmark, district, state"],
            ["People count", "How many people are stranded or need help"],
            ["Emergency", "Describe what happened — flood, landslide, stuck etc."],
            ["Phone", "Your number so rescue teams can call you back"],
          ].map(([label, text]) => (
            <div key={label} style={{ display: "flex", gap: 10, marginBottom: 8 }}>
              <span style={{ fontSize: 13, flexShrink: 0, color: "#5fa8f5", fontWeight: 600 }}>{label}:</span>
              <span style={{ fontSize: 13, color: "#7788aa" }}>{text}</span>
            </div>
          ))}
        </div>

        {/* Multilingual prompt */}
        <div style={{
          background: "#0b1628", border: "1px solid rgba(255,255,255,0.06)",
          borderRadius: 10, padding: "14px 20px", textAlign: "left"
        }}>
          <p style={{ color: "#5566aa", fontSize: 12, lineHeight: 1.8, margin: 0 }}>
            <strong style={{color:"#7788aa"}}>Hindi:</strong> बाढ़ में फंसे हैं? ऊपर फॉर्म भरें।<br/>
            <strong style={{color:"#7788aa"}}>Malayalam:</strong> വെള്ളപ്പൊക്കത്തിൽ കുടുങ്ങിയോ? മുകളിലെ ഫോം പൂരിപ്പിക്കൂ।<br/>
            <strong style={{color:"#7788aa"}}>Tamil:</strong> வெள்ளத்தில் சிக்கினீர்களா? மேலே உள்ள படிவத்தை பூர்த்தி செய்யுங்கள்।<br/>
            <strong style={{color:"#7788aa"}}>Telugu:</strong> వరదలో చిక్కుకున్నారా? పై ఫారమ్ పూరించండి।
          </p>
        </div>

        <p style={{ color: "#1e2a40", fontSize: 11, marginTop: 20 }}>
          HelpLink AI · Samsung Solve for Tomorrow 2026 · AI Living for India
        </p>
      </div>
    </div>
  );
}