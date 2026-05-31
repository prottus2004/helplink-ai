# HelpLink Deployment Guide

## Local Docker Testing

Before deploying to the cloud, test everything locally with Docker:

```bash
# Build and run with docker-compose
docker-compose up --build

# Access the application
# Frontend: http://localhost (port 80)
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Backend Deployment to Railway

### Prerequisites
- Railway account (free tier at railway.app)
- Railway CLI installed

### Deployment Steps

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Create Railway Project:**
   ```bash
   cd helplink
   railway init --name "helplink-ai"
   ```

4. **Deploy Backend:**
   ```bash
   cd backend
   railway up --service backend
   railway domain --service backend
   ```
   Note the backend URL (looks like: `https://helplink-backend-production.up.railway.app`)

5. **Set Environment Variables on Railway:**
   ```bash
   railway variables set DEMO_MODE=true
   railway variables set COPERNICUS_USER="prottus2004@gmail.com"
   railway variables set COPERNICUS_PASS="Copernicus@2004"
   railway variables set OPENCELLID_API_KEY="pk.dd5e3caffe6831b88d5513e24bb59a53"
   railway variables set TWITTER_BEARER_TOKEN="AAAAAAAAAAAAAAAAAAAAAPiS9wEAAAAAKIBJ7hHeUXIRYvS9MTymXOPqEr4%3DcwYJukmLADEREJNpJzbYpOs6L5ekeTUWcouLj7t2udZP2p9Dob"
   ```

## Frontend Deployment to Vercel

### Prerequisites
- Vercel account (free tier at vercel.com)
- GitHub account

### Deployment Steps

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Update Frontend Environment:**
   Create `frontend/.env.production`:
   ```
   VITE_API_URL=https://YOUR_RAILWAY_BACKEND_URL
   VITE_WS_URL=wss://YOUR_RAILWAY_BACKEND_URL/ws
   ```

3. **Deploy to Vercel:**
   ```bash
   cd frontend
   npm run build
   vercel --prod
   ```
   - When prompted "Link to existing project?" → say No
   - Output directory → `dist`
   - Vercel gives you a live URL

4. **Backend CORS Configuration:**
   If you see CORS errors, update backend CORS in `backend/main.py`:
   ```python
   allow_origins=[
       "https://YOUR_VERCEL_FRONTEND_URL",
       "http://localhost:5173"
   ]
   ```

## Environment Variables Required

### Backend (.env and Railway dashboard)
```
COPERNICUS_USER=your_esa_email
COPERNICUS_PASS=your_esa_password
OPENCELLID_API_KEY=your_opencellid_key
TWITTER_BEARER_TOKEN=your_twitter_token
DEMO_MODE=true
```

### Frontend (.env.production)
```
VITE_API_URL=https://your-railway-backend-url
VITE_WS_URL=wss://your-railway-backend-url/ws
```

## Troubleshooting

### Backend won't start
- Check Docker logs: `docker-compose logs backend`
- Verify all environment variables are set
- Check Python version compatibility (3.11+)

### Frontend can't reach API
- Verify backend URL is correct in .env.production
- Check Railway backend is running: visit `/health` endpoint
- Check CORS settings in backend/main.py
- Ensure WebSocket (WSS) connection is properly configured

### Docker build fails
- Clear cache: `docker-compose down && docker system prune`
- Rebuild: `docker-compose up --build`

## Testing Production Deployment

1. Visit your Vercel URL
2. Verify splash screen and map loads
3. Check browser console for errors
4. Test WebSocket connection (should see live updates)
5. Verify all data sources show as "REAL" in layer config
6. Try dispatching a rescue team
7. Check API Docs at: `https://your-railway-url/docs`
