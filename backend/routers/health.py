# ============================================================================
# health.py — Health Check API Endpoint
# Provides a /api/health endpoint that reports the operational status of
# all backend services (Supabase, IBM Watsonx, HuggingFace).
# Essential for monitoring and deployment readiness checks.
# Source: https://microservices.io/patterns/observability/health-check-api.html
# ============================================================================

from fastapi import APIRouter  # FastAPI router for modular endpoint grouping — Source: https://fastapi.tiangolo.com/tutorial/bigger-applications/
import httpx  # Async HTTP client for testing external services — Source: https://www.python-httpx.org/
from models.schemas import HealthResponse  # Response schema — Source: ./models/schemas.py
from config import settings  # Centralized configuration — Source: ./config.py

# Create a router instance for health check endpoints
# Source: https://fastapi.tiangolo.com/tutorial/bigger-applications/#apirouter
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint that verifies connectivity to all backend services.
    Returns the status of Supabase, IBM Watsonx, and HuggingFace APIs.
    Used by deployment platforms (Render, Railway) to verify the app is running.

    Source: https://microservices.io/patterns/observability/health-check-api.html
    Source: https://fastapi.tiangolo.com/tutorial/first-steps/
    """
    # Check Supabase connectivity by attempting a simple query
    # Source: https://supabase.com/docs/reference/python/select
    supabase_status = "connected"
    try:
        from models.database import supabase  # Import Supabase client — Source: ./models/database.py
        # Try a lightweight query to verify the connection is alive
        supabase.table("documents").select("id").limit(1).execute()
    except Exception as e:
        supabase_status = f"error: {str(e)[:100]}"  # Capture error message (truncated)

    # Check IBM Watsonx API connectivity
    # Source: https://cloud.ibm.com/apidocs/watsonx-ai
    watsonx_status = "configured" if settings.WATSONX_API_KEY else "not configured"

    # Check HuggingFace Inference API connectivity
    # Source: https://huggingface.co/docs/api-inference/index
    hf_status = "configured" if settings.HF_API_TOKEN else "not configured"
    if settings.HF_API_TOKEN:
        try:
            # Ping HuggingFace API with a minimal request
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://huggingface.co/api/whoami-v2",  # Whoami endpoint to verify token — Source: https://huggingface.co/docs/hub/api
                    headers={"Authorization": f"Bearer {settings.HF_API_TOKEN}"},
                )
                if resp.status_code == 200:
                    hf_status = "connected"  # Token is valid and API is reachable
                else:
                    hf_status = f"error: HTTP {resp.status_code}"  # Token or API issue
        except Exception as e:
            hf_status = f"error: {str(e)[:100]}"  # Network or timeout error

    # Determine overall health status
    # "healthy" if all critical services are operational, "degraded" otherwise
    overall = "healthy" if "error" not in supabase_status else "degraded"

    return HealthResponse(
        status=overall,  # Overall system health
        supabase=supabase_status,  # Database connection status
        watsonx=watsonx_status,  # IBM Watsonx LLM status
        huggingface=hf_status,  # HuggingFace API status
        version="2.0.0",  # API version
    )
