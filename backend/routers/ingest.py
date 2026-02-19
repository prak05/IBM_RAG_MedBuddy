# ============================================================================
# ingest.py — PubMed Knowledge Base Ingestion Endpoint
# Allows users to populate the knowledge base with PubMed medical abstracts
# by searching for specific topics (e.g., "cardiac arrest", "diabetes treatment").
# Source: https://www.ncbi.nlm.nih.gov/books/NBK25501/ (NCBI E-utilities)
# Source: https://fastapi.tiangolo.com/tutorial/first-steps/
# ============================================================================

from fastapi import APIRouter, HTTPException, BackgroundTasks  # FastAPI with background task support — Source: https://fastapi.tiangolo.com/tutorial/background-tasks/
from models.schemas import PubMedIngestRequest, PubMedIngestResponse, KnowledgeBaseStats, DocumentInfo  # Request/response schemas — Source: ./models/schemas.py
from services.pubmed_service import ingest_pubmed_articles  # PubMed ingestion pipeline — Source: ./services/pubmed_service.py
from services.vector_service import get_all_documents, get_knowledge_stats  # Knowledge base queries — Source: ./services/vector_service.py
from typing import List  # Type hints — Source: https://docs.python.org/3/library/typing.html

# Create a router instance for ingestion endpoints
# Source: https://fastapi.tiangolo.com/tutorial/bigger-applications/#apirouter
router = APIRouter()


@router.post("/ingest/pubmed", response_model=PubMedIngestResponse)
async def ingest_pubmed(request: PubMedIngestRequest):
    """
    Ingest PubMed abstracts into the knowledge base.
    Searches PubMed for the given query, fetches abstracts, chunks them,
    generates embeddings, and stores everything in Supabase pgvector.

    This endpoint runs synchronously — for large ingestions (1000+ abstracts),
    consider using the background task variant.

    Source: https://www.ncbi.nlm.nih.gov/books/NBK25501/
    Source: https://fastapi.tiangolo.com/tutorial/body/
    """
    try:
        # Run the full PubMed ingestion pipeline
        # Source: https://www.ncbi.nlm.nih.gov/books/NBK25501/
        print(f"📚 Starting PubMed ingestion: query='{request.query}', max={request.max_results}")
        stats = await ingest_pubmed_articles(
            query=request.query,  # PubMed search query
            max_results=request.max_results,  # Maximum abstracts to fetch
        )

        # Build the response message
        message = (
            f"Successfully ingested {stats['total_indexed']} of {stats['total_fetched']} "
            f"PubMed abstracts for query: '{request.query}'"
        )

        return PubMedIngestResponse(
            query=request.query,  # Echo back the search query
            total_fetched=stats["total_fetched"],  # How many abstracts were fetched
            total_indexed=stats["total_indexed"],  # How many were successfully indexed
            message=message,  # Human-readable summary
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,  # Internal server error
            detail=f"PubMed ingestion failed: {str(e)}",
        )


@router.get("/knowledge/stats", response_model=KnowledgeBaseStats)
async def knowledge_stats():
    """
    Get aggregate statistics about the knowledge base.
    Returns total documents, chunks, and breakdowns by source type.
    Used by the frontend knowledge base dashboard.

    Source: https://fastapi.tiangolo.com/tutorial/first-steps/
    """
    try:
        # Query Supabase for aggregate statistics
        stats = await get_knowledge_stats()

        return KnowledgeBaseStats(
            total_documents=stats["total_documents"],  # Total indexed documents
            total_chunks=stats["total_chunks"],  # Total text chunks in vector store
            pubmed_count=stats["pubmed_count"],  # PubMed abstracts count
            upload_count=stats["upload_count"],  # User-uploaded documents count
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch knowledge base stats: {str(e)}",
        )


@router.get("/knowledge/documents", response_model=List[DocumentInfo])
async def list_documents():
    """
    List all documents in the knowledge base.
    Returns document metadata for the knowledge base browsing page.

    Source: https://fastapi.tiangolo.com/tutorial/first-steps/
    Source: https://supabase.com/docs/reference/python/select
    """
    try:
        # Fetch all documents from Supabase, ordered by creation date
        documents = await get_all_documents()

        return [
            DocumentInfo(
                id=doc["id"],  # Document UUID
                filename=doc["filename"],  # Original filename or article title
                file_type=doc["file_type"],  # pdf, txt, md, image, pubmed
                source=doc["source"],  # upload or pubmed
                pubmed_id=doc.get("pubmed_id"),  # PubMed ID if applicable
                created_at=str(doc.get("created_at", "")),  # ISO timestamp
            )
            for doc in documents  # Transform each document record
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch documents: {str(e)}",
        )
