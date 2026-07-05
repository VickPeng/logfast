"""
LogFast — AI Changelog Generator
Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routes import auth, changelog, webhook


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init database tables
    try:
        await init_db()
    except Exception as e:
        print(f"WARNING: DB init failed: {e}")
    yield


app = FastAPI(
    title="LogFast",
    description="AI-powered changelog generator for SaaS teams",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(changelog.router, prefix="/api", tags=["repos & changelogs"])
app.include_router(webhook.router, prefix="/api/webhook", tags=["webhook"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
