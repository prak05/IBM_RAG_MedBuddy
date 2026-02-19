# ============================================================================
# config.py — Centralized Configuration Loader for MedBuddy Backend
# Loads all environment variables and API credentials from .env file
# Source: https://fastapi.tiangolo.com/advanced/settings/
# Source: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
# ============================================================================

import os  # Standard library for accessing environment variables — Source: https://docs.python.org/3/library/os.html
from dotenv import load_dotenv  # Load .env file into environment — Source: https://github.com/theskumar/python-dotenv

# Load environment variables from .env file in the backend directory
# Source: https://github.com/theskumar/python-dotenv#getting-started
load_dotenv()


class Settings:
    """
    Application settings loaded from environment variables.
    All secrets (API keys, URLs, tokens) are stored in .env file and NEVER hardcoded.
    Source: https://12factor.net/config
    """

    # --- IBM Watsonx Configuration ---
    # IBM Watsonx API key for authenticating with the Granite LLM service
    # Source: https://cloud.ibm.com/apidocs/watsonx-ai#authentication
    WATSONX_API_KEY: str = os.getenv("WATSONX_API_KEY", "")

    # IBM Watsonx project ID that scopes the API requests to your project
    # Source: https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-api-getting-started.html
    WATSONX_PROJECT_ID: str = os.getenv("WATSONX_PROJECT_ID", "")

    # IBM Watsonx API endpoint URL (region-specific)
    # Source: https://cloud.ibm.com/apidocs/watsonx-ai#endpoint-urls
    WATSONX_URL: str = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

    # --- HuggingFace Configuration ---
    # HuggingFace API token for accessing Inference API (Meditron, TrOCR, PubMedBERT)
    # Source: https://huggingface.co/docs/hub/security-tokens
    HF_API_TOKEN: str = os.getenv("HF_API_TOKEN", "")

    # --- Supabase Configuration ---
    # Supabase project URL for database, auth, and storage access
    # Source: https://supabase.com/docs/guides/getting-started/quickstarts/python
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")

    # Supabase service role key (server-side, has full database access)
    # Source: https://supabase.com/docs/guides/api/api-keys
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")

    # --- Model Configuration ---
    # IBM Granite model ID — the primary LLM for answer generation
    # Source: https://huggingface.co/ibm-granite/granite-3.0-8b-instruct
    GRANITE_MODEL_ID: str = "ibm/granite-3-8b-instruct"

    # Meditron model ID on HuggingFace — the secondary medical-specialized LLM
    # Source: https://huggingface.co/epfl-llm/meditron-7b
    MEDITRON_MODEL_ID: str = "epfl-llm/meditron-7b"

    # PubMedBERT embedding model — medical-domain-specific 768-dim embeddings
    # Source: https://huggingface.co/NeuML/pubmedbert-base-embeddings
    EMBEDDING_MODEL_ID: str = "NeuML/pubmedbert-base-embeddings"

    # Fallback embedding model if PubMedBERT is unavailable
    # Source: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
    FALLBACK_EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"

    # TrOCR model for handwriting recognition from images
    # Source: https://huggingface.co/microsoft/trocr-large-handwritten
    TROCR_MODEL_ID: str = "microsoft/trocr-large-handwritten"

    # --- RAG Configuration ---
    # Maximum chunk size in characters for document splitting
    # Source: https://www.pinecone.io/learn/chunking-strategies/
    CHUNK_SIZE: int = 512

    # Overlap between adjacent chunks to preserve context across boundaries
    # Source: https://www.pinecone.io/learn/chunking-strategies/
    CHUNK_OVERLAP: int = 50

    # Number of top similar chunks to retrieve for each query
    # Source: https://arxiv.org/abs/2005.11401 (RAG paper by Lewis et al.)
    TOP_K: int = 5

    # Minimum similarity threshold for vector search results (0.0 to 1.0)
    # Source: https://supabase.com/docs/guides/ai/vector-columns
    SIMILARITY_THRESHOLD: float = 0.5

    # LLM temperature — low value for factual, grounded medical responses
    # Source: https://arxiv.org/abs/2302.13971 (temperature and hallucination)
    LLM_TEMPERATURE: float = 0.2

    # Maximum tokens the LLM can generate in a single response
    # Source: https://cloud.ibm.com/apidocs/watsonx-ai#text-generation
    MAX_NEW_TOKENS: int = 1024

    # --- NCBI PubMed API ---
    # NCBI E-utilities base URL for PubMed search and fetch
    # Source: https://www.ncbi.nlm.nih.gov/books/NBK25501/
    NCBI_BASE_URL: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    # Optional NCBI API key for higher rate limits (10 req/sec vs 3 req/sec)
    # Source: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
    NCBI_API_KEY: str = os.getenv("NCBI_API_KEY", "")

    # --- CORS Configuration ---
    # Allowed origins for cross-origin requests (frontend URL)
    # Source: https://fastapi.tiangolo.com/tutorial/cors/
    CORS_ORIGINS: list = [
        "http://localhost:3000",   # Next.js local dev server
        "https://*.vercel.app",    # Vercel deployment
    ]


# Create a singleton settings instance used across the application
# Source: https://fastapi.tiangolo.com/advanced/settings/#creating-the-settings-only-once-with-lru_cache
settings = Settings()
