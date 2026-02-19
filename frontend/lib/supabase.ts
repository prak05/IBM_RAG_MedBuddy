// ============================================================================
// lib/supabase.ts — Supabase Client for Frontend (Auth + Realtime)
// Creates a browser-side Supabase client using the public anon key.
// Used for authentication and real-time subscriptions (NOT for direct DB access).
// Source: https://supabase.com/docs/guides/getting-started/quickstarts/nextjs
// Source: https://supabase.com/docs/reference/javascript/introduction
// ============================================================================

import { createClient } from "@supabase/supabase-js"; // Supabase JS SDK — Source: https://github.com/supabase/supabase-js

// Supabase project URL from environment variables
// Source: https://supabase.com/docs/guides/getting-started/quickstarts/nextjs
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://placeholder.supabase.co";

// Supabase anonymous key (safe for browser — enforces RLS policies)
// Source: https://supabase.com/docs/guides/api/api-keys#the-anon-key
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "placeholder-key";

// Create and export the Supabase client for browser-side use
// Uses placeholder values during build time to prevent prerender errors
// Source: https://supabase.com/docs/reference/javascript/initializing
export const supabase = createClient(supabaseUrl, supabaseAnonKey);
