"""
FastAPI Backend for AI Finance OS
"""

import os
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from config import settings
from services.database import Database
from utils.logging import setup_logging
from routes import generate, payments

# Load environment
load_dotenv()

# Setup logging
logger = setup_logging()

# Initialize database (shared instance for lifespan management)
db = Database(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Finance OS...")
    await db.connect()
    yield
    logger.info("Shutting down...")
    await db.disconnect()


app = FastAPI(
    title="AI Finance OS",
    description="AI-powered finance tools for individuals, freelancers, and small businesses",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — restrict to your domains in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO Phase 5: lock down to actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(generate.router, prefix="/api/v1", tags=["generate"])
app.include_router(payments.router, prefix="/api/v1", tags=["payments"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
