#!/usr/bin/env python3
# ============================================================================
# seed_pubmed.py — PubMed Knowledge Base Seeding Script
# One-time script to populate the MedBuddy knowledge base with PubMed abstracts.
# Downloads and indexes ~10,000 medical abstracts across key clinical topics.
# Run this BEFORE the competition demo to ensure a rich knowledge base.
#
# Usage: python -m scripts.seed_pubmed (from backend/ directory)
#
# Source: https://www.ncbi.nlm.nih.gov/books/NBK25501/ (NCBI E-utilities)
# Source: https://pubmed.ncbi.nlm.nih.gov/ (PubMed)
# ============================================================================

import asyncio  # Async event loop for running async functions — Source: https://docs.python.org/3/library/asyncio.html
import sys  # System utilities — Source: https://docs.python.org/3/library/sys.html
import os  # OS utilities for path manipulation — Source: https://docs.python.org/3/library/os.html

# Add parent directory to Python path so we can import our modules
# Source: https://docs.python.org/3/library/sys.html#sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.pubmed_service import ingest_pubmed_articles  # PubMed ingestion pipeline — Source: ./services/pubmed_service.py


# Medical topics to seed the knowledge base with
# These cover common clinical areas that competition judges are likely to ask about
# Source: https://www.ncbi.nlm.nih.gov/mesh (MeSH medical subject headings)
SEED_TOPICS = [
    # Cardiology — the existing PDF covers cardiac arrest, so extend this domain
    {"query": "cardiac arrest treatment 2024", "max_results": 500},
    {"query": "heart failure diagnosis management", "max_results": 500},
    {"query": "atrial fibrillation anticoagulation", "max_results": 300},

    # Emergency Medicine — high-impact, dramatic for demos
    {"query": "emergency medicine trauma assessment", "max_results": 500},
    {"query": "stroke acute treatment thrombolysis", "max_results": 300},
    {"query": "sepsis early recognition antibiotics", "max_results": 300},

    # Pharmacology — drug interactions are impressive to demo
    {"query": "drug interactions adverse effects clinical", "max_results": 500},
    {"query": "antibiotic resistance mechanisms treatment", "max_results": 300},

    # Internal Medicine — broad coverage
    {"query": "diabetes mellitus type 2 management guidelines", "max_results": 500},
    {"query": "hypertension treatment guidelines 2024", "max_results": 300},
    {"query": "chronic kidney disease progression", "max_results": 300},

    # Oncology — important and complex domain
    {"query": "cancer immunotherapy checkpoint inhibitors", "max_results": 500},
    {"query": "breast cancer screening early detection", "max_results": 300},

    # Infectious Disease — always relevant
    {"query": "COVID-19 long covid treatment 2024", "max_results": 500},
    {"query": "tuberculosis diagnosis treatment multidrug resistant", "max_results": 300},

    # Pediatrics — niche but impressive
    {"query": "pediatric fever management guidelines", "max_results": 200},

    # Mental Health — increasingly important domain
    {"query": "depression treatment SSRI cognitive behavioral therapy", "max_results": 300},
    {"query": "anxiety disorders pharmacotherapy", "max_results": 200},

    # Surgery / Procedures
    {"query": "surgical site infection prevention", "max_results": 200},

    # Medical AI / Digital Health — meta-relevant for a tech competition
    {"query": "artificial intelligence medical diagnosis clinical", "max_results": 500},
]


async def main():
    """
    Main seeding function — iterates through all seed topics and ingests PubMed abstracts.
    Logs progress and summary statistics.

    Source: https://docs.python.org/3/library/asyncio.html#asyncio.run
    """
    print("=" * 70)
    print("🩺 MedBuddy — PubMed Knowledge Base Seeding Script")
    print("=" * 70)
    print(f"📋 Total topics to ingest: {len(SEED_TOPICS)}")
    total_target = sum(t["max_results"] for t in SEED_TOPICS)
    print(f"🎯 Target abstracts: ~{total_target}")
    print("=" * 70)

    # Track overall progress
    grand_total_fetched = 0  # Total abstracts fetched across all topics
    grand_total_indexed = 0  # Total abstracts successfully indexed

    # Process each topic sequentially
    for i, topic in enumerate(SEED_TOPICS, start=1):
        print(f"\n--- Topic {i}/{len(SEED_TOPICS)}: '{topic['query']}' ---")

        try:
            # Run the ingestion pipeline for this topic
            stats = await ingest_pubmed_articles(
                query=topic["query"],  # PubMed search query
                max_results=topic["max_results"],  # Max abstracts for this topic
            )

            # Update running totals
            grand_total_fetched += stats["total_fetched"]
            grand_total_indexed += stats["total_indexed"]

            print(f"   ✅ Fetched: {stats['total_fetched']}, Indexed: {stats['total_indexed']}")

        except Exception as e:
            # Log errors but continue with other topics
            print(f"   ❌ Failed: {e}")
            continue

        # Brief pause between topics to be respectful of NCBI API
        # Source: https://www.ncbi.nlm.nih.gov/books/NBK25497/#chapter2.Usage_Guidelines_and_Requiremen
        await asyncio.sleep(1)

    # Print summary
    print("\n" + "=" * 70)
    print("📊 SEEDING COMPLETE — Summary")
    print("=" * 70)
    print(f"   Topics processed: {len(SEED_TOPICS)}")
    print(f"   Total abstracts fetched: {grand_total_fetched}")
    print(f"   Total abstracts indexed: {grand_total_indexed}")
    print(f"   Success rate: {(grand_total_indexed/grand_total_fetched*100):.1f}%" if grand_total_fetched > 0 else "   No abstracts fetched")
    print("=" * 70)
    print("🎉 Knowledge base is ready for the competition demo!")


# Entry point — run the async main function
# Source: https://docs.python.org/3/library/asyncio.html#asyncio.run
if __name__ == "__main__":
    asyncio.run(main())
