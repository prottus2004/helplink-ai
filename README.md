# HelpLink.AI 🚨
### **AI-Powered Disaster Rescue Coordination System**
**Built for the Samsung Solve for Tomorrow 2026 Grand Finale — Category: AI Living for India**

HelpLink is a military-grade, offline-resilient emergency operations dashboard developed to solve India's monsoon flood rescue blind spot. Every monsoon, over 5,000 Indians lose their lives in severe flash floods because search-and-rescue teams (such as the NDRF and SDRF) have no dynamic, consolidated coordination system—they search blindly. 

HelpLink resolves this critical gap by fusing three AI-powered telemetry streams into a live, real-time geo-priority rescue heatmap. This console enables commanders to identify isolated survivor clusters, geolocalize multi-lingual WhatsApp distress signals, evaluate cell tower dropouts, and dispatch rescue craft to active coordinates with zero-latency synchronization.

---

## 🌟 The Three Core AI Fusion Layers

HelpLink blends three sophisticated streams into a single prioritised heatmap using geographic proximity indexing:

1. **Satellite SAR Imagery Layer (Sentinel-1):** 
   Monsoons are plagued by heavy cloud cover and storm shadows, rendering traditional optical satellites useless. Sentinel-1 Synthetic Aperture Radar (SAR) sensors pierce clouds and operate night/day. HelpLink simulates SAR backscatter intensity coefficients ($\sigma^0$) VH polarization thresholding to distinguish land from water, automatically detecting flooded river basins, water depths, and counting buildings cut off by water.
   
2. **Multilingual SOS NLP Layer:** 
   Processes incoming WhatsApp, SMS, and wireless messages written in **10 major Indian languages** (Hindi, Malayalam, Tamil, Bengali, Telugu, Marathi, Kannada, Gujarati, Punjabi, Odia). The hybrid NLP engine detects dialects, counts digits or plural contextual indicators to estimate stranded survivors, extracts local city/district coordinates across **200+ flood-prone zones**, and runs zero-shot classification via a HuggingFace multilingual transformer model.
   
3. **Cellular Anomaly Telemetry Layer:**
   Monitors base transceiver station (BTS) telemetric health in real-time. Sudden tower shut-offs ("Dead Zones") indicate regions where rising waters have flooded power generators—leaving stranded survivors silent. Abnormal congestion peaks ("Traffic Spikes") geolocate where heavy volumes of cellular packets are being pushed, highlighting survivor epicenters.

---

## 🛠️ The Tech Stack

### **Backend Operations**
- **Core Engine:** Python 3.12+ with FastAPI (Asynchronous framework)
- **Production Server:** Uvicorn (ASGI web server)
- **Database Layer:** SQLite (via async SQLAlchemy + `aiosqlite`)
- **WebSockets:** FastAPI WebSockets (Real-time operations feeds)
- **AI / Math Packages:** NumPy, Hugging Face Transformers (`bert-base-multilingual-cased`), PyTorch, and shapely
- **Task Scheduling:** APScheduler (Dynamic vector step navigation updates)
- **Data Mocking:** Faker (Indian locale generator)

### **Frontend Command Center**
- **Framework:** React 18 (Vite boilerplate for optimized bundling)
- **Styling:** TailwindCSS v3 (NASA mission-control dark theme, glassmorphism panel styles)
- **Map Container:** Leaflet.js (`react-leaflet` + `leaflet.heat` overlays)
- **Operational Metrics:** Zustand (Global reactive state management)
- **HTTP Client:** Axios (REST API integrations)

---

## 📂 Project Architecture

