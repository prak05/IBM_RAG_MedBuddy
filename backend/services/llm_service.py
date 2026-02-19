# ============================================================================
# llm_service.py — Hybrid LLM Service (IBM Watsonx Granite + Meditron)
# Provides a unified interface for generating medical answers using two LLMs:
#   1. IBM Watsonx Granite 3 8B Instruct (PRIMARY) — reliable, fast, enterprise-grade
#   2. EPFL Meditron-7B via HuggingFace Inference API (SECONDARY) — medical-specialized
# Source: https://cloud.ibm.com/apidocs/watsonx-ai#text-generation
# Source: https://huggingface.co/epfl-llm/meditron-7b
# ============================================================================

import httpx  # Async HTTP client for HuggingFace API — Source: https://www.python-httpx.org/
from typing import Optional, AsyncGenerator, List, Dict  # Type hints — Source: https://docs.python.org/3/library/typing.html
from ibm_watsonx_ai.foundation_models import ModelInference  # IBM Watsonx model client — Source: https://ibm.github.io/watsonx-ai-python-sdk/fm_model_inference.html
from ibm_watsonx_ai import Credentials  # IBM Watsonx authentication — Source: https://ibm.github.io/watsonx-ai-python-sdk/setup_cloud.html
from config import settings  # Centralized configuration — Source: ./config.py


# ========================= Medical System Prompt =========================

# Custom system prompt that instructs the LLM to act as a medical assistant
# with citation requirements and hallucination prevention guardrails.
# Source: https://arxiv.org/abs/2302.13971 (prompt engineering for factuality)
# Source: https://arxiv.org/abs/2005.11401 (RAG: retrieval-augmented generation)
MEDICAL_SYSTEM_PROMPT = """You are MedBuddy, an AI-powered medical knowledge assistant.
Your purpose is to provide accurate, evidence-based medical information grounded STRICTLY
in the provided context passages.

CRITICAL RULES:
1. ONLY answer based on the provided context. If the context doesn't contain relevant
   information, say "I don't have enough information in my knowledge base to answer this."
2. NEVER fabricate medical information, drug dosages, or treatment recommendations.
3. Always cite which passage(s) your answer is based on using [Source N] notation.
4. Include a disclaimer that this is for educational purposes and not medical advice.
5. If the question is about a life-threatening emergency, advise calling emergency services.
6. Use clear, professional medical language accessible to both clinicians and patients.

RESPONSE FORMAT:
- Start with a direct answer to the question
- Support with evidence from the context passages
- End with relevant citations [Source 1], [Source 2], etc.
- Add disclaimer: "⚕️ This information is for educational purposes only. Consult a healthcare professional for medical advice."
"""


# ========================= IBM Watsonx Granite (Primary) =========================

def _get_granite_client() -> Optional[ModelInference]:
    """
    Initialize and return the IBM Watsonx Granite model client.
    Returns None if credentials are not configured.

    Source: https://ibm.github.io/watsonx-ai-python-sdk/fm_model_inference.html
    Source: https://cloud.ibm.com/apidocs/watsonx-ai#text-generation
    """
    # Check if IBM Watsonx credentials are configured
    if not settings.WATSONX_API_KEY or not settings.WATSONX_PROJECT_ID:
        print("⚠️ IBM Watsonx credentials not configured, Granite LLM unavailable")
        return None

    try:
        # Create IBM Watsonx credentials object
        # Source: https://ibm.github.io/watsonx-ai-python-sdk/setup_cloud.html#authentication
        credentials = Credentials(
            url=settings.WATSONX_URL,  # IBM Cloud regional endpoint
            api_key=settings.WATSONX_API_KEY,  # API key for authentication
        )

        # Initialize the Granite model for inference
        # Source: https://ibm.github.io/watsonx-ai-python-sdk/fm_model_inference.html#ModelInference
        model = ModelInference(
            model_id=settings.GRANITE_MODEL_ID,  # ibm/granite-3-8b-instruct
            credentials=credentials,  # Authentication credentials
            project_id=settings.WATSONX_PROJECT_ID,  # Watsonx project scope
        )
        return model
    except Exception as e:
        print(f"⚠️ Failed to initialize Granite client: {e}")
        return None


