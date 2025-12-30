from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json

from app.core.config import settings
from app.core.database import engine, Base
from app.routers import auth, scans, reports

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="S1C0N Security Reconnaissance Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(scans.router)
app.include_router(reports.router)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, scan_id: int):
        await websocket.accept()
        if scan_id not in self.active_connections:
            self.active_connections[scan_id] = []
        self.active_connections[scan_id].append(websocket)

    def disconnect(self, websocket: WebSocket, scan_id: int):
        if scan_id in self.active_connections:
            self.active_connections[scan_id].remove(websocket)

    async def send_update(self, scan_id: int, data: dict):
        if scan_id in self.active_connections:
            for connection in self.active_connections[scan_id]:
                await connection.send_text(json.dumps(data))

manager = ConnectionManager()

@app.get("/")
async def root():
    return {
        "message": "S1C0N API is running",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.websocket("/ws/scan/{scan_id}")
async def websocket_endpoint(websocket: WebSocket, scan_id: int):
    """WebSocket endpoint for real-time scan updates"""
    await manager.connect(websocket, scan_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, scan_id)
