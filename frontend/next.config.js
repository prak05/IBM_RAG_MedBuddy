// ============================================================================
// next.config.js — Next.js Configuration for MedBuddy Frontend
// Source: https://nextjs.org/docs/app/api-reference/next-config-js
// ============================================================================

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable React strict mode for better development warnings
  // Source: https://nextjs.org/docs/app/api-reference/next-config-js/reactStrictMode
  reactStrictMode: true,

  // Configure environment variables available in the browser
  // Source: https://nextjs.org/docs/app/building-your-application/configuring/environment-variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000", // Backend API URL
  },
};

module.exports = nextConfig; // Export the configuration — Source: https://nextjs.org/docs/app/api-reference/next-config-js