async def generate_with_granite(prompt: str, context: str) -> Optional[str]:
    """
    Generate a medical answer using IBM Watsonx Granite 3 8B Instruct.
    This is the PRIMARY LLM — reliable, fast, and enterprise-grade.

    Args:
        prompt: The user's medical question
        context: Retrieved passages from the vector store to ground the answer

    Returns:
        The generated answer string, or None if generation fails

    Source: https://cloud.ibm.com/apidocs/watsonx-ai#text-generation
    Source: https://huggingface.co/ibm-granite/granite-3.0-8b-instruct
    """
    # Initialize the Granite model client
    model = _get_granite_client()
    if not model:
        return None  # Return None if client initialization failed

    # Construct the full prompt with system instructions, context, and question
    # Source: https://huggingface.co/ibm-granite/granite-3.0-8b-instruct#prompt-template
    full_prompt = f"""{MEDICAL_SYSTEM_PROMPT}

CONTEXT PASSAGES:
{context}

USER QUESTION: {prompt}

ANSWER:"""

    try:
        # Call IBM Watsonx API for text generation
        # Source: https://ibm.github.io/watsonx-ai-python-sdk/fm_model_inference.html#ModelInference.generate_text
        response = model.generate_text(
            prompt=full_prompt,  # The complete prompt with context
            params={
                "decoding_method": "greedy",  # Greedy decoding for deterministic output — Source: https://cloud.ibm.com/apidocs/watsonx-ai#text-generation-parameters
                "max_new_tokens": settings.MAX_NEW_TOKENS,  # Maximum response length (1024 tokens)
                "temperature": settings.LLM_TEMPERATURE,  # Low temperature (0.2) for factual responses
                "repetition_penalty": 1.1,  # Slight penalty to avoid repetitive text — Source: https://arxiv.org/abs/1909.05858
            },
        )
        return response  # Return the generated text
    except Exception as e:
        print(f"⚠️ Granite generation error: {e}")
        return None  # Return None on failure


# ========================= Meditron via HuggingFace (Secondary) =========================

async def generate_with_meditron(prompt: str, context: str) -> Optional[str]:
    """
    Generate a medical answer using EPFL Meditron-7B via HuggingFace Inference API.
    This is the SECONDARY LLM — specialized in medical domain knowledge.
    No local GPU needed — inference runs on HuggingFace's servers.

    Args:
        prompt: The user's medical question
        context: Retrieved passages from the vector store to ground the answer

    Returns:
        The generated answer string, or None if generation fails

    Source: https://huggingface.co/epfl-llm/meditron-7b
    Source: https://huggingface.co/docs/api-inference/tasks/text-generation
    """
    # Check if HuggingFace API token is configured
    if not settings.HF_API_TOKEN:
        print("⚠️ HuggingFace API token not configured, Meditron unavailable")
        return None

    # Construct the full prompt with medical context
    # Source: https://huggingface.co/epfl-llm/meditron-7b#prompt-format
    full_prompt = f"""{MEDICAL_SYSTEM_PROMPT}

CONTEXT PASSAGES:
{context}

USER QUESTION: {prompt}

ANSWER:"""

    # HuggingFace Inference API endpoint for text generation
    # Source: https://huggingface.co/docs/api-inference/tasks/text-generation
    url = f"https://api-inference.huggingface.co/models/{settings.MEDITRON_MODEL_ID}"

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            # Send the prompt to Meditron via HuggingFace API
            # Source: https://huggingface.co/docs/api-inference/tasks/text-generation#using-the-api
            response = await client.post(
                url,  # Meditron model endpoint
                headers={
                    "Authorization": f"Bearer {settings.HF_API_TOKEN}",  # HF API authentication
                    "Content-Type": "application/json",  # JSON request body
                },
                json={
                    "inputs": full_prompt,  # The complete prompt text
                    "parameters": {
                        "max_new_tokens": settings.MAX_NEW_TOKENS,  # Max response length
                        "temperature": settings.LLM_TEMPERATURE,  # Low temperature for factuality
                        "return_full_text": False,  # Only return generated text, not the prompt
                        "repetition_penalty": 1.1,  # Avoid repetitive output
                    },
                    "options": {
                        "wait_for_model": True,  # Wait if model needs to load (cold start)
                    },
                },
            )
            response.raise_for_status()  # Raise on HTTP errors

            # Parse the response — HF API returns a list of generated texts
            # Source: https://huggingface.co/docs/api-inference/tasks/text-generation#output
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            return None

        except httpx.HTTPStatusError as e:
            print(f"⚠️ Meditron API error: {e.response.status_code} — {e.response.text[:200]}")
            return None
        except Exception as e:
            print(f"⚠️ Meditron unexpected error: {e}")
            return None


