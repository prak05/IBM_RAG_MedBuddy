// ============================================================================
// lib/utils.ts — Utility Functions for MedBuddy Frontend
// Contains the cn() helper for merging Tailwind CSS classes (used by Shadcn/ui)
// and API communication utilities.
// Source: https://ui.shadcn.com/docs/installation/manual
// ============================================================================

import { type ClassValue, clsx } from "clsx"; // Class name builder — Source: https://github.com/lukeed/clsx
import { twMerge } from "tailwind-merge"; // Tailwind class merger — Source: https://github.com/dcastil/tailwind-merge

/**
 * Merge Tailwind CSS class names intelligently.
 * Combines clsx (conditional classes) with tailwind-merge (deduplication).
 * This is the standard utility used by all Shadcn/ui components.
 * Source: https://ui.shadcn.com/docs/installation/manual#add-a-cn-helper
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs)); // Merge and deduplicate class names
}
