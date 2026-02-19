// ============================================================================
// lib/api.ts — Backend API Communication Layer
// Handles all HTTP requests to the FastAPI backend, including SSE streaming.
// Source: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
// Source: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
// ============================================================================

// Backend API base URL — loaded from environment variable or defaults to localhost
// Source: https://nextjs.org/docs/app/building-your-application/configuring/environment-variables
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ========================= Types =========================

/** Chat request payload sent to POST /api/chat */
export interface ChatRequest {
  question: string;       // The user's medical question
  session_id?: string;    // Optional session ID for conversation grouping
  model?: string;         // LLM preference: "granite" or "meditron"
  top_k?: number;         // Number of chunks to retrieve (default: 5)
}

/** Citation object returned in chat responses */
export interface Citation {
  content: string;        // Retrieved passage text (truncated)
  source: string;         // Source type: "upload" or "pubmed"
  filename?: string;      // Original filename if from upload
  pubmed_id?: string;     // PubMed ID if from PubMed
  similarity: number;     // Cosine similarity score (0.0 to 1.0)
  page_num?: number;      // Page number in source document
}

/** Chat response from POST /api/chat */
export interface ChatResponse {
  answer: string;         // AI-generated medical answer
  citations: Citation[];  // Source citations backing the answer
  model_used: string;     // Which LLM generated the answer
  confidence: string;     // "high", "medium", or "low"
  session_id?: string;    // Session ID for this conversation
}

/** Upload response from POST /api/upload */
export interface UploadResponse {
  document_id: string;    // UUID of the uploaded document
  filename: string;       // Original filename
  file_type: string;      // Detected file type
  chunk_count: number;    // Number of chunks created
  message: string;        // Success message
  ocr_text?: string;      // Extracted OCR text (for image uploads)
}

/** Knowledge base statistics from GET /api/knowledge/stats */
export interface KnowledgeStats {
  total_documents: number;  // Total indexed documents
  total_chunks: number;     // Total text chunks
  pubmed_count: number;     // PubMed abstracts count
  upload_count: number;     // User uploads count
}

/** Document info from GET /api/knowledge/documents */
export interface DocumentInfo {
  id: string;             // Document UUID
  filename: string;       // Original filename
  file_type: string;      // File type
  source: string;         // "upload" or "pubmed"
  pubmed_id?: string;     // PubMed ID if applicable
  created_at?: string;    // ISO timestamp
}

// ========================= API Functions =========================

/**
 * Send a chat message and receive a complete response (non-streaming).
 * Source: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
 */
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  // Make POST request to the chat endpoint
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",                                    // HTTP POST method
    headers: { "Content-Type": "application/json" },   // JSON request body
    body: JSON.stringify(request),                      // Serialize the request
  });

  // Handle error responses from the backend
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`); // Throw with error detail
  }

  return response.json(); // Parse and return the JSON response
}

/**
 * Send a chat message with Server-Sent Events (SSE) streaming.
 * Returns an async generator that yields text chunks as they arrive.
 * Source: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
 * Source: https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream
 */
export async function* streamChatMessage(
  request: ChatRequest
): AsyncGenerator<{ type: string; data: any }> {
  // Make POST request to the streaming chat endpoint
  const response = await fetch(`${API_BASE}/api/chat/stream`, {
    method: "POST",                                    // HTTP POST method
    headers: { "Content-Type": "application/json" },   // JSON request body
    body: JSON.stringify(request),                      // Serialize the request
  });

  // Handle error responses
  if (!response.ok) {
    throw new Error(`Stream request failed: HTTP ${response.status}`);
  }

  // Get the response body as a ReadableStream
  // Source: https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream
  const reader = response.body?.getReader();            // Get the stream reader
  const decoder = new TextDecoder();                     // Decode bytes to text
  let buffer = "";                                       // Buffer for incomplete SSE events

  if (!reader) throw new Error("No response body");

  // Read the stream chunk by chunk
  while (true) {
    const { done, value } = await reader.read();        // Read next chunk
    if (done) break;                                     // Stream ended

    // Decode the chunk and add to buffer
    buffer += decoder.decode(value, { stream: true });

    // Parse SSE events from the buffer (events are separated by \n\n)
    // Source: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#event_stream_format
    const events = buffer.split("\n\n");
    buffer = events.pop() || "";                         // Keep incomplete event in buffer

    // Process each complete SSE event
    for (const event of events) {
      if (!event.trim()) continue;                       // Skip empty events

      // Parse event type and data from SSE format
      let eventType = "message";                         // Default event type
      let eventData = "";                                // Event data payload

      for (const line of event.split("\n")) {
        if (line.startsWith("event: ")) {
          eventType = line.slice(7);                     // Extract event type after "event: "
        } else if (line.startsWith("data: ")) {
          eventData = line.slice(6);                     // Extract data after "data: "
        }
      }

      // Parse the JSON data and yield the event
      if (eventData) {
        try {
          const parsed = JSON.parse(eventData);          // Parse JSON data
          yield { type: eventType, data: parsed };       // Yield the parsed event
        } catch {
          yield { type: eventType, data: eventData };    // Yield raw string if not JSON
        }
      }
    }
  }
}

/**
 * Upload a file (PDF, TXT, MD, or image) to the backend for processing.
 * Source: https://developer.mozilla.org/en-US/docs/Web/API/FormData
 */
export async function uploadFile(file: File): Promise<UploadResponse> {
  // Create FormData with the file for multipart upload
  // Source: https://developer.mozilla.org/en-US/docs/Web/API/FormData/FormData
  const formData = new FormData();
  formData.append("file", file);                         // Add the file to form data

  // Make POST request with multipart/form-data
  const response = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",                                      // HTTP POST method
    body: formData,                                      // FormData body (browser sets Content-Type automatically)
  });

  // Handle error responses
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json(); // Parse and return the upload response
}

/**
 * Trigger PubMed ingestion for a specific medical topic.
 * Source: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
 */
export async function ingestPubMed(query: string, maxResults: number = 100) {
  const response = await fetch(`${API_BASE}/api/ingest/pubmed`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, max_results: maxResults }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Ingestion failed" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json(); // Return ingestion statistics
}

/**
 * Get knowledge base statistics (document and chunk counts).
 * Source: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
 */
export async function getKnowledgeStats(): Promise<KnowledgeStats> {
  const response = await fetch(`${API_BASE}/api/knowledge/stats`);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

/**
 * Get list of all documents in the knowledge base.
 * Source: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
 */
export async function getDocuments(): Promise<DocumentInfo[]> {
  const response = await fetch(`${API_BASE}/api/knowledge/documents`);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

/**
 * Check backend API health status.
 * Source: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE}/api/health`);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}
