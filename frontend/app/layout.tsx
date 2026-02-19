// ============================================================================
// app/layout.tsx — Root Layout for MedBuddy Frontend
// Wraps all pages with global styles, fonts, metadata, and the sidebar navigation.
// This is the entry point for the Next.js App Router.
// Source: https://nextjs.org/docs/app/building-your-application/routing/layouts-and-templates
// ============================================================================

import type { Metadata } from "next"; // Next.js metadata type for SEO — Source: https://nextjs.org/docs/app/api-reference/functions/generate-metadata
import "./globals.css"; // Import global Tailwind CSS styles — Source: ./globals.css

// SEO metadata for the application — appears in browser tab and search results
// Source: https://nextjs.org/docs/app/building-your-application/optimizing/metadata
export const metadata: Metadata = {
  title: "MedBuddy | AI Medical Assistant — Powered by IBM Watsonx",  // Browser tab title
  description: "Hallucination-free medical Q&A powered by IBM Watsonx Granite + Meditron with RAG. UST Sight 3.0 Competition Entry.",  // Meta description for SEO
};

/**
 * Root layout component — wraps every page in the application.
 * Provides the HTML structure, global fonts, and sidebar navigation.
 * Source: https://nextjs.org/docs/app/building-your-application/routing/layouts-and-templates
 */
export default function RootLayout({
  children, // Page content rendered inside the layout — Source: https://nextjs.org/docs/app/building-your-application/routing/layouts-and-templates#layouts
}: {
  children: React.ReactNode; // React node type for children — Source: https://react.dev/reference/react/ReactNode
}) {
  return (
    // HTML root element with language attribute for accessibility
    // Source: https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/lang
    <html lang="en" className="dark">
      {/* Body with dark mode background and smooth font rendering */}
      <body className="min-h-screen bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-50 antialiased">
        {/* Main application wrapper with sidebar + content layout */}
        <div className="flex h-screen overflow-hidden">
          {/* Sidebar Navigation — fixed left panel */}
          {/* Source: https://tailwindcss.com/docs/width */}
          <aside className="hidden md:flex w-72 flex-col bg-sidebar border-r border-slate-800">
            {/* Sidebar Header — App branding */}
            <div className="p-6 border-b border-slate-800">
              {/* App logo and title */}
              <div className="flex items-center gap-3">
                {/* Medical cross icon — Source: Unicode medical symbol */}
                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-medical-500 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-primary-500/25">
                  M
                </div>
                {/* App name and subtitle */}
                <div>
                  <h1 className="text-white font-bold text-lg tracking-tight">MedBuddy</h1>
                  <p className="text-slate-500 text-xs">AI Medical Assistant</p>
                </div>
              </div>
            </div>

            {/* Navigation Links */}
            <nav className="flex-1 p-4 space-y-1">
              {/* Chat link — main feature */}
              <a href="/chat" className="nav-link group">
                {/* Chat bubble SVG icon */}
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <span className="font-medium">Chat</span>
                {/* "New" badge for visual appeal */}
                <span className="ml-auto text-[10px] px-2 py-0.5 rounded-full bg-primary-500/20 text-primary-400 font-medium">AI</span>
              </a>

              {/* Upload link — document ingestion */}
              <a href="/upload" className="nav-link group">
                {/* Upload SVG icon */}
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span className="font-medium">Upload</span>
              </a>

              {/* Knowledge Base link — browse indexed documents */}
              <a href="/knowledge" className="nav-link group">
                {/* Database SVG icon */}
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                </svg>
                <span className="font-medium">Knowledge Base</span>
              </a>
            </nav>

            {/* Sidebar Footer — Branding and version */}
            <div className="p-4 border-t border-slate-800">
              <div className="flex items-center gap-2 text-slate-500 text-xs">
                {/* IBM Watsonx badge */}
                <div className="w-2 h-2 rounded-full bg-medical-500 animate-pulse"></div>
                <span>Powered by IBM Watsonx + Meditron</span>
              </div>
              <p className="text-slate-600 text-[10px] mt-1">UST Sight 3.0 | v2.0.0</p>
            </div>
          </aside>

          {/* Main Content Area — renders the current page */}
          <main className="flex-1 overflow-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
