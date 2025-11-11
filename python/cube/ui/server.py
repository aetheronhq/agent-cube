"""FastAPI server for AgentCube Web UI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AgentCube UI API",
    description="REST API for AgentCube Web UI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

from .routes.tasks import router as tasks_router
app.include_router(tasks_router, prefix="/api")
