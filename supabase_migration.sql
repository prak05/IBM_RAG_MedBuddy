-- ============================================================================
-- supabase_migration.sql — Supabase Database Schema for MedBuddy v2
-- Run this in the Supabase SQL Editor (Dashboard → SQL Editor → New Query)
-- Source: https://supabase.com/dashboard/project/_/sql
-- ============================================================================

-- Enable the pgvector extension for vector similarity search
-- Source: https://supabase.com/docs/guides/ai/vector-columns
-- Source: https://github.com/pgvector/pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- Table: documents — Tracks all uploaded files and PubMed articles
-- Source: https://supabase.com/docs/guides/database/tables
-- ============================================================================
CREATE TABLE IF NOT EXISTS documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,           -- Unique document identifier — Source: https://www.postgresql.org/docs/current/functions-uuid.html
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL, -- Optional link to authenticated user — Source: https://supabase.com/docs/guides/auth
    filename TEXT NOT NULL,                                    -- Original filename or PubMed article title
    file_type TEXT NOT NULL,                                   -- File type: pdf, txt, md, image, pubmed
    source TEXT DEFAULT 'upload',                              -- Source: 'upload' (user) or 'pubmed' (NCBI)
    pubmed_id TEXT,                                            -- PubMed article ID (e.g., '12345678') — Source: https://pubmed.ncbi.nlm.nih.gov/
    storage_path TEXT,                                         -- Path in Supabase Storage bucket
    created_at TIMESTAMPTZ DEFAULT now()                       -- Timestamp of when document was indexed
);

-- ============================================================================
-- Table: chunks — Document text chunks with vector embeddings
-- Each document is split into overlapping chunks for granular retrieval
-- Source: https://supabase.com/docs/guides/ai/vector-columns
-- Source: https://www.pinecone.io/learn/chunking-strategies/
-- ============================================================================
CREATE TABLE IF NOT EXISTS chunks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,             -- Unique chunk identifier
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE, -- Parent document (cascading delete) — Source: https://www.postgresql.org/docs/current/ddl-constraints.html
    content TEXT NOT NULL,                                      -- The actual text content of this chunk
    chunk_index INTEGER,                                       -- Position of this chunk in the document (0-indexed)
    embedding VECTOR(768),                                     -- 768-dimensional PubMedBERT embedding — Source: https://huggingface.co/NeuML/pubmedbert-base-embeddings
    metadata JSONB DEFAULT '{}',                               -- Flexible metadata (page_num, section, etc.) — Source: https://www.postgresql.org/docs/current/datatype-json.html
    created_at TIMESTAMPTZ DEFAULT now()                        -- Timestamp of when chunk was created
);

-- ============================================================================
-- Table: chat_messages — Chat history for conversation persistence
-- Source: https://supabase.com/docs/guides/database/tables
-- ============================================================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,             -- Unique message identifier
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL, -- Optional link to authenticated user
    session_id UUID NOT NULL,                                  -- Groups related messages in a conversation
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),   -- Message role: 'user' or 'assistant'
    content TEXT NOT NULL,                                      -- The message text content
    sources JSONB,                                             -- Citation data for assistant messages
    model_used TEXT,                                           -- Which LLM generated this response (granite/meditron)
    created_at TIMESTAMPTZ DEFAULT now()                        -- Timestamp of when message was sent
);

-- ============================================================================
-- Index: IVFFlat index for fast approximate nearest neighbor search
-- IVFFlat is recommended for pgvector when you have >1000 vectors
-- Source: https://github.com/pgvector/pgvector#ivfflat
-- Source: https://supabase.com/docs/guides/ai/vector-indexes/ivf-indexes
-- ============================================================================
CREATE INDEX IF NOT EXISTS chunks_embedding_idx ON chunks
    USING ivfflat (embedding vector_cosine_ops)                -- Cosine similarity operator — Source: https://github.com/pgvector/pgvector#distance
    WITH (lists = 100);                                        -- 100 IVF lists (good for up to ~100k vectors) — Source: https://github.com/pgvector/pgvector#ivfflat

