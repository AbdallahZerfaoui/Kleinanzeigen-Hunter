"""Main application for the application service API."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import applications
from utils.database import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup: Initialize database
    init_database()
    yield
    # Shutdown: cleanup if needed


# Create FastAPI application
app = FastAPI(
    title="Kleinanzeigen Application Service API",
    description="AI-powered rental application generation service",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(applications.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Kleinanzeigen Application Service API",
        "version": "1.0.0",
        "description": "Generate personalized rental applications using AI",
        "endpoints": {
            "generate": "POST /applications/generate",
            "health": "GET /applications/health",
            "docs": "GET /docs",
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "application_service_api"
    }
