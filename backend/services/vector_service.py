# ============================================================================
# vector_service.py — Supabase pgvector Vector Store Service
# Handles storing document chunks with embeddings and performing similarity search.
# Uses PostgreSQL's pgvector extension via Supabase for vector operations.
# Source: https://supabase.com/docs/guides/ai/vector-columns
# Source: https://github.com/pgvector/pgvector
# ============================================================================

from typing import List, Dict, Any, Optional  # Type hints — Source: https://docs.python.org/3/library/typing.html
from models.database import supabase  # Supabase client instance — Source: ./models/database.py
from services.embedding_service import embed_text  # Embedding function — Source: ./services/embedding_service.py
from config import settings  # Centralized configuration — Source: ./config.py


async def store_document(
    filename: str,
    file_type: str,
    source: str = "upload",
    pubmed_id: Optional[str] = None,
    user_id: Optional[str] = None,
    storage_path: Optional[str] = None,
) -> str:
    """
    Insert a new document record into the documents table.
    Returns the generated document UUID for linking chunks.

    Source: https://supabase.com/docs/reference/python/insert
    """
    # Build the document record to insert into Supabase
    # Source: https://supabase.com/docs/reference/python/insert
    doc_data = {
        "filename": filename,  # Original filename or PubMed article title
        "file_type": file_type,  # pdf, txt, md, image, pubmed
        "source": source,  # upload or pubmed
    }

    # Add optional fields only if they have values (avoid null inserts)
    if pubmed_id:
        doc_data["pubmed_id"] = pubmed_id  # PubMed article identifier
    if user_id:
        doc_data["user_id"] = user_id  # Supabase auth user ID
    if storage_path:
        doc_data["storage_path"] = storage_path  # Path in Supabase Storage bucket

    # Execute the insert and return the new document's UUID
    # Source: https://supabase.com/docs/reference/python/insert
    result = supabase.table("documents").insert(doc_data).execute()

    # Extract and return the generated document ID from the response
    # Source: https://supabase.com/docs/reference/python/insert#return-data-after-inserting
    return result.data[0]["id"]


async def store_chunks(
    document_id: str,
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
) -> int:
    """
    Store document chunks with their vector embeddings in the chunks table.
    Each chunk gets its embedding stored for similarity search via pgvector.

    Args:
        document_id: UUID of the parent document
        chunks: List of chunk dicts with 'content' and optional 'metadata'
        embeddings: List of embedding vectors (one per chunk)

    Returns:
        Number of chunks successfully stored

    Source: https://supabase.com/docs/guides/ai/vector-columns#storing-a-vector-embedding
    """
    # Build batch insert data — each row is a chunk with its embedding
    # Source: https://supabase.com/docs/reference/python/insert#insert-many-rows
    rows = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        rows.append({
            "document_id": document_id,  # Foreign key to parent document
            "content": chunk["content"],  # The actual text content of this chunk
            "chunk_index": i,  # Position of this chunk in the original document
            "embedding": embedding,  # 768-dim PubMedBERT vector — Source: https://supabase.com/docs/guides/ai/vector-columns
            "metadata": chunk.get("metadata", {}),  # Optional metadata (page_num, section, etc.)
        })

    # Batch insert all chunks in one database call for efficiency
    # Source: https://supabase.com/docs/reference/python/insert#insert-many-rows
    if rows:
        supabase.table("chunks").insert(rows).execute()

    return len(rows)  # Return count of stored chunks


