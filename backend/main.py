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
from websocket.manager import manager
from api.routes import sos, map_data, rescue_teams, alerts
from api.routes.live_data import router as live_data_router
from config import APP_HOST, APP_PORT, DEMO_MODE, WEBSOCKET_REFRESH_INTERVAL, PRODUCTION_MODE
from simulation.scenarios import load_scenario, SCENARIOS

# Initialize background scheduler for real-time simulated updates
scheduler = AsyncIOScheduler()

async def tick_simulation_job():
    """Wrapper to run real-time updates inside an active DB transaction"""
    from simulation.data_generator import simulate_realtime_update
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
    # 1b. Stamp Alembic to record current migration state (stamp only — never upgrade on fresh DB)
    try:
        from alembic.config import Config as AlembicConfig
        from alembic import command as alembic_command
        cfg = AlembicConfig(os.path.join(os.path.dirname(__file__), "alembic.ini"))
        cfg.set_main_option("script_location",
                            os.path.join(os.path.dirname(__file__), "migrations"))
        alembic_command.stamp(cfg, "head")
        print("[FastAPI Startup] Alembic stamp applied")
    except Exception as e:
        print(f"[FastAPI Startup] Alembic stamp skipped: {e}")
    
    # 2. Load active scenario (default: Wayanad Kerala Landslides) only in demo mode
    if DEMO_MODE:
        from simulation.scenarios import load_scenario
        async with async_session() as db_session:
            try:
                print("[FastAPI Startup] Pre-loading default scenario 'wayanad'...")
                await load_scenario("wayanad", db_session)
            except Exception as e:
                print(f"[FastAPI Startup ERROR] Failed to load wayanad scenario: {e}")

    # 3. Initialize scheduler background tasks
    if DEMO_MODE:
        print(f"[FastAPI Startup] Starting background simulation ticks (Interval: {WEBSOCKET_REFRESH_INTERVAL}s)...")
        scheduler.add_job(tick_simulation_job, 'interval', seconds=WEBSOCKET_REFRESH_INTERVAL)
    else:
        print("[FastAPI Startup] Production mode enabled — starting real data pollers...")

        # Import real pollers lazily to avoid circular imports during startup
        try:
            from data.real_data_poller import (
                poll_twitter_sos,
                poll_gdacs_disasters,
                refresh_opencellid_towers,
                auto_satellite_check,
            )
        except Exception as e:
            print(f"[Startup] Failed to import real_data_poller: {e}")
            # Still start scheduler so other jobs (if any) can run

        async def real_twitter_poll():
            try:
                count = await poll_twitter_sos()
                if count and count > 0:
                    print(f"[RealData] Ingested {count} real SOS tweets")
            except Exception as e:
                print(f"[RealData] Twitter poll error: {e}")

        async def real_gdacs_poll():
            try:
                events = await poll_gdacs_disasters()
                if events:
                    print(f"[RealData] {len(events)} active South-Asia events from GDACS")
            except Exception as e:
                print(f"[RealData] GDACS poll error: {e}")

        # Poll every 5 minutes for tweets
        scheduler.add_job(real_twitter_poll, 'interval', minutes=5)
        # Poll GDACS every 30 minutes
        scheduler.add_job(real_gdacs_poll, 'interval', minutes=30)
        # Check satellite imagery every 6 hours
        scheduler.add_job(auto_satellite_check, 'interval', hours=6)
        # Refresh OpenCelliD towers once per day
        scheduler.add_job(refresh_opencellid_towers, 'interval', hours=24)

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
async def api_load_scenario(
    scenario_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Load a pre-built disaster scenario into the database for demo purposes"""
    try:
        result = await load_scenario(scenario_id, db)

        # Broadcast to all connected dashboards
        await manager.broadcast({
            "type": "scenario_loaded",
            "data": result
        })

        return result
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to load scenario: {e}")


@app.get("/api/demo/scenarios")
async def list_scenarios():
    """List available demo scenarios"""
    return [
        {
            "id": k,
            "name": v["scenario_name"],
            "location": v["location"],
            "severity": v["severity"],
            "total_affected": v["total_affected"],
            "center_lat": v["center_lat"],
            "center_lng": v["center_lng"],
            "zoom": v["zoom"],
        }
        for k, v in SCENARIOS.items()
    ]


@app.post("/api/demo/reset")
async def reset_scenario(db: AsyncSession = Depends(get_db)):
    """Clear all demo data and reset to blank state"""
    from sqlalchemy import text
    await db.execute(text("DELETE FROM sos_signals WHERE source = 'demo'"))
    await db.execute(text("DELETE FROM satellite_zones"))
    await db.execute(text("DELETE FROM cellular_anomalies"))
    await db.execute(text(
        "DELETE FROM rescue_teams WHERE team_code LIKE 'NDRF-%' "
        "OR team_code LIKE 'SDRF-%' OR team_code LIKE 'CG-%' "
        "OR team_code LIKE 'ARMY-%'"
    ))
    await db.commit()
    await manager.broadcast({"type": "scenario_reset"})
    return {"status": "reset", "message": "All demo data cleared"}

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
        "production_mode": PRODUCTION_MODE,
        "active_scheduler": scheduler.running
    }

# Mount static build folder of React if exists
dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(dist_path):
    print(f"[FastAPI Static] Mounting production client distribution from {dist_path}...")
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
