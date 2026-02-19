# ============================================================================
# schemas.py — Pydantic Models for API Request/Response Validation
# Defines the data shapes for all API endpoints using Pydantic v2.
# FastAPI uses these for automatic validation, serialization, and OpenAPI docs.
# Source: https://fastapi.tiangolo.com/tutorial/body/
# Source: https://docs.pydantic.dev/latest/
# ============================================================================

from pydantic import BaseModel, Field  # Pydantic base class and field validators — Source: https://docs.pydantic.dev/latest/concepts/models/
from typing import Optional, List  # Type hints for optional and list fields — Source: https://docs.python.org/3/library/typing.html
from datetime import datetime  # Datetime type for timestamps — Source: https://docs.python.org/3/library/datetime.html
from uuid import UUID  # UUID type for unique identifiers — Source: https://docs.python.org/3/library/uuid.html


# ========================= Chat Schemas =========================

class ChatRequest(BaseModel):
    """
    Request body for the /api/chat endpoint.
    Contains the user's question and optional session/model preferences.
    Source: https://fastapi.tiangolo.com/tutorial/body/
    """
    question: str = Field(  # The user's medical question to answer
        ...,  # Required field (no default value)
        min_length=1,  # Must be at least 1 character — Source: https://docs.pydantic.dev/latest/concepts/fields/#string-constraints
        max_length=5000,  # Cap at 5000 chars to prevent abuse
        description="The medical question to ask the RAG system"  # OpenAPI description
    )
    session_id: Optional[str] = Field(  # Optional session ID for chat history grouping
        default=None,  # Defaults to None if not provided
        description="Session ID to group related chat messages together"  # OpenAPI description
    )
    model: Optional[str] = Field(  # Which LLM to use for this query
        default="granite",  # Default to IBM Granite (primary model)
        description="LLM to use: 'granite' (IBM Watsonx) or 'meditron' (HuggingFace)"  # OpenAPI description
    )
    top_k: Optional[int] = Field(  # Number of chunks to retrieve
        default=5,  # Retrieve 5 most relevant chunks by default
        ge=1,  # Minimum 1 chunk — Source: https://docs.pydantic.dev/latest/concepts/fields/#numeric-constraints
        le=20,  # Maximum 20 chunks to limit context size
        description="Number of similar document chunks to retrieve"  # OpenAPI description
    )


class Citation(BaseModel):
    """
    Represents a single source citation from the vector search results.
    Displayed alongside AI responses to show evidence grounding.
    Source: https://arxiv.org/abs/2005.11401 (RAG paper — retrieval-augmented generation)
    """
    content: str = Field(..., description="The text content of the retrieved chunk")  # The actual retrieved passage
    source: str = Field(..., description="Source of the chunk: 'upload', 'pubmed'")  # Where the chunk came from
    filename: Optional[str] = Field(default=None, description="Original filename if from upload")  # Original file name
    pubmed_id: Optional[str] = Field(default=None, description="PubMed article ID if from PubMed")  # PubMed identifier
    similarity: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")  # How relevant this chunk is
    page_num: Optional[int] = Field(default=None, description="Page number in source document")  # Page reference


class ChatResponse(BaseModel):
    """
    Response body for the /api/chat endpoint.
    Contains the AI's answer along with source citations and metadata.
    Source: https://fastapi.tiangolo.com/tutorial/response-model/
    """
    answer: str = Field(..., description="The AI-generated answer to the question")  # The LLM's response text
    citations: List[Citation] = Field(  # List of source citations backing the answer
        default=[],  # Empty list if no citations found
        description="Source citations from the knowledge base"  # OpenAPI description
    )
    model_used: str = Field(..., description="Which LLM generated this answer")  # granite or meditron
    confidence: str = Field(  # Confidence level based on retrieval quality
        default="medium",  # Default to medium confidence
        description="Answer confidence: 'high', 'medium', or 'low' based on retrieval similarity"  # OpenAPI description
    )
    session_id: Optional[str] = Field(default=None, description="Session ID for this conversation")  # Session tracking


# ========================= Upload Schemas =========================

