// ============================================================================
// app/page.tsx — Landing / Hero Page for MedBuddy
// The first page users see — showcases features and directs to the chat.
// Source: https://nextjs.org/docs/app/building-your-application/routing/pages-and-layouts
// ============================================================================

import Link from "next/link"; // Next.js client-side navigation — Source: https://nextjs.org/docs/app/api-reference/components/link

/**
 * Landing page component — the MedBuddy hero page.
 * Displays the app's value proposition and key features.
 * Source: https://nextjs.org/docs/app/building-your-application/routing/pages-and-layouts
 */
export default function HomePage() {
  return (
    // Full-height container with centered content
    <div className="min-h-screen flex flex-col items-center justify-center p-8 relative overflow-hidden">
      {/* Background gradient orbs for visual depth */}
      {/* Source: https://tailwindcss.com/docs/gradient-color-stops */}
      <div className="absolute top-20 -left-40 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-20 -right-40 w-96 h-96 bg-medical-500/10 rounded-full blur-3xl"></div>

      {/* Hero Content */}
      <div className="text-center max-w-4xl mx-auto relative z-10">
        {/* UST Sight 3.0 Competition Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-500/10 border border-primary-500/20 rounded-full text-primary-400 text-sm font-medium mb-8">
          <div className="w-2 h-2 rounded-full bg-medical-500 animate-pulse"></div>
          UST Sight 3.0 Competition Entry
        </div>

        {/* Main Title with gradient text */}
        <h1 className="text-6xl md:text-7xl font-bold tracking-tight mb-6">
          <span className="gradient-text">MedBuddy</span>
          <br />
          <span className="text-slate-400 text-3xl md:text-4xl font-medium">
            AI-Powered Medical Assistant
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-slate-400 text-lg md:text-xl max-w-2xl mx-auto mb-12 leading-relaxed">
          Hallucination-free medical Q&A grounded in{" "}
          <span className="text-primary-400 font-semibold">PubMed research</span> and your documents.
          Powered by{" "}
          <span className="text-white font-semibold">IBM Watsonx Granite</span> +{" "}
          <span className="text-medical-400 font-semibold">EPFL Meditron</span>.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-wrap justify-center gap-4 mb-16">
          {/* Primary CTA — Start Chatting */}
          <Link href="/chat" className="btn-medical text-lg px-8 py-4">
            Start Medical Chat
            <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>

          {/* Secondary CTA — Upload Documents */}
          <Link href="/upload" className="inline-flex items-center px-8 py-4 border border-slate-700 text-slate-300 hover:text-white hover:border-slate-500 rounded-xl font-medium transition-all duration-200 text-lg">
            Upload Documents
            <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </Link>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {/* Feature 1: Hybrid AI */}
          <div className="glass-card p-6 text-left">
            <div className="w-12 h-12 bg-primary-500/10 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-white font-semibold text-lg mb-2">Hybrid AI Models</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Dual LLM architecture: IBM Granite for reliability + EPFL Meditron for deep medical expertise.
            </p>
          </div>

          {/* Feature 2: Multi-Modal Input */}
          <div className="glass-card p-6 text-left">
            <div className="w-12 h-12 bg-medical-500/10 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-medical-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-white font-semibold text-lg mb-2">Multi-Modal Input</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Upload PDFs, text files, Markdown, and even handwritten notes — powered by Microsoft TrOCR.
            </p>
          </div>

          {/* Feature 3: PubMed Knowledge */}
          <div className="glass-card p-6 text-left">
            <div className="w-12 h-12 bg-amber-500/10 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h3 className="text-white font-semibold text-lg mb-2">PubMed Knowledge Base</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Grounded in 10,000+ peer-reviewed medical abstracts from PubMed with verifiable citations.
            </p>
          </div>
        </div>

        {/* Tech Stack Badges */}
        <div className="mt-16 flex flex-wrap justify-center gap-3">
          {["IBM Watsonx", "Meditron-7B", "PubMedBERT", "Supabase pgvector", "Next.js", "FastAPI", "TrOCR"].map((tech) => (
            <span key={tech} className="px-3 py-1.5 bg-slate-800/50 border border-slate-700/50 rounded-lg text-slate-400 text-xs font-medium">
              {tech}
            </span>
          ))}
        </div>

        {/* Credits */}
        <p className="mt-8 text-slate-600 text-xs">
          Built by Prakhar Sharma & Adithya Baiju | RIET | KTU S6 CSD 334
        </p>
      </div>
    </div>
  );
}
