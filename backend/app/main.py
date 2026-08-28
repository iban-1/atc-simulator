import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.progression import router as progression_router
from app.api.scenarios import router as scenarios_router
from app.config import settings
from app.services.progression_store import load_progression
from app.simulation.session import SimulationSession
from app.websocket.handlers import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.progression = load_progression()
    app.state.session = SimulationSession(progression=app.state.progression)
    loop_task = asyncio.create_task(app.state.session.run_forever(settings.tick_interval_s))
    try:
        yield
    finally:
        loop_task.cancel()
        try:
            await loop_task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="ATC Simulator (Fictional, Educational)", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(progression_router)
app.include_router(scenarios_router)
app.include_router(ws_router)
