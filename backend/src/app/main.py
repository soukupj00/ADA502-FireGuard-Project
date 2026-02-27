import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import risk_router, subscription, zones


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources (e.g., ML models, DB connections)
    print("FireGuard API starting up...")
    # No need to init_db() here as Intelligence System handles schema
    yield
    # Shutdown: Clean up resources
    print("FireGuard API shutting down...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="FireGuard API",
        description="Fire risk calculation service",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs/",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Get allowed origins from env, defaulting to development settings
    # In docker-compose, we can pass "http://<YOUR_IP>" or "*"
    origins_str = os.getenv(
        "BACKEND_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    )

    # split the string into a list
    origins = [origin.strip() for origin in origins_str.split(",")]

    # Configure CORS for Frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(risk_router.router)
    app.include_router(zones.router)
    app.include_router(subscription.router)

    return app


app = create_app()