# ========================= Hybrid Generation (Main Entry Point) =========================

async def generate_answer(
    question: str,
    context_chunks: List[Dict],
    model_preference: str = "granite",
) -> Dict:
    """
    Generate a medical answer using the hybrid LLM strategy.
    Routes to the preferred model, with automatic fallback on failure.

    Hybrid Strategy:
    - If model_preference is "granite": Try Granite first, fallback to Meditron
    - If model_preference is "meditron": Try Meditron first, fallback to Granite
    - If both fail: Return a graceful error message

    Args:
        question: The user's medical question
        context_chunks: Retrieved chunks from vector search (with content and metadata)
        model_preference: Which model to try first ("granite" or "meditron")

    Returns:
        Dict with 'answer', 'model_used', and 'confidence' keys

    Source: https://arxiv.org/abs/2005.11401 (RAG: Retrieval-Augmented Generation)
    """
    # Format the context chunks into a numbered list for the LLM prompt
    # Each chunk is labeled as [Source N] for citation in the response
    context_parts = []
    for i, chunk in enumerate(context_chunks, start=1):
        source_label = chunk.get("filename", chunk.get("source", "Unknown"))  # Source identification
        context_parts.append(f"[Source {i}] ({source_label}):\n{chunk['content']}")

    # Join all context passages with separator lines
    context_text = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant context found."

    # Calculate confidence based on average similarity score of retrieved chunks
    # Source: https://arxiv.org/abs/2005.11401 (retrieval quality affects generation quality)
    avg_similarity = 0.0
    if context_chunks:
        similarities = [c.get("similarity", 0.0) for c in context_chunks]
        avg_similarity = sum(similarities) / len(similarities)

    # Determine confidence level based on retrieval quality
    if avg_similarity >= 0.8:
        confidence = "high"  # Strong evidence in knowledge base
    elif avg_similarity >= 0.6:
        confidence = "medium"  # Moderate evidence
    else:
        confidence = "low"  # Weak evidence — answer may be less reliable

    # Try the preferred model first, then fallback
    answer = None
    model_used = model_preference

    if model_preference == "granite":
        # Try IBM Granite first (primary)
        answer = await generate_with_granite(question, context_text)
        if not answer:
            # Fallback to Meditron if Granite fails
            print("⚠️ Granite failed, falling back to Meditron...")
            answer = await generate_with_meditron(question, context_text)
            model_used = "meditron" if answer else "none"
    else:
        # Try Meditron first (secondary)
        answer = await generate_with_meditron(question, context_text)
        if not answer:
            # Fallback to Granite if Meditron fails
            print("⚠️ Meditron failed, falling back to Granite...")
            answer = await generate_with_granite(question, context_text)
            model_used = "granite" if answer else "none"

    # If both models failed, return a graceful error message
    if not answer:
        answer = (
            "I apologize, but I'm currently unable to generate a response. "
            "Both AI models (IBM Granite and Meditron) are temporarily unavailable. "
            "Please try again in a moment or check the system status at /api/health."
        )
        model_used = "none"
        confidence = "low"

    return {
        "answer": answer,  # The generated medical answer
        "model_used": model_used,  # Which model actually generated the answer
        "confidence": confidence,  # Confidence level based on retrieval quality
    }
