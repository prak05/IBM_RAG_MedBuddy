// ============================================================================
// tailwind.config.ts — Tailwind CSS Configuration with Medical Theme
// Defines the custom color palette, fonts, and animation extensions
// for MedBuddy's medical-grade UI design.
// Source: https://tailwindcss.com/docs/configuration
// ============================================================================

import type { Config } from "tailwindcss"; // Tailwind config type — Source: https://tailwindcss.com/docs/configuration#type-script

const config: Config = {
  // Enable dark mode via CSS class (toggled by theme-provider component)
  // Source: https://tailwindcss.com/docs/dark-mode#toggling-dark-mode-manually
  darkMode: ["class"],

  // Specify which files Tailwind should scan for class names
  // Source: https://tailwindcss.com/docs/content-configuration
  content: [
    "./app/**/*.{ts,tsx}",        // Next.js App Router pages
    "./components/**/*.{ts,tsx}",  // Reusable components
    "./lib/**/*.{ts,tsx}",         // Utility libraries
  ],

  theme: {
    extend: {
      // Custom color palette — medical-grade blues, greens, and neutrals
      // Source: https://tailwindcss.com/docs/customizing-colors
      colors: {
        // Primary: Deep medical blue (inspired by IBM Watsonx branding)
        primary: {
          50: "#eff6ff",   // Lightest blue for backgrounds
          100: "#dbeafe",  // Light blue for hover states
          200: "#bfdbfe",  // Soft blue for borders
          300: "#93c5fd",  // Medium-light blue
          400: "#60a5fa",  // Medium blue
          500: "#3b82f6",  // Primary blue (main CTA buttons)
          600: "#2563eb",  // Darker blue for active states
          700: "#1d4ed8",  // Deep blue for headers
          800: "#1e40af",  // Very deep blue
          900: "#1e3a8a",  // Darkest blue for dark mode accents
        },
        // Accent: Medical green (health/success indicator)
        medical: {
          50: "#f0fdf4",   // Lightest green
          100: "#dcfce7",  // Light green
          200: "#bbf7d0",  // Soft green
          300: "#86efac",  // Medium green
          400: "#4ade80",  // Bright green (health indicators)
          500: "#22c55e",  // Primary green (success states)
          600: "#16a34a",  // Dark green
          700: "#15803d",  // Deep green
          800: "#166534",  // Very deep green
          900: "#14532d",  // Darkest green
        },
        // Sidebar and dark backgrounds
        sidebar: {
          DEFAULT: "#0f172a",    // Dark navy sidebar — Source: Tailwind slate-900
          hover: "#1e293b",      // Slightly lighter on hover — Source: Tailwind slate-800
          active: "#334155",     // Active state — Source: Tailwind slate-700
        },
      },

      // Custom font families — clean, professional medical look
      // Source: https://tailwindcss.com/docs/font-family
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],   // Primary font — Source: https://fonts.google.com/specimen/Inter
        mono: ["JetBrains Mono", "monospace"],         // Code/data font — Source: https://fonts.google.com/specimen/JetBrains+Mono
      },

      // Custom animations for polished UI interactions
      // Source: https://tailwindcss.com/docs/animation
      animation: {
        "fade-in": "fadeIn 0.3s ease-in-out",           // Smooth fade in for messages
        "slide-up": "slideUp 0.3s ease-out",             // Slide up for new content
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite", // Slow pulse for loading
        "typing": "typing 1.5s ease-in-out infinite",    // Typing indicator dots
      },

      // Keyframe definitions for custom animations
      // Source: https://tailwindcss.com/docs/animation#customizing-your-theme
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        typing: {
          "0%, 60%, 100%": { opacity: "0.3" },
          "30%": { opacity: "1" },
        },
      },

      // Custom border radius for card-like elements
      // Source: https://tailwindcss.com/docs/border-radius
      borderRadius: {
        "xl": "1rem",
        "2xl": "1.5rem",
      },
    },
  },

  // Tailwind CSS plugins
  // Source: https://tailwindcss.com/docs/plugins
  plugins: [],
};

export default config; // Export configuration — Source: https://tailwindcss.com/docs/configuration
