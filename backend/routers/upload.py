# ============================================================================
# upload.py — File Upload API Endpoint
# Handles multipart file uploads (PDF, TXT, MD, JPG, JPEG, PNG), processes them
# through the appropriate parser (document or OCR), chunks the text, generates
# embeddings, and stores everything in Supabase pgvector.
# Source: https://fastapi.tiangolo.com/tutorial/request-files/
# ============================================================================

from fastapi import APIRouter, UploadFile, File, HTTPException  # FastAPI file upload support — Source: https://fastapi.tiangolo.com/tutorial/request-files/
from models.schemas import UploadResponse  # Response schema — Source: ./models/schemas.py
from services.document_service import process_document  # PDF/TXT/MD processor — Source: ./services/document_service.py
from services.ocr_service import extract_text_from_image  # Image OCR processor — Source: ./services/ocr_service.py
from services.document_service import chunk_text  # Text chunking utility — Source: ./services/document_service.py
from services.embedding_service import embed_batch  # Batch embedding — Source: ./services/embedding_service.py
from services.vector_service import store_document, store_chunks  # Supabase storage — Source: ./services/vector_service.py

# Create a router instance for upload endpoints
# Source: https://fastapi.tiangolo.com/tutorial/bigger-applications/#apirouter
router = APIRouter()

# Supported file types and their MIME type mappings
# Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
SUPPORTED_EXTENSIONS = {
    "pdf": "pdf",  # PDF documents
    "txt": "txt",  # Plain text files
    "md": "md",  # Markdown files
    "jpg": "image",  # JPEG images (for OCR)
    "jpeg": "image",  # JPEG images (alternative extension)
    "png": "image",  # PNG images (for OCR)
}


def detect_file_type(filename: str) -> str:
    """
    Detect the file type from the filename extension.
    Returns a normalized type string: 'pdf', 'txt', 'md', or 'image'.

    Args:
        filename: The original filename with extension

    Returns:
        Normalized file type string

    Source: https://docs.python.org/3/library/os.path.html#os.path.splitext
    """
    # Extract the file extension and normalize to lowercase
    # Source: https://docs.python.org/3/library/os.path.html#os.path.splitext
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    # Look up the extension in our supported types map
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: .{extension}. "
            f"Supported: {', '.join(SUPPORTED_EXTENSIONS.keys())}"  # List all supported types
        )

    return SUPPORTED_EXTENSIONS[extension]  # Return normalized type string


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a medical document or image for the RAG knowledge base.

    Processing Pipeline:
    1. Validate file type (PDF, TXT, MD, JPG, JPEG, PNG)
    2. Read file bytes
    3. Route to appropriate processor:
       - PDF/TXT/MD → document_service (text extraction + chunking)
       - JPG/JPEG/PNG → ocr_service (handwriting recognition) → chunking
    4. Generate embeddings for all chunks using PubMedBERT
    5. Store document record and chunks with embeddings in Supabase

    Source: https://fastapi.tiangolo.com/tutorial/request-files/
    """
    # Step 1: Validate the uploaded file type
    # Source: https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile
    try:
        file_type = detect_file_type(file.filename)  # Detect from extension
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))  # Return 400 Bad Request for unsupported types

    # Step 2: Read the file bytes into memory
    # Source: https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile
    file_bytes = await file.read()  # Read entire file content as bytes

    # Validate file size (max 50MB to prevent abuse)
    # Source: https://fastapi.tiangolo.com/tutorial/request-files/
    max_size = 50 * 1024 * 1024  # 50 MB in bytes
    if len(file_bytes) > max_size:
        raise HTTPException(
            status_code=413,  # 413 Payload Too Large
            detail=f"File too large: {len(file_bytes) / (1024*1024):.1f}MB. Maximum is 50MB.",
        )

    # Step 3: Route to appropriate processor based on file type
    ocr_text = None  # Will hold OCR-extracted text for image uploads
    chunks = []  # Will hold processed text chunks

    try:
        if file_type == "image":
            # Process image through OCR pipeline
            # Source: https://huggingface.co/microsoft/trocr-large-handwritten
            print(f"🖼️ Processing image: {file.filename} ({len(file_bytes)} bytes)")
            ocr_text = await extract_text_from_image(file_bytes)  # Extract text via TrOCR

            if not ocr_text or not ocr_text.strip():
                raise HTTPException(
                    status_code=422,  # 422 Unprocessable Entity
                    detail="OCR could not extract any text from this image. "
                           "Please try a clearer image or a different format.",
                )

            # Chunk the OCR-extracted text
            chunks = chunk_text(
                ocr_text,
                metadata={"filename": file.filename, "source": "upload", "ocr": True},
            )
        else:
            # Process document (PDF, TXT, or MD)
            print(f"📄 Processing document: {file.filename} ({len(file_bytes)} bytes)")
            chunks = process_document(file_bytes, file.filename, file_type)

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(
            status_code=500,  # Internal server error
            detail=f"Document processing failed: {str(e)}",
        )

    # Validate that we got some chunks
    if not chunks:
        raise HTTPException(
            status_code=422,  # 422 Unprocessable Entity
            detail="No text content could be extracted from this file.",
        )

    # Step 4: Generate embeddings for all chunks using PubMedBERT
    # Source: https://huggingface.co/NeuML/pubmedbert-base-embeddings
    try:
        print(f"🧮 Generating embeddings for {len(chunks)} chunks...")
        texts = [c["content"] for c in chunks]  # Extract text content from chunks
        embeddings = await embed_batch(texts)  # Batch embed all chunks
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Embedding generation failed: {str(e)}",
        )

    # Step 5: Store the document and chunks in Supabase
    # Source: https://supabase.com/docs/reference/python/insert
    try:
        # Create the document record
        doc_id = await store_document(
            filename=file.filename,  # Original filename
            file_type=file_type,  # Normalized file type
            source="upload",  # Mark as user upload
        )

        # Store all chunks with their embeddings
        chunk_count = await store_chunks(doc_id, chunks, embeddings)
        print(f"✅ Stored {chunk_count} chunks for document {doc_id}")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database storage failed: {str(e)}",
        )

    # Return success response with document details
    # Source: https://fastapi.tiangolo.com/tutorial/response-model/
    return UploadResponse(
        document_id=doc_id,  # UUID of the new document record
        filename=file.filename,  # Original filename
        file_type=file_type,  # Detected file type
        chunk_count=chunk_count,  # Number of chunks created
        message=f"Successfully processed and indexed {file.filename} ({chunk_count} chunks)",
        ocr_text=ocr_text[:500] if ocr_text else None,  # First 500 chars of OCR text for preview
    )