```text
helplink/
├── backend/
│   ├── main.py                    # FastAPI app setup, LIFESPAN tables setup, sockets mounts
│   ├── config.py                  # Port parameters, database file paths, and NLP toggles
│   ├── requirements.txt           # Python backend dependencies
│   ├── api/
│   │   ├── routes/
│   │   │   ├── sos.py             # REST routes for incoming SOS submissions, feeds, and verifications
│   │   │   ├── map_data.py        # Heatmaps, satellite zones, and cell anomalies geoJSON streams
│   │   │   ├── rescue_teams.py    # Forces trackers and coordinate allocation dispatches
│   │   │   └── alerts.py          # Dashboard operations summaries and timeline milestones
│   │   └── schemas.py             # Pydantic contract validations
│   ├── ai/
│   │   ├── nlp_engine.py          # Multilingual Indic keyword & zero-shot Transformer engine
│   │   ├── satellite_processor.py  # Sentinel-1 SAR flood shape NumPy simulator
│   │   ├── cellular_analyzer.py   # Cellular towers dead-zone telemetric monitor
│   │   └── priority_engine.py     # Core multi-sensor priority index weighted fusion engine
│   ├── db/
│   │   ├── database.py            # Async engine sessions and database tables builders
│   │   └── models.py              # Relational schemas (SOS, Teams, Satellite, Cellular, Scenarios)
│   ├── simulation/
│   │   ├── scenarios.py           # Preloaded datasets (Kerala landslide, Assam, and Bihar floods)
│   │   └── data_generator.py      # Real-time coordinate step nav & template spawners (10s intervals)
│   └── websocket/
│       └── manager.py             # Real-time WebSocket connection manager broadcasts
├── frontend/
│   ├── index.html                 # DOM mount index
│   ├── vite.config.js             # Vite configurations and port 8000 API proxies
│   ├── tailwind.config.js         # Tailwind theme expansions
│   └── src/
│       ├── main.jsx               # React bootstrap and class-based global ErrorBoundary
│       ├── App.jsx                # NASA-style 3-column split dashboard grid
│       ├── index.css              # Custom dark scrollbars, pulsing blips, and leaflet styles
│       ├── components/
│       │   ├── Map/
│       │   │   ├── RescueMap.jsx  # Central Leaflet operations map layer compiler
│       │   │   ├── HeatmapLayer.js# custom leaflet.heat bridge component
│       │   │   └── SurvivorMarker.jsx
│       │   ├── Dashboard/
│       │   │   ├── CommandHeader.jsx
│       │   │   ├── StatCard.jsx
│       │   │   ├── AlertFeed.jsx
│       │   │   └── TeamTracker.jsx
│       │   ├── SOS/
│       │   │   ├── SOSInbox.jsx   # Indic message feed and collapsible manual SOS forms
│       │   │   └── SOSCard.jsx
│       │   └── Demo/
│       │       └── ScenarioPanel.jsx
│       ├── store/
│       │   └── useHelpLinkStore.js# Zustand operational global state store
│       ├── hooks/
│       │   ├── useWebSocket.js    # Sockets connectivity hook with auto-reconnects
│       │   └── useRescueData.js   # Axios endpoint wrappers and scenario loader hooks
│       └── utils/
│           ├── priorityColors.js  # Color HSL maps for priority statuses
│           └── languageMap.js     # Flags and scripts mappings for 10 Indic languages
└── README.md
```

---

## 🚀 Setup & Local Execution Guide

### **Prerequisites**
- **Operating System:** Windows 10/11
- **Python:** Python 3.10+ (Verified on Python 3.12.10)
- **Node.js:** Node.js 18+ (Verified on Node.js v24.16.0)

### **Step 1: Backend Setup**
1. Navigate to the backend folder:
   ```powershell
   cd backend
   ```
2. Install all pinned dependencies (FastAPI, SQLAlchemy, NumPy, PyTorch, HF Transformers, etc.):
   ```powershell
   pip install -r requirements.txt
   ```
3. Start the FastAPI server using Uvicorn:
   ```powershell
   uvicorn main:app --reload --port 8000
   ```
   *Note: On boot, HelpLink will auto-create the `helplink.db` SQLite schema, hydrate it with the default Kerala landslides scenario, and launch the real-time APScheduler.*

### **Step 2: Frontend Setup**
1. Open a new terminal and navigate to the frontend folder:
   ```powershell
   cd frontend
   ```
2. Install all Node modules:
   ```powershell
   npm install
   ```
3. Start the Vite React development server:
   ```powershell
   npm run dev
   ```
4. Access the dashboard:
   - **Emergency Operations Dashboard:** `http://localhost:5173`
   - **Asynchronous Swagger API Docs:** `http://localhost:8000/docs`

---

## 🧭 Samsung Grand Finale Showcase Playbook

To demonstrate HelpLink to the panel judges, use this chronological presentation guide:

1. **The Startup WOW:**
   Load `http://localhost:5173`. A gorgeous full-screen glowing red splash screen displays, highlighting **"Samsung Solve for Tomorrow 2026 | AI Living for India"** and showing satellite array synchronization loaders before fading into the NASA-style operations dashboard.
   
2. **Explore the Layers:**
   Point out the central Map of Wayanad, Kerala. Toggle layers on/off in the top-right **Layers Config** legend to show/hide the red **Sentinel-1 SAR submerged zones**, the purple **cellular dead zones**, the red/orange **critical SOS beacons**, and the blue **heatmaps**.
   