class UploadResponse(BaseModel):
    """
    Response body for the /api/upload endpoint.
    Returns information about the uploaded and processed document.
    Source: https://fastapi.tiangolo.com/tutorial/response-model/
    """
    document_id: str = Field(..., description="Unique ID of the uploaded document in Supabase")  # UUID of the new document record
    filename: str = Field(..., description="Original filename of the uploaded file")  # What the user uploaded
    file_type: str = Field(..., description="Detected file type: pdf, txt, md, image")  # File classification
    chunk_count: int = Field(..., description="Number of text chunks created from the document")  # How many chunks were indexed
    message: str = Field(..., description="Human-readable status message")  # Success/info message
    ocr_text: Optional[str] = Field(  # Extracted text from OCR (for image uploads only)
        default=None,  # None for non-image uploads
        description="Extracted text from OCR processing (for image uploads)"  # OpenAPI description
    )


# ========================= Ingest Schemas =========================

class PubMedIngestRequest(BaseModel):
    """
    Request body for the /api/ingest/pubmed endpoint.
    Specifies which PubMed topics to ingest and how many abstracts.
    Source: https://www.ncbi.nlm.nih.gov/books/NBK25501/ (NCBI E-utilities documentation)
    """
    query: str = Field(  # PubMed search query string
        ...,  # Required field
        min_length=1,  # Must have at least 1 character
        description="PubMed search query (e.g., 'cardiac arrest treatment')"  # OpenAPI description
    )
    max_results: Optional[int] = Field(  # How many abstracts to fetch
        default=100,  # Fetch 100 abstracts by default
        ge=1,  # Minimum 1 result
        le=10000,  # Maximum 10,000 to prevent overload
        description="Maximum number of PubMed abstracts to ingest"  # OpenAPI description
    )


class PubMedIngestResponse(BaseModel):
    """
    Response body for the /api/ingest/pubmed endpoint.
    Reports how many abstracts were successfully ingested.
    Source: https://fastapi.tiangolo.com/tutorial/response-model/
    """
    query: str = Field(..., description="The PubMed search query that was executed")  # Echo back the query
    total_fetched: int = Field(..., description="Number of abstracts fetched from PubMed")  # How many we got from NCBI
    total_indexed: int = Field(..., description="Number of abstracts successfully embedded and stored")  # How many made it to pgvector
    message: str = Field(..., description="Human-readable status message")  # Success/info message


# ========================= Knowledge Base Schemas =========================

class DocumentInfo(BaseModel):
    """
    Information about a document stored in the knowledge base.
    Used in the knowledge base browsing page.
    Source: https://docs.pydantic.dev/latest/concepts/models/
    """
    id: str = Field(..., description="Document UUID")  # Unique identifier
    filename: str = Field(..., description="Original filename or PubMed title")  # Display name
    file_type: str = Field(..., description="File type: pdf, txt, md, image, pubmed")  # Type classification
    source: str = Field(..., description="Source: 'upload' or 'pubmed'")  # Where it came from
    pubmed_id: Optional[str] = Field(default=None, description="PubMed ID if applicable")  # PubMed reference
    chunk_count: Optional[int] = Field(default=None, description="Number of chunks from this document")  # Index size
    created_at: Optional[str] = Field(default=None, description="ISO timestamp of when document was indexed")  # When it was added


class KnowledgeBaseStats(BaseModel):
    """
    Aggregate statistics about the knowledge base.
    Shown on the knowledge base dashboard page.
    Source: https://docs.pydantic.dev/latest/concepts/models/
    """
    total_documents: int = Field(..., description="Total number of indexed documents")  # Document count
    total_chunks: int = Field(..., description="Total number of text chunks in vector store")  # Chunk count
    pubmed_count: int = Field(..., description="Number of PubMed abstracts indexed")  # PubMed subset count
    upload_count: int = Field(..., description="Number of user-uploaded documents indexed")  # Upload subset count


# ========================= Health Schema =========================

class HealthResponse(BaseModel):
    """
    Response body for the /api/health endpoint.
    Reports the operational status of all backend services.
    Source: https://microservices.io/patterns/observability/health-check-api.html
    """
    status: str = Field(..., description="Overall health status: 'healthy' or 'degraded'")  # Overall status
    supabase: str = Field(..., description="Supabase connection status")  # DB health
    watsonx: str = Field(..., description="IBM Watsonx API status")  # LLM health
    huggingface: str = Field(..., description="HuggingFace Inference API status")  # HF API health
    version: str = Field(default="2.0.0", description="API version")  # Version number
