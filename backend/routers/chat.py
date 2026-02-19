# ============================================================================
# chat.py — Chat API Endpoints (Question Answering + Streaming)
# Handles the core RAG pipeline: receive question → retrieve context → generate answer.
# Provides both a standard POST endpoint and an SSE streaming endpoint.
# Source: https://fastapi.tiangolo.com/tutorial/first-steps/
# Source: https://arxiv.org/abs/2005.11401 (RAG: Retrieval-Augmented Generation)
# ============================================================================

import json  # JSON serialization for SSE events — Source: https://docs.python.org/3/library/json.html
import uuid  # UUID generation for session IDs — Source: https://docs.python.org/3/library/uuid.html
from fastapi import APIRouter, HTTPException  # FastAPI router and error handling — Source: https://fastapi.tiangolo.com/tutorial/handling-errors/
from fastapi.responses import StreamingResponse  # Streaming response for SSE — Source: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
from models.schemas import ChatRequest, ChatResponse, Citation  # Request/response schemas — Source: ./models/schemas.py
from services.vector_service import search_similar  # Vector similarity search — Source: ./services/vector_service.py
from services.llm_service import generate_answer  # Hybrid LLM generation — Source: ./services/llm_service.py
from models.database import supabase  # Supabase client for chat history — Source: ./models/database.py

