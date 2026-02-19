// ============================================================================
// app/upload/page.tsx — Document Upload Page for MedBuddy
// Supports drag-and-drop upload for PDF, TXT, MD, and images (JPG/JPEG/PNG).
// Includes OCR preview for handwritten/image uploads.
// Source: https://nextjs.org/docs/app/building-your-application/routing/pages-and-layouts
// ============================================================================

"use client"; // Mark as Client Component for interactivity — Source: https://nextjs.org/docs/app/building-your-application/rendering/client-components

import { useState, useCallback } from "react"; // React hooks — Source: https://react.dev/reference/react
import { uploadFile, type UploadResponse } from "@/lib/api"; // API upload function — Source: ./lib/api.ts

/** Accepted file types for upload */
// Source: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/file#accept
const ACCEPTED_TYPES: Record<string, string> = {
  "application/pdf": "PDF",            // PDF documents
  "text/plain": "TXT",                 // Plain text files
  "text/markdown": "MD",               // Markdown files
  "image/jpeg": "JPG",                 // JPEG images
  "image/png": "PNG",                  // PNG images
};

/** Accepted file extensions for validation */
const ACCEPTED_EXTENSIONS = [".pdf", ".txt", ".md", ".jpg", ".jpeg", ".png"]; // Supported file types

/** Maximum file size in bytes (50MB) */
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB limit — Source: backend/routers/upload.py

/** Interface for tracking upload state */
interface UploadState {
  file: File;              // The file being uploaded
  status: "pending" | "uploading" | "success" | "error"; // Current upload status
  progress: number;        // Upload progress percentage (0-100)
  response?: UploadResponse; // Server response on success
  error?: string;          // Error message on failure
}

/**
 * Upload page component — drag-and-drop document upload interface.
 * Handles file selection, validation, upload, and OCR preview display.
 * Source: https://react.dev/reference/react/useState
 */