3. **Trigger the Automated Guided Tour:**
   In the bottom-right corner, click **"START INTERACTIVE DEMO TOUR ⚡"**. The tour executes a 6-step automated coordination flow:
   - Hard-loads the Wayanad landslide scenario database.
   - Highlights SAR flood rings under cloud cover.
   - Spawns a live Malayalam distress text block ("അടിയന്തിര സഹായം ആവശ്യമാണ്...").
   - Automatically pans and zooms the map onto the target geolocated coordinates in Kalpetta Town.
   - Highlights the NLP dialect classification, survivor extraction count (8 people), and dispatches the nearest available team (**`NDRF-KL-02`**).
   - Draws a blue dotted vector routing line on the map, simulates sending a Twilio SMS confirmation back to the survivor's mobile, and completes the mission as counters increment dynamically.
   
4. **Real-time Navigation Ticks:**
   Watch as dispatched boat squads move step-by-step towards their target on the map in real-time. Upon arrival, their status transitions to `on_ground` (indicated by a swimming rescuer emoji `🏊` or military chopper `🚁`), rescues are successfully processed, and active counters update with zero-latency.
   
5. **Switch Disasters on the Fly:**
   Use the header dropdown or the bottom panel to switch to **SITE 2: ASSAM (Brahmaputra Floods)** or **SITE 3: BIHAR FLOODS**. Watch as the dashboard fades out, completely wipes the transactional database, generates new localized coordinates, and maps lowlands low-elevation river contours.
   
6. **Submit a Manual SOS:**
   In the left panel, click **"MANUAL ENTRY +"**. Type in a distress message in Hindi (e.g., *"madad karo bhaiya 4 log doob rahe hain"*), click **"SCAFFOLD GPS"** to auto-generate coordinates near the active scenario center, and click submit. The NLP engine evaluates the dialect, survivor count, and priority levels instantly.
   
7. **Download the Operations Brief:**
   Click **"EXPORT BRIEF 📥"** in the demo controller. An automated text document compiling the session metrics, active coordinates, and NDRF dispatched units downloads directly as a `.txt` file for the commanders.

---

### **Built for India, Designed to Save Lives.**
**HelpLink AI Team — Samsung Solve for Tomorrow 2026**

---

## 🌐 Phase 3: Production Deployment

### **Docker Containerization (NEW)**

HelpLink is now fully containerized for production deployment:

```bash
# Build and run locally with Docker Compose
docker-compose up --build

# Frontend: http://localhost (port 80)
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Container Configuration:**
- ✅ Backend: Python 3.11-slim, optimized FastAPI production server
- ✅ Frontend: Multi-stage build (Node.js for build, Nginx Alpine for serve)
- ✅ Health checks: Automated monitoring on both services
- ✅ Volume mounts: Persistent data cache for satellite/tower APIs
- ✅ Environment variables: All credentials injected at runtime

See [DEPLOYMENT.md](./DEPLOYMENT.md) for full Railway + Vercel cloud deployment instructions.

### **Real Data Sources Integration**

HelpLink now pulls from **4 major free/open disaster data providers**:

| Source | Type | Status Badge | Graceful Fallback |
|--------|------|--------------|-------------------|
| **ESA Copernicus Sentinel-1** | Satellite SAR Imaging | 🟢 REAL | Simulated zones if API fails |
| **OpenCelliD Global DB** | Cell Tower Locations | 🟢 REAL | Simulated anomalies if API fails |
| **GDACS** | Global Disaster Alerts | 🟢 REAL | No fallback (critical data) |
| **Twitter/X API** | Social Media SOS Signals | 🟢 REAL | Simulated if tweets unavailable |

**Status Display:**
All data sources display real-time status badges in the RescueMap layer configuration panel. Users instantly see which data is live vs. simulated.

### **AI Explainability Panel**

Every SOS marker now displays an **AI Decision Breakdown** showing:
- 🎯 **Language Detection**: Shows detected language with confidence percentage
- 📝 **Keywords Matched**: Displays which SOS keywords were found in the message
- 👥 **Survivors Estimated**: Shows how many people extraction counted from natural language
- 📊 **Priority Score Components**: Visual breakdown of:
  - 40% SOS signal density contribution
  - 35% Satellite severity contribution  
  - 25% Cellular coverage overlap contribution
- 🔗 **Data Source Attribution**: Which system provided this signal (NLP Engine v1.0, Twitter, etc.)

This ensures Samsung judges understand **exactly why each rescue is prioritized**—a key competitive advantage for explainable AI in government procurement.

### **Environment Variables Required**

**For Local Development & Docker:**
```bash
COPERNICUS_USER=your_esa_email
COPERNICUS_PASS=your_esa_password  
OPENCELLID_API_KEY=your_api_key
TWITTER_BEARER_TOKEN=your_bearer_token
DEMO_MODE=true
```

**Note:** All credentials are stored in `.env` file which is `.gitignore`'d for security.

---

### **Built for India, Designed to Save Lives.**
**HelpLink AI Team — Samsung Solve for Tomorrow 2026**