# Create a router instance for chat endpoints
# Source: https://fastapi.tiangolo.com/tutorial/bigger-applications/#apirouter
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint — receives a medical question and returns an AI-generated
    answer with source citations from the knowledge base.

    RAG Pipeline:
    1. Embed the user's question using PubMedBERT
    2. Search Supabase pgvector for the top-K most similar chunks
    3. Augment the LLM prompt with retrieved context passages
    4. Generate answer using IBM Granite (primary) or Meditron (secondary)
    5. Return answer with citations and confidence score

    Source: https://arxiv.org/abs/2005.11401 (RAG paper by Lewis et al.)
    Source: https://fastapi.tiangolo.com/tutorial/body/
    """
    # Generate a session ID if not provided (for grouping related messages)
    # Source: https://docs.python.org/3/library/uuid.html#uuid.uuid4
    session_id = request.session_id or str(uuid.uuid4())

    # Step 1 & 2: Retrieve relevant context from the vector store
    # This embeds the query and performs cosine similarity search via pgvector
    # Source: https://supabase.com/docs/guides/ai/vector-columns#querying-a-vector-embedding
    try:
        search_results = await search_similar(
            query=request.question,  # The user's medical question
            top_k=request.top_k,  # Number of chunks to retrieve (default: 5)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,  # Internal server error
            detail=f"Vector search failed: {str(e)}. Is the knowledge base indexed?",
        )

    # Step 3 & 4: Generate answer using the hybrid LLM service
    # Source: https://arxiv.org/abs/2005.11401 (RAG: context-augmented generation)
    try:
        result = await generate_answer(
            question=request.question,  # The user's question
            context_chunks=search_results,  # Retrieved context passages
            model_preference=request.model or "granite",  # Preferred LLM model
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,  # Internal server error
            detail=f"LLM generation failed: {str(e)}",
        )

    # Step 5: Build citation objects from search results
    # Source: https://docs.pydantic.dev/latest/concepts/models/
    citations = [
        Citation(
            content=chunk["content"][:300],  # Truncate chunk content for display (max 300 chars)
            source=chunk.get("source", "upload"),  # Source type (upload or pubmed)
            filename=chunk.get("filename"),  # Original filename
            pubmed_id=chunk.get("pubmed_id"),  # PubMed ID for linking
            similarity=round(chunk.get("similarity", 0.0), 3),  # Rounded similarity score
            page_num=chunk.get("metadata", {}).get("page_num"),  # Page number if available
        )
        for chunk in search_results  # Create a Citation for each retrieved chunk
    ]

    # Save the conversation to chat history in Supabase
    # Source: https://supabase.com/docs/reference/python/insert
    try:
        # Save user message
        supabase.table("chat_messages").insert({
            "session_id": session_id,  # Group messages by session
            "role": "user",  # This is a user message
            "content": request.question,  # The question text
        }).execute()

        # Save assistant response
        supabase.table("chat_messages").insert({
            "session_id": session_id,  # Same session as the question
            "role": "assistant",  # This is an AI response
            "content": result["answer"],  # The generated answer
            "model_used": result["model_used"],  # Which LLM was used
            "sources": json.dumps([c.model_dump() for c in citations]),  # Serialized citations
        }).execute()
    except Exception as e:
        # Don't fail the request if history saving fails — the answer is more important
        print(f"⚠️ Failed to save chat history: {e}")

    # Return the complete response
    # Source: https://fastapi.tiangolo.com/tutorial/response-model/
    return ChatResponse(
        answer=result["answer"],  # The AI-generated medical answer
        citations=citations,  # Source citations from knowledge base
        model_used=result["model_used"],  # Which model generated the answer
        confidence=result["confidence"],  # Confidence level (high/medium/low)
        session_id=session_id,  # Session ID for conversation tracking
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint using Server-Sent Events (SSE).
    Sends the answer token-by-token for a real-time typing effect in the UI.

    Note: Currently simulates streaming by chunking the full response.
    True token-by-token streaming requires model-specific streaming APIs.

    Source: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
    Source: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
    """
    import asyncio  # Async sleep for simulating token delay — Source: https://docs.python.org/3/library/asyncio.html

    async def event_generator():
        """
        Async generator that yields SSE events containing response chunks.
        Source: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#event_stream_format
        """
        try:
            # Step 1: Retrieve context (same as non-streaming endpoint)
            search_results = await search_similar(
                query=request.question,
                top_k=request.top_k,
            )

            # Send a "sources" event with citation data first
            # Source: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#named_events
            citations_data = [
                {
                    "content": chunk["content"][:300],
                    "source": chunk.get("source", "upload"),
                    "filename": chunk.get("filename"),
                    "pubmed_id": chunk.get("pubmed_id"),
                    "similarity": round(chunk.get("similarity", 0.0), 3),
                }
                for chunk in search_results
            ]
            yield f"event: sources\ndata: {json.dumps(citations_data)}\n\n"  # SSE sources event

            # Step 2: Generate the full answer
            result = await generate_answer(
                question=request.question,
                context_chunks=search_results,
                model_preference=request.model or "granite",
            )

            # Send metadata event (model used, confidence)
            metadata = {
                "model_used": result["model_used"],
                "confidence": result["confidence"],
            }
            yield f"event: metadata\ndata: {json.dumps(metadata)}\n\n"  # SSE metadata event

            # Step 3: Stream the answer in small chunks (simulated streaming)
            # Split answer into words and send in groups for a typing effect
            # Source: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
            words = result["answer"].split()  # Split answer into words
            chunk_size = 3  # Send 3 words at a time for natural-looking streaming

            for i in range(0, len(words), chunk_size):
                word_chunk = " ".join(words[i:i + chunk_size])  # Join 3 words
                yield f"data: {json.dumps({'text': word_chunk + ' '})}\n\n"  # SSE data event with text chunk
                await asyncio.sleep(0.05)  # Small delay for typing effect (50ms)

            # Send completion event
            yield f"event: done\ndata: {json.dumps({'status': 'complete'})}\n\n"  # SSE done event

        except Exception as e:
            # Send error event if anything goes wrong
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"  # SSE error event

    # Return a StreamingResponse with SSE content type
    # Source: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
    return StreamingResponse(
        event_generator(),  # The async generator that yields SSE events
        media_type="text/event-stream",  # SSE content type — Source: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
        headers={
            "Cache-Control": "no-cache",  # Disable caching for real-time data
            "Connection": "keep-alive",  # Keep connection open for streaming
            "X-Accel-Buffering": "no",  # Disable Nginx buffering if behind reverse proxy
        },
    )
