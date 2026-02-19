// ============================================================================
// app/chat/page.tsx — Main Chat Interface for MedBuddy
// The core feature: medical Q&A with streaming responses, citations, and
// model selection between IBM Granite and Meditron.
// Source: https://nextjs.org/docs/app/building-your-application/routing/pages-and-layouts
// ============================================================================

"use client"; // Mark as Client Component for interactivity — Source: https://nextjs.org/docs/app/building-your-application/rendering/client-components

import { useState, useRef, useEffect } from "react"; // React hooks — Source: https://react.dev/reference/react
import { sendChatMessage, type ChatResponse, type Citation } from "@/lib/api"; // API functions — Source: ./lib/api.ts

/** Message type for the chat history */
interface Message {
  id: string;          // Unique message ID
  role: "user" | "assistant"; // Who sent this message
  content: string;     // Message text content
  citations?: Citation[]; // Source citations (assistant only)
  model_used?: string; // Which LLM was used (assistant only)
  confidence?: string; // Confidence level (assistant only)
  timestamp: Date;     // When the message was sent
}

/**
 * Chat page component — the main medical Q&A interface.
 * Handles message input, API communication, and response display.
 * Source: https://react.dev/reference/react/useState
 */
export default function ChatPage() {
  // State for chat messages history
  // Source: https://react.dev/reference/react/useState
  const [messages, setMessages] = useState<Message[]>([]);

  // State for the current input text
  const [input, setInput] = useState("");

  // State for loading indicator during API calls
  const [isLoading, setIsLoading] = useState(false);

  // State for selected LLM model (granite or meditron)
  const [selectedModel, setSelectedModel] = useState<"granite" | "meditron">("granite");

  // State for expanded citation panels
  const [expandedCitation, setExpandedCitation] = useState<string | null>(null);

  // Ref for auto-scrolling to the latest message
  // Source: https://react.dev/reference/react/useRef
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  // Source: https://react.dev/reference/react/useEffect
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); // Smooth scroll to bottom
  }, [messages]); // Trigger on messages change

  /**
   * Handle sending a message to the backend.
   * Source: https://react.dev/learn/responding-to-events
   */
  const handleSend = async () => {
    // Don't send empty messages or while loading
    if (!input.trim() || isLoading) return;

    // Create the user message object
    const userMessage: Message = {
      id: `user-${Date.now()}`,  // Unique ID using timestamp
      role: "user",              // This is a user message
      content: input,            // The message text
      timestamp: new Date(),     // Current time
    };

    // Add user message to chat history and clear input
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input; // Save input before clearing
    setInput("");               // Clear the input field
    setIsLoading(true);         // Show loading indicator

    try {
      // Send the question to the backend API
      // Source: ./lib/api.ts
      const response: ChatResponse = await sendChatMessage({
        question: currentInput,    // The user's medical question
        model: selectedModel,      // granite or meditron
        top_k: 5,                  // Retrieve top 5 chunks
      });

      // Create the assistant message object with citations
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,  // Unique ID
        role: "assistant",               // This is an AI response
        content: response.answer,        // The generated answer
        citations: response.citations,   // Source citations
        model_used: response.model_used, // Which model was used
        confidence: response.confidence, // Confidence level
        timestamp: new Date(),           // Current time
      };

      // Add assistant message to chat history
      setMessages((prev) => [...prev, assistantMessage]);

    } catch (error) {
      // Handle API errors gracefully
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : "Unknown error"}. Please try again.`,
        confidence: "low",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false); // Hide loading indicator
    }
  };

  /**
   * Handle Enter key press to send message.
   * Source: https://react.dev/learn/responding-to-events
   */
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // Prevent newline
      handleSend();       // Send the message
    }
  };

  /**
   * Get the CSS class for a confidence badge.
   */
  const getConfidenceClass = (confidence: string) => {
    switch (confidence) {
      case "high": return "confidence-high";     // Green badge
      case "medium": return "confidence-medium"; // Amber badge
      case "low": return "confidence-low";       // Red badge
      default: return "confidence-medium";       // Default to medium
    }
  };

  return (
    // Chat page layout — full height flex column
    <div className="flex flex-col h-screen">
      {/* Chat Header */}
      <header className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-950/50 backdrop-blur-lg">
        <div className="flex items-center justify-between">
          {/* Page title */}
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Medical Chat</h2>
            <p className="text-sm text-slate-500">Ask questions grounded in your medical knowledge base</p>
          </div>

          {/* Model Selector Toggle */}
          <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 rounded-xl p-1">
            {/* Granite button */}
            <button
              onClick={() => setSelectedModel("granite")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedModel === "granite"
                  ? "bg-primary-600 text-white shadow-md"  // Active state
                  : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"  // Inactive state
              }`}
            >
              IBM Granite
            </button>
            {/* Meditron button */}
            <button
              onClick={() => setSelectedModel("meditron")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedModel === "meditron"
                  ? "bg-medical-600 text-white shadow-md"  // Active state (green)
                  : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"  // Inactive state
              }`}
            >
              Meditron
            </button>
          </div>
        </div>
      </header>

      {/* Messages Area — scrollable chat history */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
        {/* Empty state — shown when no messages */}
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            {/* Large medical icon */}
            <div className="w-20 h-20 bg-gradient-to-br from-primary-500/10 to-medical-500/10 rounded-2xl flex items-center justify-center mb-6">
              <svg className="w-10 h-10 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-slate-300 mb-2">Start a Medical Conversation</h3>
            <p className="text-slate-500 max-w-md">
              Ask any medical question. Your answers will be grounded in PubMed research and uploaded documents.
            </p>
            {/* Suggested Questions */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl">
              {[
                "What are the common causes of cardiac arrest in young adults?",
                "Explain the treatment protocol for acute stroke",
                "What are the side effects of SSRI medications?",
                "Describe the pathophysiology of type 2 diabetes",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => { setInput(suggestion); }} // Pre-fill the input with this suggestion
                  className="text-left p-4 bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 hover:border-slate-600 rounded-xl text-sm text-slate-400 hover:text-slate-300 transition-all duration-200"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Chat Messages */}
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex animate-fade-in ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div className={`max-w-[80%] ${message.role === "user" ? "" : ""}`}>
              {/* Message Bubble */}
              <div className={message.role === "user" ? "chat-bubble-user" : "chat-bubble-assistant"}>
                {/* Message content with preserved whitespace */}
                <div className="whitespace-pre-wrap">{message.content}</div>
              </div>

              {/* Metadata bar (assistant messages only) */}
              {message.role === "assistant" && (message.model_used || message.confidence) && (
                <div className="flex items-center gap-2 mt-2 px-1">
                  {/* Model badge */}
                  {message.model_used && (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-medium">
                      {message.model_used === "granite" ? "IBM Granite" : "Meditron"}
                    </span>
                  )}
                  {/* Confidence badge */}
                  {message.confidence && (
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${getConfidenceClass(message.confidence)}`}>
                      {message.confidence} confidence
                    </span>
                  )}
                </div>
              )}

              {/* Citations Panel (assistant messages with citations) */}
              {message.citations && message.citations.length > 0 && (
                <div className="mt-3 space-y-2">
                  {/* Citations toggle button */}
                  <button
                    onClick={() => setExpandedCitation(expandedCitation === message.id ? null : message.id)}
                    className="flex items-center gap-2 text-xs text-primary-400 hover:text-primary-300 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                    {message.citations.length} sources
                    <svg className={`w-3 h-3 transition-transform ${expandedCitation === message.id ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {/* Expanded citations list */}
                  {expandedCitation === message.id && (
                    <div className="space-y-2 animate-slide-up">
                      {message.citations.map((citation, idx) => (
                        <div key={idx} className="p-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-xs">
                          {/* Citation header with source info */}
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold text-primary-400">[Source {idx + 1}]</span>
                            <span className="text-slate-500">{citation.filename || citation.source}</span>
                            {/* PubMed link if available */}
                            {citation.pubmed_id && (
                              <a
                                href={`https://pubmed.ncbi.nlm.nih.gov/${citation.pubmed_id}/`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-medical-400 hover:text-medical-300 underline"
                              >
                                PubMed
                              </a>
                            )}
                            {/* Similarity score */}
                            <span className={`ml-auto px-1.5 py-0.5 rounded text-[10px] font-medium ${
                              citation.similarity >= 0.8 ? "confidence-high" :
                              citation.similarity >= 0.6 ? "confidence-medium" : "confidence-low"
                            }`}>
                              {(citation.similarity * 100).toFixed(0)}% match
                            </span>
                          </div>
                          {/* Citation content */}
                          <p className="text-slate-400 leading-relaxed">{citation.content}</p>
                          {/* Page number if available */}
                          {citation.page_num && (
                            <span className="text-slate-600 mt-1 block">Page {citation.page_num}</span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading Indicator — typing animation */}
        {isLoading && (
          <div className="flex justify-start animate-fade-in">
            <div className="chat-bubble-assistant flex items-center gap-1.5">
              <div className="typing-dot" style={{ animationDelay: "0ms" }}></div>
              <div className="typing-dot" style={{ animationDelay: "150ms" }}></div>
              <div className="typing-dot" style={{ animationDelay: "300ms" }}></div>
            </div>
          </div>
        )}

        {/* Auto-scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area — message input with send button */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-950/50 backdrop-blur-lg">
        <div className="max-w-4xl mx-auto flex items-end gap-3">
          {/* Text input field */}
          <div className="flex-1 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}  // Update input state
              onKeyDown={handleKeyDown}                    // Handle Enter to send
              placeholder="Ask a medical question..."      // Placeholder text
              rows={1}                                     // Single row by default
              className="w-full resize-none bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 pr-12 text-sm text-slate-900 dark:text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
              style={{ minHeight: "48px", maxHeight: "120px" }}  // Height constraints
            />
          </div>

          {/* Send Button */}
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}  // Disable when empty or loading
            className="flex-shrink-0 w-12 h-12 bg-primary-600 hover:bg-primary-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-xl flex items-center justify-center transition-all duration-200 shadow-lg shadow-primary-500/25 hover:shadow-xl"
          >
            {/* Send arrow icon */}
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19V5M5 12l7-7 7 7" />
            </svg>
          </button>
        </div>

        {/* Disclaimer */}
        <p className="text-center text-[10px] text-slate-500 mt-2">
          MedBuddy is for educational purposes only. Always consult a healthcare professional for medical advice.
        </p>
      </div>
    </div>
  );
}
