// ============================================================================
// app/auth/login/page.tsx — Login Page for MedBuddy
// Email/password authentication using Supabase Auth.
// Source: https://nextjs.org/docs/app/building-your-application/routing/pages-and-layouts
// Source: https://supabase.com/docs/guides/auth/auth-email-passwordless
// ============================================================================

"use client"; // Mark as Client Component for interactivity — Source: https://nextjs.org/docs/app/building-your-application/rendering/client-components

import { useState } from "react"; // React hooks — Source: https://react.dev/reference/react
import { supabase } from "@/lib/supabase"; // Supabase client — Source: ./lib/supabase.ts
import Link from "next/link"; // Next.js client-side navigation — Source: https://nextjs.org/docs/app/api-reference/components/link

/**
 * Login page component — email/password authentication.
 * Uses Supabase Auth for secure login.
 * Source: https://supabase.com/docs/reference/javascript/auth-signinwithpassword
 */
export default function LoginPage() {
  // State for email input
  // Source: https://react.dev/reference/react/useState
  const [email, setEmail] = useState("");

  // State for password input
  const [password, setPassword] = useState("");

  // State for loading indicator
  const [isLoading, setIsLoading] = useState(false);

  // State for error messages
  const [error, setError] = useState<string | null>(null);

  // State for success message
  const [success, setSuccess] = useState(false);

  /**
   * Handle login form submission.
   * Source: https://supabase.com/docs/reference/javascript/auth-signinwithpassword
   */
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();     // Prevent default form submission
    setIsLoading(true);     // Show loading state
    setError(null);         // Clear previous errors

    try {
      // Attempt login with Supabase Auth
      // Source: https://supabase.com/docs/reference/javascript/auth-signinwithpassword
      const { error: authError } = await supabase.auth.signInWithPassword({
        email,      // User's email address
        password,   // User's password
      });

      // Handle authentication errors
      if (authError) {
        setError(authError.message); // Display Supabase error message
        return;
      }

      // Login successful — redirect to chat
      setSuccess(true);
      window.location.href = "/chat"; // Navigate to chat page
    } catch (err) {
      // Handle unexpected errors
      setError(err instanceof Error ? err.message : "Login failed. Please try again.");
    } finally {
      setIsLoading(false); // Hide loading state
    }
  };

  return (
    // Login page layout — centered card
    <div className="min-h-screen flex items-center justify-center p-4">
      {/* Background gradient orbs for visual depth */}
      <div className="absolute top-20 -left-40 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-20 -right-40 w-96 h-96 bg-medical-500/10 rounded-full blur-3xl"></div>

      {/* Login Card */}
      <div className="w-full max-w-md relative z-10">
        {/* App branding */}
        <div className="text-center mb-8">
          {/* Logo */}
          <div className="w-14 h-14 mx-auto bg-gradient-to-br from-primary-500 to-medical-500 rounded-2xl flex items-center justify-center text-white font-bold text-2xl shadow-lg shadow-primary-500/25 mb-4">
            M
          </div>
          <h1 className="text-2xl font-bold text-white">Welcome back</h1>
          <p className="text-slate-500 mt-1">Sign in to your MedBuddy account</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin} className="glass-card p-8 space-y-5">
          {/* Error alert */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-3 flex items-center gap-2">
              <svg className="w-4 h-4 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          {/* Success alert */}
          {success && (
            <div className="bg-medical-500/10 border border-medical-500/20 rounded-xl p-3 flex items-center gap-2">
              <svg className="w-4 h-4 text-medical-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <p className="text-sm text-medical-300">Login successful! Redirecting...</p>
            </div>
          )}

          {/* Email field */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-1.5">
              Email address
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}  // Update email state
              placeholder="doctor@hospital.com"
              required                                     // HTML5 required validation
              autoComplete="email"                         // Browser autofill hint
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
            />
          </div>

          {/* Password field */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-1.5">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)} // Update password state
              placeholder="Enter your password"
              required                                       // HTML5 required validation
              autoComplete="current-password"                // Browser autofill hint
              minLength={6}                                  // Minimum password length
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
            />
          </div>

          {/* Submit button */}
          <button
            type="submit"
            disabled={isLoading || !email || !password} // Disable when loading or empty fields
            className="w-full py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-xl font-medium text-sm transition-all duration-200 flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                {/* Loading spinner */}
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Signing in...
              </>
            ) : (
              "Sign In"
            )}
          </button>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-800"></div>
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-2 bg-slate-900 text-slate-500">or</span>
            </div>
          </div>

          {/* Sign up link */}
          <p className="text-center text-sm text-slate-500">
            Don&apos;t have an account?{" "}
            <Link href="/auth/signup" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
              Create one
            </Link>
          </p>
        </form>

        {/* Skip auth link — for demo/development */}
        <p className="text-center text-xs text-slate-600 mt-4">
          <Link href="/chat" className="hover:text-slate-400 transition-colors">
            Skip login and go to chat →
          </Link>
        </p>
      </div>
    </div>
  );
}