export default function UploadPage() {
  // State for files being uploaded
  // Source: https://react.dev/reference/react/useState
  const [uploads, setUploads] = useState<UploadState[]>([]);

  // State for drag-over visual feedback
  const [isDragOver, setIsDragOver] = useState(false);

  // State for OCR preview text (shown for image uploads)
  const [ocrPreview, setOcrPreview] = useState<string | null>(null);

  /**
   * Validate a file before upload.
   * Checks file type and size constraints.
   */
  const validateFile = (file: File): string | null => {
    // Check file extension against accepted list
    const extension = "." + file.name.split(".").pop()?.toLowerCase(); // Extract file extension
    if (!ACCEPTED_EXTENSIONS.includes(extension)) {
      return `Unsupported file type: ${extension}. Accepted: ${ACCEPTED_EXTENSIONS.join(", ")}`; // Return error for invalid type
    }

    // Check file size against maximum
    if (file.size > MAX_FILE_SIZE) {
      return `File too large: ${(file.size / 1024 / 1024).toFixed(1)}MB. Maximum: 50MB`; // Return error for oversized file
    }

    return null; // No validation errors
  };

  /**
   * Process selected files — validate and add to upload queue.
   * Source: https://react.dev/reference/react/useCallback
   */
  const processFiles = useCallback((files: FileList | File[]) => {
    const fileArray = Array.from(files); // Convert FileList to array for iteration

    // Validate each file and create upload states
    const newUploads: UploadState[] = fileArray
      .map((file) => {
        const error = validateFile(file); // Run validation checks
        return {
          file,                                              // The file object
          status: error ? "error" as const : "pending" as const, // Set initial status
          progress: 0,                                       // Start at 0% progress
          error: error || undefined,                         // Attach validation error if any
        };
      });

    // Add new uploads to existing list
    setUploads((prev) => [...prev, ...newUploads]);

    // Auto-start uploading valid files
    newUploads
      .filter((u) => u.status === "pending") // Only upload valid files
      .forEach((u) => handleUpload(u.file)); // Start each upload
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  /**
   * Handle individual file upload to the backend.
   * Source: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
   */
  const handleUpload = async (file: File) => {
    // Update status to uploading
    setUploads((prev) =>
      prev.map((u) =>
        u.file === file ? { ...u, status: "uploading" as const, progress: 30 } : u // Set to 30% while in transit
      )
    );

    try {
      // Send file to backend API
      // Source: ./lib/api.ts — uploadFile function
      const response = await uploadFile(file);

      // Update status to success with response data
      setUploads((prev) =>
        prev.map((u) =>
          u.file === file
            ? { ...u, status: "success" as const, progress: 100, response } // Complete upload
            : u
        )
      );

      // If OCR text was returned (image uploads), show preview
      if (response.ocr_text) {
        setOcrPreview(response.ocr_text); // Display extracted text
      }
    } catch (error) {
      // Update status to error with message
      setUploads((prev) =>
        prev.map((u) =>
          u.file === file
            ? {
                ...u,
                status: "error" as const,
                progress: 0,
                error: error instanceof Error ? error.message : "Upload failed", // Capture error message
              }
            : u
        )
      );
    }
  };

  /**
   * Handle drag-over event for visual feedback.
   * Source: https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/dragover_event
   */
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();      // Prevent default browser behavior
    e.stopPropagation();     // Stop event bubbling
    setIsDragOver(true);     // Show drag-over visual state
  }, []);

  /**
   * Handle drag-leave event to remove visual feedback.
   * Source: https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/dragleave_event
   */
  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();      // Prevent default browser behavior
    e.stopPropagation();     // Stop event bubbling
    setIsDragOver(false);    // Remove drag-over visual state
  }, []);

  /**
   * Handle file drop event.
   * Source: https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/drop_event
   */
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();      // Prevent default browser behavior
      e.stopPropagation();     // Stop event bubbling
      setIsDragOver(false);    // Remove drag-over visual state

      const files = e.dataTransfer.files; // Get dropped files
      if (files.length > 0) {
        processFiles(files);   // Process the dropped files
      }
    },
    [processFiles] // Re-create when processFiles changes
  );

  /**
   * Handle file input change (click-to-select).
   * Source: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/file
   */
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files; // Get selected files
    if (files && files.length > 0) {
      processFiles(files);       // Process selected files
    }
    e.target.value = "";         // Reset input to allow re-selecting same file
  };

  /**
   * Get icon and color for a file type.
   */
  const getFileTypeInfo = (filename: string) => {
    const ext = filename.split(".").pop()?.toLowerCase(); // Extract extension
    switch (ext) {
      case "pdf":
        return { icon: "PDF", color: "text-red-400 bg-red-500/10" };      // Red for PDFs
      case "txt":
        return { icon: "TXT", color: "text-blue-400 bg-blue-500/10" };    // Blue for text
      case "md":
        return { icon: "MD", color: "text-purple-400 bg-purple-500/10" }; // Purple for markdown
      case "jpg":
      case "jpeg":
      case "png":
        return { icon: "IMG", color: "text-green-400 bg-green-500/10" };  // Green for images
      default:
        return { icon: "FILE", color: "text-slate-400 bg-slate-500/10" }; // Default gray
    }
  };

  /**
   * Remove an upload from the list.
   */
  const removeUpload = (index: number) => {
    setUploads((prev) => prev.filter((_, i) => i !== index)); // Filter out by index
  };

  /**
   * Clear all completed uploads.
   */
  const clearCompleted = () => {
    setUploads((prev) => prev.filter((u) => u.status !== "success" && u.status !== "error")); // Keep only pending/uploading
  };

  return (
    // Upload page layout — full height flex column
    <div className="flex flex-col h-screen">
      {/* Page Header */}
      <header className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-950/50 backdrop-blur-lg">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">Upload Documents</h2>
          <p className="text-sm text-slate-500">Add medical documents, research papers, or handwritten notes to your knowledge base</p>
        </div>
      </header>

      {/* Main Content Area — scrollable */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Drag-and-Drop Upload Zone */}
          {/* Source: https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API */}
          <div
            onDragOver={handleDragOver}       // Handle drag over
            onDragLeave={handleDragLeave}     // Handle drag leave
            onDrop={handleDrop}               // Handle file drop
            className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
              isDragOver
                ? "border-primary-500 bg-primary-500/5 scale-[1.02]"   // Active drag state
                : "border-slate-700 hover:border-slate-600 bg-slate-900/30" // Default state
            }`}
          >
            {/* Upload icon */}
            <div className="w-16 h-16 mx-auto mb-6 bg-gradient-to-br from-primary-500/10 to-medical-500/10 rounded-2xl flex items-center justify-center">
              <svg className="w-8 h-8 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>

            {/* Instructions text */}
            <h3 className="text-lg font-semibold text-slate-300 mb-2">
              {isDragOver ? "Drop files here..." : "Drag & Drop files here"}
            </h3>
            <p className="text-slate-500 mb-4">or click to browse</p>

            {/* Hidden file input */}
            {/* Source: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/file */}
            <input
              type="file"
              multiple                                    // Allow multiple file selection
              accept={ACCEPTED_EXTENSIONS.join(",")}      // Restrict to accepted types
              onChange={handleFileSelect}                  // Handle file selection
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" // Invisible overlay
            />

            {/* Accepted formats badges */}
            <div className="flex flex-wrap justify-center gap-2 mt-4">
              {Object.values(ACCEPTED_TYPES).map((type) => (
                <span
                  key={type}
                  className="px-3 py-1 bg-slate-800/50 border border-slate-700/50 rounded-lg text-slate-400 text-xs font-medium"
                >
                  {type}
                </span>
              ))}
            </div>

            {/* Max size notice */}
            <p className="text-slate-600 text-xs mt-3">Maximum file size: 50MB</p>
          </div>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-3 gap-4">
            {/* PDF Processing Card */}
            <div className="glass-card p-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-red-500/10 rounded-xl flex items-center justify-center">
                  <span className="text-red-400 font-bold text-sm">PDF</span>
                </div>
                <h4 className="text-white font-medium">PDF Documents</h4>
              </div>
              <p className="text-slate-500 text-sm">
                Research papers, textbooks, and medical reports — extracted page by page.
              </p>
            </div>

            {/* Text/Markdown Card */}
            <div className="glass-card p-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-blue-500/10 rounded-xl flex items-center justify-center">
                  <span className="text-blue-400 font-bold text-sm">TXT</span>
                </div>
                <h4 className="text-white font-medium">Text & Markdown</h4>
              </div>
              <p className="text-slate-500 text-sm">
                Clinical notes, study guides, and formatted medical documentation.
              </p>
            </div>

            {/* Image/OCR Card */}
            <div className="glass-card p-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-green-500/10 rounded-xl flex items-center justify-center">
                  <span className="text-green-400 font-bold text-sm">IMG</span>
                </div>
                <h4 className="text-white font-medium">Images & Handwriting</h4>
              </div>
              <p className="text-slate-500 text-sm">
                Handwritten notes and prescriptions — powered by Microsoft TrOCR.
              </p>
            </div>
          </div>

          {/* Upload List — shows all uploads with status */}
          {uploads.length > 0 && (
            <div className="space-y-3">
              {/* Header with clear button */}
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-300">
                  Uploads ({uploads.length})
                </h3>
                {/* Show clear button when there are completed uploads */}
                {uploads.some((u) => u.status === "success" || u.status === "error") && (
                  <button
                    onClick={clearCompleted}
                    className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
                  >
                    Clear completed
                  </button>
                )}
              </div>

              {/* Upload items */}
              {uploads.map((upload, index) => {
                const fileInfo = getFileTypeInfo(upload.file.name); // Get file type styling
                return (
                  <div
                    key={`${upload.file.name}-${index}`}
                    className="glass-card p-4 flex items-center gap-4"
                  >
                    {/* File type badge */}
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-xs ${fileInfo.color}`}>
                      {fileInfo.icon}
                    </div>

                    {/* File info and progress */}
                    <div className="flex-1 min-w-0">
                      {/* Filename (truncated) */}
                      <p className="text-sm font-medium text-white truncate">
                        {upload.file.name}
                      </p>
                      {/* File size */}
                      <p className="text-xs text-slate-500">
                        {(upload.file.size / 1024).toFixed(1)} KB
                      </p>

                      {/* Progress bar (shown during upload) */}
                      {upload.status === "uploading" && (
                        <div className="mt-2 w-full bg-slate-800 rounded-full h-1.5">
                          <div
                            className="bg-primary-500 h-1.5 rounded-full transition-all duration-500 animate-pulse"
                            style={{ width: `${upload.progress}%` }}  // Dynamic width based on progress
                          ></div>
                        </div>
                      )}

                      {/* Success info — chunk count */}
                      {upload.status === "success" && upload.response && (
                        <p className="text-xs text-medical-400 mt-1">
                          {upload.response.chunk_count} chunks indexed
                          {upload.response.ocr_text && " • OCR extracted"} {/* Show OCR indicator */}
                        </p>
                      )}

                      {/* Error message */}
                      {upload.status === "error" && upload.error && (
                        <p className="text-xs text-red-400 mt-1">{upload.error}</p>
                      )}
                    </div>

                    {/* Status indicator */}
                    <div className="flex-shrink-0">
                      {/* Uploading spinner */}
                      {upload.status === "uploading" && (
                        <div className="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
                      )}
                      {/* Success checkmark */}
                      {upload.status === "success" && (
                        <div className="w-6 h-6 bg-medical-500/20 rounded-full flex items-center justify-center">
                          <svg className="w-4 h-4 text-medical-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      )}
                      {/* Error X icon */}
                      {upload.status === "error" && (
                        <button
                          onClick={() => removeUpload(index)}   // Remove this upload on click
                          className="w-6 h-6 bg-red-500/20 rounded-full flex items-center justify-center hover:bg-red-500/30 transition-colors"
                        >
                          <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* OCR Preview Panel — shown when image text is extracted */}
          {ocrPreview && (
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  {/* Eye icon for preview */}
                  <svg className="w-5 h-5 text-medical-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <h3 className="text-sm font-semibold text-white">OCR Extracted Text</h3>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-medical-500/20 text-medical-400 font-medium">
                    Microsoft TrOCR
                  </span>
                </div>
                {/* Close button */}
                <button
                  onClick={() => setOcrPreview(null)}    // Hide OCR preview
                  className="text-slate-500 hover:text-slate-300 transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              {/* OCR text content with preserved whitespace */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 max-h-60 overflow-y-auto">
                <p className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed font-mono">
                  {ocrPreview}
                </p>
              </div>
              <p className="text-[10px] text-slate-600 mt-2">
                This text has been extracted and indexed into your knowledge base for Q&A.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
