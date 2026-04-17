"""Main FastAPI application entry point."""

import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pythonjsonlogger import jsonlogger

from app.config import settings
from app.core.exceptions import IncidentBriefError, ValidationError
from app.api.routes import incidents

# Configure structured logging
log_handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s',
    rename_fields={
        'asctime': 'timestamp',
        'name': 'logger',
        'levelname': 'level'
    }
)
log_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG if settings.app_debug else logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events.
    """
    # Startup
    logger.info(
        "Starting Incident Brief Generator API",
        extra={
            "app_name": settings.app_name,
            "environment": settings.app_env,
            "debug": settings.app_debug
        }
    )
    yield
    # Shutdown
    logger.info("Shutting down Incident Brief Generator API")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Generate structured incident briefs from New Relic, Splunk, and Jira data",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.app_debug else None,
    redoc_url="/api/redoc" if settings.app_debug else None,
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(incidents.router, prefix="/api/v1", tags=["incidents"])


# Global exception handlers
@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle validation errors."""
    logger.warning(f"Validation error: {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation Error",
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(IncidentBriefError)
async def incident_brief_error_handler(request: Request, exc: IncidentBriefError):
    """Handle custom incident brief errors."""
    logger.error(f"Incident brief error: {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Incident Brief Generation Failed",
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.exception(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.app_env
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "service": settings.app_name,
        "version": "0.1.0",
        "docs": "/api/docs" if settings.app_debug else "Not available in production",
        "status": "operational"
    }