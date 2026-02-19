# ============================================================================
# embedding_service.py — Text Embedding Service using HuggingFace Inference API
# Converts text into 768-dimensional vectors using PubMedBERT for medical-domain
# semantic similarity. These embeddings power the vector search in Supabase pgvector.
# Source: https://huggingface.co/docs/api-inference/index
# Source: https://huggingface.co/NeuML/pubmedbert-base-embeddings
# ============================================================================

import httpx  # Async HTTP client for calling HuggingFace API — Source: https://www.python-httpx.org/
from typing import List, Optional  # Type hints — Source: https://docs.python.org/3/library/typing.html
from config import settings  # Centralized configuration — Source: ./config.py


# HuggingFace Inference API endpoint for feature extraction (embeddings)
# Source: https://huggingface.co/docs/api-inference/tasks/feature-extraction
HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction"

# HTTP headers including the HuggingFace API token for authentication
# Source: https://huggingface.co/docs/api-inference/quicktour#running-inference-with-api-requests
HEADERS = {
    "Authorization": f"Bearer {settings.HF_API_TOKEN}",  # Auth header with HF token
    "Content-Type": "application/json",  # Request body is JSON
}


async def embed_text(text: str, model_id: Optional[str] = None) -> List[float]:
    """
    Generate a vector embedding for a single text string using HuggingFace Inference API.
    Returns a 768-dimensional float vector suitable for cosine similarity search.

    Args:
        text: The text to embed (a document chunk or user query)
        model_id: HuggingFace model ID to use (defaults to PubMedBERT)

    Returns:
        List of 768 floats representing the text embedding

    Source: https://huggingface.co/docs/api-inference/tasks/feature-extraction
    Source: https://huggingface.co/NeuML/pubmedbert-base-embeddings
    """
    # Use PubMedBERT by default, fall back to MiniLM if specified
    # Source: https://huggingface.co/NeuML/pubmedbert-base-embeddings
    effective_model = model_id or settings.EMBEDDING_MODEL_ID

    # Construct the full API URL for the specific model
    # Source: https://huggingface.co/docs/api-inference/tasks/feature-extraction#api-specification
    url = f"{HF_API_URL}/{effective_model}"

    # Truncate very long texts to avoid API limits (max ~512 tokens for BERT models)
    # Source: https://huggingface.co/NeuML/pubmedbert-base-embeddings (max_seq_length: 512)
    truncated_text = text[:2000]  # Rough character limit (BERT tokenizer ~4 chars/token)

    # Make the async HTTP request to HuggingFace Inference API
    # Source: https://www.python-httpx.org/async/
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Send the text to the embedding model
            # Source: https://huggingface.co/docs/api-inference/tasks/feature-extraction#using-the-api
            response = await client.post(
                url,  # Full model endpoint URL
                headers=HEADERS,  # Auth + content type headers
                json={"inputs": truncated_text, "options": {"wait_for_model": True}},  # Request body with wait flag for cold starts
            )
            # Raise an exception if the HTTP status code indicates an error
            # Source: https://www.python-httpx.org/exceptions/
            response.raise_for_status()

            # Parse the response — HF API returns nested list of embeddings
            # Source: https://huggingface.co/docs/api-inference/tasks/feature-extraction#output
            embedding = response.json()

            # Handle different response formats from HuggingFace API
            # Some models return [[vector]], others return [vector]
            # Source: https://huggingface.co/docs/api-inference/tasks/feature-extraction
            if isinstance(embedding, list) and len(embedding) > 0:
                if isinstance(embedding[0], list):
                    # Model returned token-level embeddings — average them to get sentence embedding
                    # Source: https://arxiv.org/abs/1908.10084 (SBERT: mean pooling strategy)
                    import numpy as np  # NumPy for efficient array operations — Source: https://numpy.org/
                    return np.mean(embedding[0], axis=0).tolist()  # Mean pool across tokens
                return embedding  # Already a flat vector

            # If response format is unexpected, raise an error
            raise ValueError(f"Unexpected embedding response format: {type(embedding)}")

        except httpx.HTTPStatusError as e:
            # If PubMedBERT fails, try the fallback model (MiniLM)
            # Source: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
            if effective_model == settings.EMBEDDING_MODEL_ID and settings.FALLBACK_EMBEDDING_MODEL_ID:
                print(f"⚠️ Primary embedding model failed ({e.response.status_code}), trying fallback...")
                return await embed_text(text, model_id=settings.FALLBACK_EMBEDDING_MODEL_ID)
            raise  # Re-raise if fallback also fails


async def embed_batch(texts: List[str], model_id: Optional[str] = None) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in a batch.
    Processes texts sequentially to respect HuggingFace API rate limits.

    Args:
        texts: List of text strings to embed
        model_id: HuggingFace model ID to use (defaults to PubMedBERT)

    Returns:
        List of embedding vectors, one per input text

    Source: https://huggingface.co/docs/api-inference/rate-limits
    """
    embeddings = []  # Accumulator for all embedding vectors

    # Process each text individually (HF free tier has rate limits)
    # Source: https://huggingface.co/docs/api-inference/rate-limits
    for i, text in enumerate(texts):
        # Skip empty or whitespace-only texts
        if not text or not text.strip():
            embeddings.append([0.0] * 768)  # Return zero vector for empty text (768 = PubMedBERT dimension)
            continue

        # Generate embedding for this text
        embedding = await embed_text(text, model_id=model_id)
        embeddings.append(embedding)  # Add to results

        # Log progress every 50 texts for long batches
        if (i + 1) % 50 == 0:
            print(f"   Embedded {i + 1}/{len(texts)} texts...")  # Progress indicator

    return embeddings  # Return all embeddings
