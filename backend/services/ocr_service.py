# ============================================================================
# ocr_service.py — OCR (Optical Character Recognition) Service
# Extracts text from images (JPG, JPEG, PNG) including handwritten content.
# Uses Microsoft's TrOCR model via HuggingFace Inference API (no local GPU needed).
# Source: https://huggingface.co/microsoft/trocr-large-handwritten
# Source: https://arxiv.org/abs/2109.10282 (TrOCR paper by Li et al.)
# ============================================================================

import httpx  # Async HTTP client for calling HuggingFace API — Source: https://www.python-httpx.org/
import base64  # Base64 encoding for sending images to API — Source: https://docs.python.org/3/library/base64.html
import io  # BytesIO for image manipulation — Source: https://docs.python.org/3/library/io.html
from PIL import Image  # Pillow for image preprocessing — Source: https://pillow.readthedocs.io/
from typing import Optional  # Type hints — Source: https://docs.python.org/3/library/typing.html
from config import settings  # Centralized configuration — Source: ./config.py


# HuggingFace Inference API base URL for model inference
# Source: https://huggingface.co/docs/api-inference/index
HF_API_BASE = "https://api-inference.huggingface.co/models"

# HTTP headers for HuggingFace API authentication
# Source: https://huggingface.co/docs/api-inference/quicktour#running-inference-with-api-requests
HEADERS = {
    "Authorization": f"Bearer {settings.HF_API_TOKEN}",  # HuggingFace API token
}


def preprocess_image(image_bytes: bytes, max_size: int = 1024) -> bytes:
    """
    Preprocess an image for optimal OCR results.
    Resizes large images, converts to RGB, and enhances contrast.

    Args:
        image_bytes: Raw bytes of the uploaded image
        max_size: Maximum dimension (width or height) in pixels

    Returns:
        Preprocessed image bytes in JPEG format

    Source: https://pillow.readthedocs.io/en/stable/handbook/tutorial.html
    Source: https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html (preprocessing best practices)
    """
    # Open the image from raw bytes using Pillow
    # Source: https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.open
    image = Image.open(io.BytesIO(image_bytes))

    # Convert to RGB if image has alpha channel (RGBA) or is grayscale
    # TrOCR expects RGB input — Source: https://huggingface.co/microsoft/trocr-large-handwritten
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Resize if image is too large (saves API bandwidth and improves speed)
    # Source: https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.thumbnail
    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)  # High-quality downsampling

    # Convert back to bytes in JPEG format
    # Source: https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=95)  # High quality JPEG
    return output.getvalue()  # Return preprocessed image bytes


async def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extract text from an image using Microsoft TrOCR via HuggingFace Inference API.
    TrOCR is a transformer-based model specifically trained for handwriting recognition.

    This function sends the image to the HF API and returns the extracted text.
    No local GPU required — all inference happens on HuggingFace's servers.

    Args:
        image_bytes: Raw bytes of the image file (JPG, JPEG, or PNG)

    Returns:
        Extracted text string from the image

    Source: https://huggingface.co/microsoft/trocr-large-handwritten
    Source: https://huggingface.co/docs/api-inference/tasks/image-to-text
    """
    # Preprocess the image for optimal OCR results
    processed_bytes = preprocess_image(image_bytes)

    # Try TrOCR for handwriting recognition first
    # Source: https://huggingface.co/microsoft/trocr-large-handwritten
    text = await _call_ocr_model(processed_bytes, settings.TROCR_MODEL_ID)

    # If TrOCR returns empty or very short text, try a general OCR model as fallback
    # Source: https://huggingface.co/microsoft/trocr-base-printed (alternative for printed text)
    if not text or len(text.strip()) < 3:
        print("⚠️ TrOCR returned minimal text, trying printed text model...")
        text = await _call_ocr_model(processed_bytes, "microsoft/trocr-base-printed")

    # If still no text, try a document understanding model
    # Source: https://huggingface.co/naver-clova-ix/donut-base-finetuned-cord-v2
    if not text or len(text.strip()) < 3:
        print("⚠️ Printed OCR also minimal, trying document understanding model...")
        text = await _call_document_model(processed_bytes)

    return text.strip() if text else ""  # Return cleaned text or empty string


async def _call_ocr_model(image_bytes: bytes, model_id: str) -> Optional[str]:
    """
    Call a HuggingFace image-to-text model with the given image bytes.
    Handles the API request and response parsing.

    Args:
        image_bytes: Preprocessed image bytes
        model_id: HuggingFace model ID for OCR

    Returns:
        Extracted text or None if the call fails

    Source: https://huggingface.co/docs/api-inference/tasks/image-to-text
    """
    # Construct the API endpoint URL for the specific model
    url = f"{HF_API_BASE}/{model_id}"

    # Make the async HTTP request to HuggingFace Inference API
    # For image-to-text tasks, send raw image bytes with appropriate content type
    # Source: https://huggingface.co/docs/api-inference/tasks/image-to-text#using-the-api
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                url,  # Model-specific endpoint
                headers={**HEADERS, "Content-Type": "application/octet-stream"},  # Send as binary
                content=image_bytes,  # Raw image bytes as request body
                params={"wait_for_model": "true"},  # Wait for model to load if cold — Source: https://huggingface.co/docs/api-inference/parameters
            )
            response.raise_for_status()  # Raise on HTTP errors — Source: https://www.python-httpx.org/exceptions/

            # Parse the JSON response — image-to-text returns a list of generated texts
            # Source: https://huggingface.co/docs/api-inference/tasks/image-to-text#output
            result = response.json()

            # Extract the generated text from the response
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")  # First result's text
            return None  # No text extracted

        except httpx.HTTPStatusError as e:
            # Log the error and return None (caller will try fallback)
            print(f"⚠️ OCR model {model_id} error: {e.response.status_code}")
            return None
        except Exception as e:
            print(f"⚠️ OCR model {model_id} unexpected error: {e}")
            return None


async def _call_document_model(image_bytes: bytes) -> Optional[str]:
    """
    Fallback: Use a document understanding model for complex document images.
    This model can handle structured documents, forms, and mixed content.

    Source: https://huggingface.co/Salesforce/blip2-opt-2.7b
    Source: https://huggingface.co/docs/api-inference/tasks/image-to-text
    """
    # Use BLIP-2 as a general-purpose image understanding model
    # Source: https://huggingface.co/Salesforce/blip2-opt-2.7b
    url = f"{HF_API_BASE}/Salesforce/blip2-opt-2.7b"

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                url,  # BLIP-2 endpoint
                headers={**HEADERS, "Content-Type": "application/octet-stream"},  # Send as binary
                content=image_bytes,  # Raw image bytes
                params={"wait_for_model": "true"},  # Wait for model loading
            )
            response.raise_for_status()  # Raise on HTTP errors

            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")  # Return extracted description
            return None

        except Exception as e:
            print(f"⚠️ Document model error: {e}")
            return None
