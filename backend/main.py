from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db, create_all_tables, async_session
from simulation.scenarios import load_scenario
from simulation.data_generator import simulate_realtime_update
from websocket.manager import manager
from api.routes import sos, map_data, rescue_teams, alerts
from api.routes.live_data import router as live_data_router
from config import APP_HOST, APP_PORT, DEMO_MODE, WEBSOCKET_REFRESH_INTERVAL

# Initialize background scheduler for real-time simulated updates
scheduler = AsyncIOScheduler()

async def tick_simulation_job():
    """Wrapper to run real-time updates inside an active DB transaction"""
    async with async_session() as db_session:
        try:
            await simulate_realtime_update(db_session)
        except Exception as e:
            print(f"[Main Scheduler ERROR] Job execution failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Start-up: Create all tables asynchronously
    print("[FastAPI Startup] Bootstrapping SQLite database schema...")
    await create_all_tables()
    
    # 2. Load active scenario (default: Wayanad Kerala Landslides)
    if DEMO_MODE:
        async with async_session() as db_session:
            try:
                print("[FastAPI Startup] Pre-loading default scenario 'wayanad'...")
                await load_scenario("wayanad", db_session)
            except Exception as e:
                print(f"[FastAPI Startup ERROR] Failed to load wayanad scenario: {e}")
                
    # 3. Initialize scheduler background tasks
    print(f"[FastAPI Startup] Starting background simulation ticks (Interval: {WEBSOCKET_REFRESH_INTERVAL}s)...")
    scheduler.add_job(tick_simulation_job, 'interval', seconds=WEBSOCKET_REFRESH_INTERVAL)
    scheduler.start()
    
    yield
    
    # 4. Shutdown: Clean up background threads
    print("[FastAPI Shutdown] Stopping background simulation scheduler...")
    scheduler.shutdown()

app = FastAPI(
    title="HelpLink API Portal",
    description="AI disaster rescue coordination portal developed for Samsung Solve for Tomorrow 2026.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware mapping
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local dev and presentations
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST controllers
app.include_router(sos.router, prefix="/api/sos", tags=["SOS Signals"])
app.include_router(map_data.router, prefix="/api/map", tags=["Map Coordinates & GeoJSON"])
app.include_router(rescue_teams.router, prefix="/api/teams", tags=["Search & Rescue Units"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Operations Operations Feed"])
app.include_router(live_data_router, tags=["Live Disaster Feeds"])

# Direct load scenario controller for simulation control panels
@app.post("/api/demo/load-scenario/{scenario_id}")
async def api_load_scenario(scenario_id: str, db: AsyncSession = Depends(get_db)):
    """
    Triggers scenario switching on the fly.
    Clears all logs and loads either Kerala landslide, Assam, or Bihar floods.
    """
    try:
        scenario = await load_scenario(scenario_id, db)
        
        # Broadcast switch notification to all sockets
        ws_event = {
            "type": "scenario_loaded",
            "data": {
                "id": scenario.id,
                "scenario_name": scenario.scenario_name,
                "location": scenario.location,
                "description": scenario.description,
                "severity": scenario.severity,
                "total_affected": scenario.total_affected
            }
        }
        await manager.broadcast(ws_event)
        
        return {
            "status": "success",
            "message": f"Scenario '{scenario.scenario_name}' loaded successfully.",
            "scenario": {
                "id": scenario.id,
                "name": scenario.scenario_name
            }
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Scenario swap execution failed: {str(e)}"
        )

# WebSocket connection route
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Maintain connection, handle keep-alive pings
            data = await websocket.receive_text()
            # If clients send message triggers, we can handle them here
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"[WebSocket ERROR] Connection broken by exception: {e}")
        manager.disconnect(websocket)

# Health verification endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "demo_mode": DEMO_MODE,
        "active_scheduler": scheduler.running
    }

# Mount static build folder of React if exists
dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(dist_path):
    print(f"[FastAPI Static] Mounting production client distribution from {dist_path}...")
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")
