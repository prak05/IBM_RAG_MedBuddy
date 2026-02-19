// ============================================================================
// app/knowledge/page.tsx — Knowledge Base Browser for MedBuddy
// Browse indexed documents, view stats, and trigger PubMed ingestion.
// Source: https://nextjs.org/docs/app/building-your-application/routing/pages-and-layouts
// ============================================================================

"use client"; // Mark as Client Component for interactivity — Source: https://nextjs.org/docs/app/building-your-application/rendering/client-components

import { useState, useEffect } from "react"; // React hooks — Source: https://react.dev/reference/react
import {
  getKnowledgeStats,
  getDocuments,
  ingestPubMed,
  type KnowledgeStats,
  type DocumentInfo,
} from "@/lib/api"; // API functions — Source: ./lib/api.ts

/**
 * Knowledge base page component — browse and manage indexed documents.
 * Displays statistics, document list, and PubMed ingestion controls.
 * Source: https://react.dev/reference/react/useState
 */
export default function KnowledgePage() {
  // State for knowledge base statistics
  // Source: https://react.dev/reference/react/useState
  const [stats, setStats] = useState<KnowledgeStats | null>(null);

  // State for document list
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);

  // State for loading indicator
  const [isLoading, setIsLoading] = useState(true);

  // State for PubMed ingestion query
  const [pubmedQuery, setPubmedQuery] = useState("");

  // State for PubMed ingestion loading
  const [isIngesting, setIsIngesting] = useState(false);

  // State for ingestion result message
  const [ingestMessage, setIngestMessage] = useState<string | null>(null);

  // State for error messages
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch knowledge base data on component mount.
   * Source: https://react.dev/reference/react/useEffect
   */
  useEffect(() => {
    fetchData(); // Load initial data
  }, []); // Run once on mount

  /**
   * Fetch stats and documents from the backend.
   */
  const fetchData = async () => {
    setIsLoading(true);  // Show loading state
    setError(null);      // Clear previous errors

    try {
      // Fetch stats and documents in parallel for speed
      // Source: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all
      const [statsData, docsData] = await Promise.all([
        getKnowledgeStats(), // GET /api/knowledge/stats
        getDocuments(),      // GET /api/knowledge/documents
      ]);

      setStats(statsData);       // Update stats state
      setDocuments(docsData);    // Update documents state
    } catch (err) {
      // Handle fetch errors gracefully
      setError(err instanceof Error ? err.message : "Failed to load knowledge base data");
    } finally {
      setIsLoading(false); // Hide loading state
    }
  };

  /**
   * Handle PubMed ingestion request.
   * Source: https://react.dev/learn/responding-to-events
   */
  const handleIngest = async () => {
    if (!pubmedQuery.trim() || isIngesting) return; // Don't ingest empty queries

    setIsIngesting(true);    // Show ingestion loading
    setIngestMessage(null);  // Clear previous message
    setError(null);          // Clear previous errors

    try {
      // Trigger PubMed ingestion via API
      const result = await ingestPubMed(pubmedQuery.trim(), 100); // Ingest up to 100 articles
      setIngestMessage(
        `Successfully ingested ${result.articles_ingested || 0} PubMed articles for "${pubmedQuery}"`
      ); // Show success message
      setPubmedQuery("");    // Clear the input
      fetchData();           // Refresh the data to show new documents
    } catch (err) {
      setError(err instanceof Error ? err.message : "PubMed ingestion failed");
    } finally {
      setIsIngesting(false); // Hide ingestion loading
    }
  };

  /**
   * Handle Enter key press in PubMed query input.
   * Source: https://react.dev/learn/responding-to-events
   */
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault(); // Prevent form submission
      handleIngest();     // Trigger ingestion
    }
  };

  /**
   * Get icon styling for document source type.
   */
  const getSourceIcon = (source: string, fileType: string) => {
    if (source === "pubmed") {
      return { icon: "PM", color: "text-amber-400 bg-amber-500/10" }; // Amber for PubMed
    }
    switch (fileType) {
      case "pdf":
        return { icon: "PDF", color: "text-red-400 bg-red-500/10" };     // Red for PDFs
      case "txt":
        return { icon: "TXT", color: "text-blue-400 bg-blue-500/10" };   // Blue for text
      case "md":
        return { icon: "MD", color: "text-purple-400 bg-purple-500/10" }; // Purple for markdown
      case "image":
        return { icon: "IMG", color: "text-green-400 bg-green-500/10" }; // Green for images
      default:
        return { icon: "DOC", color: "text-slate-400 bg-slate-500/10" }; // Default gray
    }
  };

  /**
   * Format date string to human-readable format.
   * Source: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toLocaleDateString
   */
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return "Unknown date"; // Fallback for missing dates
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",     // Full year
      month: "short",      // Abbreviated month
      day: "numeric",      // Day of month
    });
  };

  return (
    // Knowledge base page layout — full height flex column
    <div className="flex flex-col h-screen">
      {/* Page Header */}
      <header className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-950/50 backdrop-blur-lg">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Knowledge Base</h2>
            <p className="text-sm text-slate-500">Browse indexed documents and PubMed abstracts</p>
          </div>
          {/* Refresh button */}
          <button
            onClick={fetchData}
            disabled={isLoading}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-300 rounded-xl text-sm font-medium transition-all"
          >
            {isLoading ? "Loading..." : "Refresh"}
          </button>
        </div>
      </header>

      {/* Main Content Area — scrollable */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-5xl mx-auto space-y-6">
          {/* Error Alert */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center gap-3">
              <svg className="w-5 h-5 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          {/* Success Message */}
          {ingestMessage && (
            <div className="bg-medical-500/10 border border-medical-500/20 rounded-xl p-4 flex items-center gap-3">
              <svg className="w-5 h-5 text-medical-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <p className="text-sm text-medical-300">{ingestMessage}</p>
            </div>
          )}

          {/* Statistics Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* Total Documents */}
            <div className="glass-card p-5">
              <p className="text-slate-500 text-xs font-medium uppercase tracking-wider mb-1">Documents</p>
              <p className="text-2xl font-bold text-white">
                {isLoading ? "..." : stats?.total_documents ?? 0}
              </p>
            </div>

            {/* Total Chunks */}
            <div className="glass-card p-5">
              <p className="text-slate-500 text-xs font-medium uppercase tracking-wider mb-1">Chunks</p>
              <p className="text-2xl font-bold text-white">
                {isLoading ? "..." : stats?.total_chunks?.toLocaleString() ?? 0}
              </p>
            </div>

            {/* PubMed Count */}
            <div className="glass-card p-5">
              <p className="text-slate-500 text-xs font-medium uppercase tracking-wider mb-1">PubMed</p>
              <p className="text-2xl font-bold text-amber-400">
                {isLoading ? "..." : stats?.pubmed_count ?? 0}
              </p>
            </div>

            {/* Upload Count */}
            <div className="glass-card p-5">
              <p className="text-slate-500 text-xs font-medium uppercase tracking-wider mb-1">Uploads</p>
              <p className="text-2xl font-bold text-primary-400">
                {isLoading ? "..." : stats?.upload_count ?? 0}
              </p>
            </div>
          </div>

          {/* PubMed Ingestion Section */}
          <div className="glass-card p-6">
            <div className="flex items-center gap-3 mb-4">
              {/* Book icon */}
              <div className="w-10 h-10 bg-amber-500/10 rounded-xl flex items-center justify-center">
                <svg className="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div>
                <h3 className="text-white font-semibold">PubMed Ingestion</h3>
                <p className="text-slate-500 text-sm">Import peer-reviewed medical abstracts from NCBI PubMed</p>
              </div>
            </div>

            {/* Ingestion input and button */}
            <div className="flex gap-3">
              <input
                type="text"
                value={pubmedQuery}
                onChange={(e) => setPubmedQuery(e.target.value)} // Update query state
                onKeyDown={handleKeyDown}                          // Handle Enter key
                placeholder="Enter medical topic (e.g., cardiac arrest, diabetes treatment)"
                disabled={isIngesting}
                className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 transition-all disabled:opacity-50"
              />
              <button
                onClick={handleIngest}
                disabled={!pubmedQuery.trim() || isIngesting}
                className="px-6 py-3 bg-amber-600 hover:bg-amber-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-xl font-medium text-sm transition-all duration-200 flex items-center gap-2"
              >
                {isIngesting ? (
                  <>
                    {/* Spinner icon during ingestion */}
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Ingesting...
                  </>
                ) : (
                  <>
                    {/* Download icon */}
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Ingest
                  </>
                )}
              </button>
            </div>

            {/* Suggested topics */}
            <div className="flex flex-wrap gap-2 mt-3">
              {["Cardiac arrest", "Type 2 diabetes", "Stroke treatment", "Drug interactions", "Cancer immunotherapy"].map(
                (topic) => (
                  <button
                    key={topic}
                    onClick={() => setPubmedQuery(topic)} // Pre-fill input with suggested topic
                    className="px-3 py-1 bg-slate-800/50 border border-slate-700/50 hover:border-amber-500/50 rounded-lg text-slate-400 hover:text-amber-400 text-xs font-medium transition-all"
                  >
                    {topic}
                  </button>
                )
              )}
            </div>
          </div>

          {/* Documents List */}
          <div>
            <h3 className="text-sm font-semibold text-slate-300 mb-3">
              Indexed Documents ({documents.length})
            </h3>

            {/* Loading state */}
            {isLoading && (
              <div className="text-center py-12">
                <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                <p className="text-slate-500 text-sm">Loading knowledge base...</p>
              </div>
            )}

            {/* Empty state */}
            {!isLoading && documents.length === 0 && (
              <div className="text-center py-12 glass-card">
                <div className="w-16 h-16 mx-auto mb-4 bg-slate-800/50 rounded-2xl flex items-center justify-center">
                  <svg className="w-8 h-8 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                  </svg>
                </div>
                <h4 className="text-slate-400 font-medium mb-1">No documents yet</h4>
                <p className="text-slate-600 text-sm">Upload documents or ingest PubMed abstracts to get started.</p>
              </div>
            )}

            {/* Document cards */}
            {!isLoading && documents.length > 0 && (
              <div className="space-y-2">
                {documents.map((doc) => {
                  const sourceInfo = getSourceIcon(doc.source, doc.file_type); // Get styling info
                  return (
                    <div
                      key={doc.id}
                      className="glass-card p-4 flex items-center gap-4 hover:border-slate-600 transition-all"
                    >
                      {/* Source type badge */}
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-xs flex-shrink-0 ${sourceInfo.color}`}>
                        {sourceInfo.icon}
                      </div>

                      {/* Document info */}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white truncate">
                          {doc.filename}
                        </p>
                        <div className="flex items-center gap-2 mt-0.5">
                          {/* Source badge */}
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-medium">
                            {doc.source}
                          </span>
                          {/* File type badge */}
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-medium">
                            {doc.file_type}
                          </span>
                          {/* PubMed link if available */}
                          {doc.pubmed_id && (
                            <a
                              href={`https://pubmed.ncbi.nlm.nih.gov/${doc.pubmed_id}/`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 font-medium hover:bg-amber-500/20 transition-colors"
                            >
                              PMID: {doc.pubmed_id}
                            </a>
                          )}
                        </div>
                      </div>

                      {/* Date */}
                      <p className="text-xs text-slate-500 flex-shrink-0">
                        {formatDate(doc.created_at)}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