async def search_similar(
    query: str,
    top_k: int = None,
    threshold: float = None,
) -> List[Dict[str, Any]]:
    """
    Perform vector similarity search against the chunks table using pgvector.
    Embeds the query, then calls the match_chunks PostgreSQL function.

    Args:
        query: The user's question to find similar content for
        top_k: Number of results to return (defaults to config TOP_K)
        threshold: Minimum similarity score (defaults to config SIMILARITY_THRESHOLD)

    Returns:
        List of matching chunks with content, metadata, and similarity scores

    Source: https://supabase.com/docs/guides/ai/vector-columns#querying-a-vector-embedding
    Source: https://supabase.com/docs/reference/python/rpc
    """
    # Use config defaults if not specified
    effective_top_k = top_k or settings.TOP_K  # Default: 5 results
    effective_threshold = threshold or settings.SIMILARITY_THRESHOLD  # Default: 0.5 similarity

    # First, embed the user's query using the same model used for documents
    # Source: https://arxiv.org/abs/2005.11401 (RAG: query and documents must use same embedding space)
    query_embedding = await embed_text(query)

    # Call the match_chunks PostgreSQL function via Supabase RPC
    # This function performs cosine similarity search using pgvector's <=> operator
    # Source: https://supabase.com/docs/reference/python/rpc
    # Source: https://github.com/pgvector/pgvector#querying
    result = supabase.rpc("match_chunks", {
        "query_embedding": query_embedding,  # The query vector to search against
        "match_threshold": effective_threshold,  # Minimum cosine similarity score
        "match_count": effective_top_k,  # Maximum number of results to return
    }).execute()

    # Enrich results with document metadata (filename, source, pubmed_id)
    # Source: https://supabase.com/docs/reference/python/select
    enriched_results = []
    for chunk in result.data:
        # Fetch the parent document info for each chunk
        doc_result = supabase.table("documents").select(
            "filename, source, pubmed_id"  # Only fetch the fields we need for citations
        ).eq("id", chunk["document_id"]).execute()

        # Merge document info into the chunk result
        doc_info = doc_result.data[0] if doc_result.data else {}
        enriched_results.append({
            "content": chunk["content"],  # The retrieved text passage
            "similarity": chunk["similarity"],  # Cosine similarity score (0.0 to 1.0)
            "document_id": chunk["document_id"],  # Parent document UUID
            "metadata": chunk.get("metadata", {}),  # Chunk metadata (page number, etc.)
            "filename": doc_info.get("filename", "Unknown"),  # Source filename
            "source": doc_info.get("source", "upload"),  # Source type
            "pubmed_id": doc_info.get("pubmed_id"),  # PubMed ID if applicable
        })

    return enriched_results  # Return enriched search results


async def delete_document(document_id: str) -> bool:
    """
    Delete a document and all its associated chunks from the database.
    The chunks are automatically deleted due to ON DELETE CASCADE foreign key.

    Source: https://supabase.com/docs/reference/python/delete
    Source: https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-FK
    """
    # Delete the document — chunks cascade automatically via foreign key constraint
    # Source: https://supabase.com/docs/reference/python/delete
    supabase.table("documents").delete().eq("id", document_id).execute()
    return True  # Return True to confirm deletion


async def get_all_documents() -> List[Dict[str, Any]]:
    """
    Fetch all documents from the database for the knowledge base listing page.
    Includes chunk counts for each document.

    Source: https://supabase.com/docs/reference/python/select
    """
    # Fetch all documents ordered by creation date (newest first)
    # Source: https://supabase.com/docs/reference/python/order
    result = supabase.table("documents").select("*").order(
        "created_at", desc=True  # Most recent documents first
    ).execute()

    return result.data  # Return list of document records


async def get_knowledge_stats() -> Dict[str, int]:
    """
    Get aggregate statistics about the knowledge base.
    Returns total documents, chunks, and breakdowns by source.

    Source: https://supabase.com/docs/reference/python/select#selecting-with-count
    """
    # Count total documents
    # Source: https://supabase.com/docs/reference/python/select
    docs_result = supabase.table("documents").select("id", count="exact").execute()
    total_docs = docs_result.count or 0  # Total document count

    # Count total chunks
    chunks_result = supabase.table("chunks").select("id", count="exact").execute()
    total_chunks = chunks_result.count or 0  # Total chunk count

    # Count PubMed documents specifically
    pubmed_result = supabase.table("documents").select("id", count="exact").eq(
        "source", "pubmed"  # Filter for PubMed source only
    ).execute()
    pubmed_count = pubmed_result.count or 0  # PubMed document count

    return {
        "total_documents": total_docs,  # All documents
        "total_chunks": total_chunks,  # All chunks across all documents
        "pubmed_count": pubmed_count,  # PubMed subset
        "upload_count": total_docs - pubmed_count,  # User uploads = total - pubmed
    }