-- Index on document_id for fast chunk lookups by document
-- Source: https://www.postgresql.org/docs/current/indexes.html
CREATE INDEX IF NOT EXISTS chunks_document_id_idx ON chunks(document_id);

-- Index on session_id for fast chat history lookups
-- Source: https://www.postgresql.org/docs/current/indexes.html
CREATE INDEX IF NOT EXISTS chat_messages_session_id_idx ON chat_messages(session_id);

-- Index on source for filtering documents by type
-- Source: https://www.postgresql.org/docs/current/indexes.html
CREATE INDEX IF NOT EXISTS documents_source_idx ON documents(source);

-- ============================================================================
-- Function: match_chunks — Vector similarity search using pgvector
-- Called via Supabase RPC from the backend Python code
-- Source: https://supabase.com/docs/guides/ai/vector-columns#querying-a-vector-embedding
-- Source: https://github.com/pgvector/pgvector#querying
-- ============================================================================
CREATE OR REPLACE FUNCTION match_chunks(
    query_embedding VECTOR(768),                               -- The query vector to search against (768-dim PubMedBERT)
    match_threshold FLOAT DEFAULT 0.5,                         -- Minimum cosine similarity score (0.0 to 1.0)
    match_count INT DEFAULT 5                                  -- Maximum number of results to return
)
RETURNS TABLE (
    id UUID,                                                   -- Chunk ID
    content TEXT,                                              -- Chunk text content
    document_id UUID,                                          -- Parent document ID
    metadata JSONB,                                            -- Chunk metadata
    similarity FLOAT                                           -- Cosine similarity score
)
LANGUAGE plpgsql                                               -- PL/pgSQL procedural language — Source: https://www.postgresql.org/docs/current/plpgsql.html
AS $$
BEGIN
    RETURN QUERY
    SELECT
        chunks.id,                                             -- Return the chunk UUID
        chunks.content,                                        -- Return the chunk text
        chunks.document_id,                                    -- Return the parent document UUID
        chunks.metadata,                                       -- Return the chunk metadata
        1 - (chunks.embedding <=> query_embedding) AS similarity -- Calculate cosine similarity — Source: https://github.com/pgvector/pgvector#distance
    FROM chunks
    WHERE 1 - (chunks.embedding <=> query_embedding) > match_threshold -- Filter by minimum similarity
    ORDER BY chunks.embedding <=> query_embedding              -- Sort by distance (ascending = most similar first)
    LIMIT match_count;                                         -- Limit results
END;
$$;

-- ============================================================================
-- Row Level Security (RLS) — Restrict data access per user
-- Source: https://supabase.com/docs/guides/auth/row-level-security
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Policy: Allow service role full access (for backend server-side operations)
-- Source: https://supabase.com/docs/guides/auth/row-level-security#service-key
CREATE POLICY "Service role full access on documents" ON documents
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access on chunks" ON chunks
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access on chat_messages" ON chat_messages
    FOR ALL USING (true) WITH CHECK (true);

-- ============================================================================
-- Storage: Create bucket for uploaded files
-- Run this separately in Supabase Dashboard → Storage → New Bucket
-- Bucket name: medbuddy-uploads
-- Public: false (private, accessed via signed URLs)
-- ============================================================================
-- Note: Storage bucket creation is done via Supabase Dashboard, not SQL.
-- Go to: https://supabase.com/dashboard/project/_/storage/buckets
-- Click "New Bucket" → Name: "medbuddy-uploads" → Public: unchecked

-- ============================================================================
-- DONE! Your Supabase database is ready for MedBuddy v2.
-- Next steps:
-- 1. Run the seed script: cd backend && python -m scripts.seed_pubmed
-- 2. Start the backend: cd backend && uvicorn main:app --reload
-- 3. Start the frontend: cd frontend && npm run dev
-- ============================================================================
