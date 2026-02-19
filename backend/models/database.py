# ============================================================================
# database.py — Supabase Client Initialization for MedBuddy
# Creates and exports a Supabase client instance used by all services
# to interact with PostgreSQL (pgvector), Auth, and Storage.
# Source: https://supabase.com/docs/reference/python/introduction
# Source: https://github.com/supabase/supabase-py
# ============================================================================

from supabase import create_client, Client  # Supabase Python SDK — Source: https://supabase.com/docs/reference/python/initializing
from typing import Optional  # Type hints — Source: https://docs.python.org/3/library/typing.html
from config import settings  # Import our centralized settings — Source: ./config.py


def get_supabase_client() -> Optional[Client]:
    """
    Creates and returns a Supabase client using the service role key.
    The service role key bypasses Row Level Security (RLS) for server-side operations.
    In production, use the anon key for client-side and service key for server-side only.
    Returns None if credentials are not configured (allows app to start without Supabase).
    Source: https://supabase.com/docs/guides/api/api-keys#the-service_role-key
    """
    # Validate that required Supabase credentials are present
    # Source: https://supabase.com/docs/guides/getting-started/quickstarts/python
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        print(
            "⚠️ SUPABASE_URL and SUPABASE_SERVICE_KEY not set in .env file. "  # Warning for missing credentials
            "Get these from: https://supabase.com/dashboard/project/_/settings/api"  # Direct link to Supabase dashboard
        )
        return None  # Return None instead of crashing — allows app to start for development

    try:
        # Create the Supabase client with project URL and service role key
        # Source: https://supabase.com/docs/reference/python/initializing
        client: Client = create_client(
            settings.SUPABASE_URL,  # Your Supabase project URL (e.g., https://xxxx.supabase.co)
            settings.SUPABASE_SERVICE_KEY,  # Service role key for full database access
        )
        return client  # Return the initialized client for use in services
    except Exception as e:
        print(f"⚠️ Failed to initialize Supabase client: {e}")  # Log the error
        return None  # Return None on failure


# Create a module-level Supabase client instance (singleton pattern)
# This avoids creating a new connection on every request
# Source: https://supabase.com/docs/reference/python/initializing
supabase: Optional[Client] = get_supabase_client()
