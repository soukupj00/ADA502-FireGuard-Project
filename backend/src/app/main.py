# backend/src/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from src.app.routers import risk_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources (e.g., ML models, DB connections)
    print("FireGuard API starting up...")
    await init_db()
    yield
    # Shutdown: Clean up resources
    print("FireGuard API shutting down...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="FireGuard API",
        description="Fire risk calculation service [cite: 3]",
        version="1.0.0",
        lifespan=lifespan
    )

    # Configure CORS for Frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # Vite default port
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(risk_router.router)

    return app


app = create_app()