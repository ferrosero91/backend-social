import os
import sys
import django
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Bootstrap Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruiting_agent.settings.base')
django.setup()

from api.agent.api import api_router

app = FastAPI(
    title="Intelligent Recruiting Agent API",
    description="Backend API for intelligent interviewing agent for SMEs",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/agent")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Intelligent Recruiting Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
