// ============================================================================
// app/auth/signup/page.tsx — Registration Page for MedBuddy
// New user registration using Supabase Auth.
// Source: https://nextjs.org/docs/app/building-your-application/routing/pages-and-layouts
// Source: https://supabase.com/docs/guides/auth/auth-email-passwordless
// ============================================================================

"use client"; // Mark as Client Component for interactivity — Source: https://nextjs.org/docs/app/building-your-application/rendering/client-components

import { useState } from "react"; // React hooks — Source: https://react.dev/reference/react
import { supabase } from "@/lib/supabase"; // Supabase client — Source: ./lib/supabase.ts
import Link from "next/link"; // Next.js client-side navigation — Source: https://nextjs.org/docs/app/api-reference/components/link

/**
 * Signup page component — new user registration.
 * Uses Supabase Auth for secure account creation.
 * Source: https://supabase.com/docs/reference/javascript/auth-signup
 */
export default function SignupPage() {
  // State for full name input
  // Source: https://react.dev/reference/react/useState
  const [fullName, setFullName] = useState("");

  // State for email input
  const [email, setEmail] = useState("");

  // State for password input
  const [password, setPassword] = useState("");

  // State for confirm password input
  const [confirmPassword, setConfirmPassword] = useState("");

  // State for loading indicator
  const [isLoading, setIsLoading] = useState(false);

  // State for error messages
  const [error, setError] = useState<string | null>(null);

  // State for success (email confirmation sent)
  const [success, setSuccess] = useState(false);

  /**
   * Handle signup form submission.
   * Source: https://supabase.com/docs/reference/javascript/auth-signup
   */
  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();     // Prevent default form submission
    setError(null);         // Clear previous errors

    // Validate password match
    if (password !== confirmPassword) {
      setError("Passwords do not match"); // Show mismatch error
      return;
    }

    // Validate password length
    if (password.length < 6) {
      setError("Password must be at least 6 characters"); // Show length error
      return;
    }

    setIsLoading(true); // Show loading state

    try {
      // Create new user with Supabase Auth
      // Source: https://supabase.com/docs/reference/javascript/auth-signup
      const { error: authError } = await supabase.auth.signUp({
        email,                              // User's email address
        password,                           // User's chosen password
        options: {
          data: {
            full_name: fullName,            // Store full name in user metadata
          },
        },
      });

      // Handle authentication errors
      if (authError) {
        setError(authError.message); // Display Supabase error message
        return;
      }

      // Registration successful
      setSuccess(true);
    } catch (err) {
      // Handle unexpected errors
      setError(err instanceof Error ? err.message : "Registration failed. Please try again.");
    } finally {
      setIsLoading(false); // Hide loading state
    }
  };

  return (
    // Signup page layout — centered card
    <div className="min-h-screen flex items-center justify-center p-4">
      {/* Background gradient orbs for visual depth */}
      <div className="absolute top-20 -left-40 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-20 -right-40 w-96 h-96 bg-medical-500/10 rounded-full blur-3xl"></div>

      {/* Signup Card */}
      <div className="w-full max-w-md relative z-10">
        {/* App branding */}
        <div className="text-center mb-8">
          {/* Logo */}
          <div className="w-14 h-14 mx-auto bg-gradient-to-br from-primary-500 to-medical-500 rounded-2xl flex items-center justify-center text-white font-bold text-2xl shadow-lg shadow-primary-500/25 mb-4">
            M
          </div>
          <h1 className="text-2xl font-bold text-white">Create an account</h1>
          <p className="text-slate-500 mt-1">Join MedBuddy for AI-powered medical insights</p>
        </div>

        {/* Success state — email confirmation sent */}
        {success ? (
          <div className="glass-card p-8 text-center">
            {/* Success icon */}
            <div className="w-16 h-16 mx-auto mb-4 bg-medical-500/10 rounded-2xl flex items-center justify-center">
              <svg className="w-8 h-8 text-medical-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Check your email</h3>
            <p className="text-slate-400 text-sm mb-6">
              We sent a confirmation link to <span className="text-white font-medium">{email}</span>.
              Click the link to activate your account.
            </p>
            <Link
              href="/auth/login"
              className="inline-flex items-center px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-medium text-sm transition-all"
            >
              Back to Login
            </Link>
          </div>
        ) : (
          /* Registration Form */
          <form onSubmit={handleSignup} className="glass-card p-8 space-y-5">
            {/* Error alert */}
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-3 flex items-center gap-2">
                <svg className="w-4 h-4 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-sm text-red-300">{error}</p>
              </div>
            )}

            {/* Full name field */}
            <div>
              <label htmlFor="fullName" className="block text-sm font-medium text-slate-300 mb-1.5">
                Full Name
              </label>
              <input
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)} // Update name state
                placeholder="Dr. Jane Smith"
                required                                       // HTML5 required validation
                autoComplete="name"                            // Browser autofill hint
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
              />
            </div>

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
                placeholder="Minimum 6 characters"
                required                                       // HTML5 required validation
                autoComplete="new-password"                    // Browser autofill hint
                minLength={6}                                  // Minimum password length
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
              />
            </div>

            {/* Confirm password field */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-300 mb-1.5">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)} // Update confirm password
                placeholder="Re-enter your password"
                required                                              // HTML5 required validation
                autoComplete="new-password"                           // Browser autofill hint
                minLength={6}                                         // Minimum password length
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
              />
            </div>

            {/* Submit button */}
            <button
              type="submit"
              disabled={isLoading || !email || !password || !confirmPassword || !fullName}
              className="w-full py-3 bg-medical-600 hover:bg-medical-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-xl font-medium text-sm transition-all duration-200 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  {/* Loading spinner */}
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Creating account...
                </>
              ) : (
                "Create Account"
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

            {/* Login link */}
            <p className="text-center text-sm text-slate-500">
              Already have an account?{" "}
              <Link href="/auth/login" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
                Sign in
              </Link>
            </p>
          </form>
        )}

        {/* Disclaimer */}
        <p className="text-center text-[10px] text-slate-600 mt-4">
          By creating an account, you agree that MedBuddy is for educational purposes only.
        </p>
      </div>
    </div>
  );
}
