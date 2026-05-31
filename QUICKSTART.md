# 🚀 HelpLink Quick Start Guide

## 30-Second Startup

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Then open browser:
http://localhost:5173
```

## 2-Minute Presentation

1. **Load dashboard** → Show glowing map with real satellite + tower layers
2. **Click SOS beacon** → Show AI Decision Breakdown (language, keywords, priority score)
3. **Start interactive demo** → Watch auto-dispatch (click button in bottom-right)
4. **Show API docs** → Visit http://localhost:8000/docs

## Docker One-Liner (Production Testing)

```bash
docker-compose up --build
# Frontend: http://localhost
# Backend: http://localhost:8000
```

## Real Data Status

Check data sources status:
```bash
curl http://localhost:8000/api/live/data-status
```

Response: `{"satellite": "real", "towers": "real", "tweets": "ready", "gdacs": "live"}`

## Deploy to Cloud (5 minutes)

### Railway Backend
```bash
npm install -g @railway/cli
railway login
railway init --name helplink
railway up --service backend
railway domain --service backend    # Get URL
railway variables set COPERNICUS_USER=... COPERNICUS_PASS=... etc
```

### Vercel Frontend
```bash
cd frontend
echo "VITE_API_URL=https://YOUR_RAILWAY_URL" > .env.production
npm run build
vercel --prod
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Backend won't start | Check Python 3.10+: `python --version` |
| Frontend build fails | `rm -rf node_modules && npm ci` |
| WebSocket disconnects | Verify `/ws` endpoint accessible |
| Real data shows "SIMULATED" | Check API credentials in `.env` |
| Docker build fails | `docker system prune` then rebuild |

## Documentation Files

- **README.md** - Project overview + tech stack
- **DEPLOYMENT.md** - Step-by-step cloud deployment
- **PRESENTATION_GUIDE.md** - Samsung judges demo script
- **PHASE3_SUMMARY.md** - What was completed in Phase 3

## Key Endpoints

```
GET  /api/live/disasters           # GDACS live events
GET  /api/live/data-status         # Real vs simulated badge status
GET  /api/map/satellite-zones      # Sentinel-1 SAR zones
GET  /api/map/cellular-anomalies   # OpenCelliD tower anomalies
GET  /api/sos/feed                 # NLP-processed distress signals
POST /api/teams/{id}/dispatch      # Dispatch rescue team
WS   /ws                           # Real-time WebSocket updates
```

## GitHub Repository

```bash
git remote add origin https://github.com/prottus2004/helplink.git
git branch -M main
git push -u origin main
```

## Version Info

- **Backend:** FastAPI 0.111.0 on Python 3.11+
- **Frontend:** React 18 with Vite, Node.js 18+
- **Containerization:** Docker + docker-compose
- **Deployment:** Railway + Vercel (free tiers)

---

**For detailed docs, see README.md**  
**For Samsung presentation, see PRESENTATION_GUIDE.md**  
**For deployment steps, see DEPLOYMENT.md**
