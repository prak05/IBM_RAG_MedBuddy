# ============================================================================
# main.py — FastAPI Application Entry Point for MedBuddy Backend
# This is the central hub that initializes the API server, configures CORS,
# and registers all route handlers (chat, upload, ingest, health).
# Source: https://fastapi.tiangolo.com/tutorial/first-steps/
# ============================================================================

from contextlib import asynccontextmanager  # Async context manager for app lifespan events — Source: https://docs.python.org/3/library/contextlib.html
from fastapi import FastAPI  # FastAPI framework for building high-performance APIs — Source: https://fastapi.tiangolo.com/
from fastapi.middleware.cors import CORSMiddleware  # CORS middleware to allow frontend cross-origin requests — Source: https://fastapi.tiangolo.com/tutorial/cors/
from config import settings  # Import our centralized configuration — Source: ./config.py
from routers import health, chat, upload, ingest  # Import all API route modules — Source: ./routers/


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager — runs setup on startup and cleanup on shutdown.
    This is where we initialize expensive resources (DB connections, model clients).
    Source: https://fastapi.tiangolo.com/advanced/events/#lifespan
    """
    # --- Startup: Log that the server is ready ---
    print("🩺 MedBuddy Backend starting up...")  # Startup log message
    print(f"   IBM Watsonx Model: {settings.GRANITE_MODEL_ID}")  # Log which LLM model we're using
    print(f"   Embedding Model: {settings.EMBEDDING_MODEL_ID}")  # Log which embedding model we're using
    print(f"   Supabase URL: {settings.SUPABASE_URL[:30]}...")  # Log partial Supabase URL (don't leak full URL)
    yield  # Application runs here — Source: https://fastapi.tiangolo.com/advanced/events/
    # --- Shutdown: Cleanup resources ---
    print("🩺 MedBuddy Backend shutting down...")  # Shutdown log message


# Initialize the FastAPI application with metadata for auto-generated docs
# Source: https://fastapi.tiangolo.com/tutorial/metadata/
app = FastAPI(
    title="MedBuddy API",  # API title shown in Swagger docs
    description="Medical RAG Chatbot API powered by IBM Watsonx Granite + Meditron | UST Sight 3.0",  # Description for API docs
    version="2.0.0",  # Semantic version — Source: https://semver.org/
    lifespan=lifespan,  # Attach the lifespan manager for startup/shutdown events
)

# Configure CORS to allow the Next.js frontend to make API requests
# Source: https://fastapi.tiangolo.com/tutorial/cors/
# Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
app.add_middleware(
    CORSMiddleware,  # FastAPI's built-in CORS middleware
    allow_origins=["*"],  # Allow all origins in development (restrict in production) — Source: https://fastapi.tiangolo.com/tutorial/cors/#use-corsmiddleware
    allow_credentials=True,  # Allow cookies/auth headers to be sent — Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#requests_with_credentials
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all request headers (Authorization, Content-Type, etc.)
)

# Register API routers — each router handles a specific domain of endpoints
# Source: https://fastapi.tiangolo.com/tutorial/bigger-applications/#apirouter
app.include_router(health.router, prefix="/api", tags=["Health"])  # Health check endpoint at /api/health
app.include_router(chat.router, prefix="/api", tags=["Chat"])  # Chat endpoints at /api/chat and /api/chat/stream
app.include_router(upload.router, prefix="/api", tags=["Upload"])  # File upload endpoint at /api/upload
app.include_router(ingest.router, prefix="/api", tags=["Ingest"])  # PubMed ingestion endpoint at /api/ingest


# Root endpoint — returns a welcome message confirming the API is running
# Source: https://fastapi.tiangolo.com/tutorial/first-steps/#first-steps
@app.get("/")
async def root():
    """Root endpoint that confirms the MedBuddy API is operational."""
    return {
        "message": "🩺 MedBuddy API v2.0 — Powered by IBM Watsonx Granite + Meditron",  # Welcome message
        "docs": "/docs",  # Link to auto-generated Swagger UI documentation
        "health": "/api/health",  # Link to health check endpoint
    }
