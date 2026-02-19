# ============================================================================
# pubmed_service.py — PubMed Abstract Fetcher via NCBI E-utilities API
# Downloads medical research abstracts from PubMed (the world's largest
# biomedical literature database) for indexing in our RAG knowledge base.
# Source: https://www.ncbi.nlm.nih.gov/books/NBK25501/ (E-utilities documentation)
# Source: https://pubmed.ncbi.nlm.nih.gov/ (PubMed home)
# ============================================================================

import httpx  # Async HTTP client for NCBI API calls — Source: https://www.python-httpx.org/
import defusedxml.ElementTree as ET  # Secure XML parser protecting against entity expansion attacks — Source: https://github.com/tiran/defusedxml
import asyncio  # Async sleep for rate limiting — Source: https://docs.python.org/3/library/asyncio.html
from typing import List, Dict, Optional  # Type hints — Source: https://docs.python.org/3/library/typing.html
from config import settings  # Centralized configuration — Source: ./config.py


# NCBI E-utilities base URL for all PubMed API calls
# Source: https://www.ncbi.nlm.nih.gov/books/NBK25501/
NCBI_BASE = settings.NCBI_BASE_URL


async def search_pubmed(query: str, max_results: int = 100) -> List[str]:
    """
    Search PubMed for article IDs matching a query string.
    Uses the ESearch E-utility to find PMIDs (PubMed IDs).

    Args:
        query: Medical search query (e.g., "cardiac arrest treatment")
        max_results: Maximum number of PMIDs to return

    Returns:
        List of PubMed ID strings (PMIDs)

    Source: https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESearch
    """
    # Build the ESearch URL with query parameters
    # Source: https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESearch
    params = {
        "db": "pubmed",  # Search the PubMed database
        "term": query,  # The search query string
        "retmax": min(max_results, 10000),  # Cap at 10,000 (NCBI limit)
        "retmode": "json",  # Request JSON response format
        "sort": "relevance",  # Sort by relevance to query — Source: https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.sort
    }

    # Add NCBI API key if available (increases rate limit from 3 to 10 req/sec)
    # Source: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
    if settings.NCBI_API_KEY:
        params["api_key"] = settings.NCBI_API_KEY

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Make the search request to NCBI E-utilities
        # Source: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
        response = await client.get(f"{NCBI_BASE}/esearch.fcgi", params=params)
        response.raise_for_status()  # Raise on HTTP errors

        # Parse the JSON response to extract PMIDs
        # Source: https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESearch
        data = response.json()
        pmids = data.get("esearchresult", {}).get("idlist", [])  # Extract the list of PMIDs

    return pmids  # Return list of PubMed ID strings


async def fetch_abstracts(pmids: List[str], batch_size: int = 200) -> List[Dict[str, str]]:
    """
    Fetch article abstracts and metadata from PubMed using the EFetch E-utility.
    Processes PMIDs in batches to respect NCBI rate limits.

    Args:
        pmids: List of PubMed IDs to fetch
        batch_size: Number of PMIDs per batch request (max 200 recommended)

    Returns:
        List of dicts with 'pmid', 'title', 'abstract', 'journal', 'year' keys

    Source: https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.EFetch
    """
    articles = []  # Accumulator for fetched articles

    # Process PMIDs in batches to avoid overloading the API
    # Source: https://www.ncbi.nlm.nih.gov/books/NBK25497/#chapter2.Usage_Guidelines_and_Requiremen
    for i in range(0, len(pmids), batch_size):
        batch = pmids[i:i + batch_size]  # Get the next batch of PMIDs

        # Build the EFetch URL parameters
        # Source: https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.EFetch
        params = {
            "db": "pubmed",  # Fetch from PubMed database
            "id": ",".join(batch),  # Comma-separated PMIDs
            "rettype": "xml",  # XML format (contains full structured data)
            "retmode": "xml",  # Response mode
        }

        # Add NCBI API key if available for higher rate limits
        if settings.NCBI_API_KEY:
            params["api_key"] = settings.NCBI_API_KEY

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Make the fetch request to NCBI E-utilities
            # Source: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi
            response = await client.get(f"{NCBI_BASE}/efetch.fcgi", params=params)
            response.raise_for_status()  # Raise on HTTP errors

            # Parse the XML response to extract article data
            # Source: https://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html (PubMed XML schema)
            articles.extend(_parse_pubmed_xml(response.text))

        # Rate limiting: wait 0.34 seconds between batches (3 req/sec without API key)
        # Source: https://www.ncbi.nlm.nih.gov/books/NBK25497/#chapter2.Usage_Guidelines_and_Requiremen
        if i + batch_size < len(pmids):
            await asyncio.sleep(0.34)  # Respect NCBI rate limits

        # Log progress
        print(f"   Fetched {min(i + batch_size, len(pmids))}/{len(pmids)} abstracts...")

    return articles  # Return all fetched article data


def _parse_pubmed_xml(xml_text: str) -> List[Dict[str, str]]:
    """
    Parse PubMed EFetch XML response into structured article dictionaries.
    Extracts title, abstract, journal name, publication year, and PMID.

    Source: https://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html
    Source: https://docs.python.org/3/library/xml.etree.elementtree.html
    """
    articles = []  # Accumulator for parsed articles

    try:
        # Parse the XML string into an ElementTree
        # Source: https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.fromstring
        root = ET.fromstring(xml_text)

        # Iterate through each PubmedArticle element
        # Source: https://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#pubmedarticle
        for article in root.findall(".//PubmedArticle"):
            # Extract PMID (PubMed unique identifier)
            # Source: https://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#pmid
            pmid_elem = article.find(".//PMID")
            pmid = pmid_elem.text if pmid_elem is not None else ""

            # Extract article title
            # Source: https://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#articletitle
            title_elem = article.find(".//ArticleTitle")
            title = title_elem.text if title_elem is not None else ""

            # Extract abstract text (may have multiple AbstractText elements for structured abstracts)
            # Source: https://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#abstract
            abstract_parts = []
            for abstract_text in article.findall(".//AbstractText"):
                # Structured abstracts have labels (BACKGROUND, METHODS, RESULTS, CONCLUSIONS)
                label = abstract_text.get("Label", "")  # Get the section label if present
                text = abstract_text.text or ""  # Get the text content
                if label:
                    abstract_parts.append(f"{label}: {text}")  # Include label for structured abstracts
                else:
                    abstract_parts.append(text)  # Plain text for unstructured abstracts

            abstract = " ".join(abstract_parts)  # Combine all abstract sections

            # Extract journal name
            # Source: https://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#journal
            journal_elem = article.find(".//Journal/Title")
            journal = journal_elem.text if journal_elem is not None else ""

            # Extract publication year
            # Source: https://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#pubdate
            year_elem = article.find(".//PubDate/Year")
            year = year_elem.text if year_elem is not None else ""

            # Only include articles that have both a title and an abstract
            if title and abstract:
                articles.append({
                    "pmid": pmid,  # PubMed identifier (e.g., "12345678")
                    "title": title,  # Article title
                    "abstract": abstract,  # Full abstract text
                    "journal": journal,  # Journal name
                    "year": year,  # Publication year
                })

    except ET.ParseError as e:
        # Log XML parsing errors but don't crash the whole batch
        print(f"⚠️ XML parsing error: {e}")

    return articles  # Return parsed articles


async def ingest_pubmed_articles(
    query: str,
    max_results: int = 100,
) -> Dict[str, int]:
    """
    Full PubMed ingestion pipeline: search → fetch → chunk → embed → store.
    This is the main entry point called by the /api/ingest/pubmed endpoint.

    Args:
        query: PubMed search query
        max_results: Maximum number of articles to ingest

    Returns:
        Dict with 'total_fetched' and 'total_indexed' counts

    Source: https://www.ncbi.nlm.nih.gov/books/NBK25501/
    """
    # Import here to avoid circular imports
    from services.embedding_service import embed_batch  # Embedding function — Source: ./services/embedding_service.py
    from services.vector_service import store_document, store_chunks  # Vector store functions — Source: ./services/vector_service.py
    from services.document_service import chunk_text  # Text chunking — Source: ./services/document_service.py

    # Step 1: Search PubMed for matching article IDs
    print(f"🔍 Searching PubMed for: '{query}' (max {max_results} results)...")
    pmids = await search_pubmed(query, max_results)
    print(f"   Found {len(pmids)} PMIDs")

    if not pmids:
        return {"total_fetched": 0, "total_indexed": 0}  # No results found

    # Step 2: Fetch article abstracts from PubMed
    print(f"📥 Fetching abstracts for {len(pmids)} articles...")
    articles = await fetch_abstracts(pmids)
    print(f"   Fetched {len(articles)} articles with abstracts")

    # Step 3: Process each article (chunk → embed → store)
    total_indexed = 0  # Counter for successfully indexed articles
    for i, article in enumerate(articles):
        try:
            # Combine title and abstract for richer content
            full_text = f"{article['title']}\n\n{article['abstract']}"

            # Chunk the article text
            chunks = chunk_text(
                full_text,
                metadata={
                    "pubmed_id": article["pmid"],  # PubMed identifier for citation
                    "title": article["title"],  # Article title
                    "journal": article["journal"],  # Journal name
                    "year": article["year"],  # Publication year
                    "source": "pubmed",  # Mark as PubMed source
                },
            )

            # Generate embeddings for all chunks
            texts = [c["content"] for c in chunks]  # Extract text content
            embeddings = await embed_batch(texts)  # Batch embed all chunks

            # Store the document record in Supabase
            doc_id = await store_document(
                filename=article["title"][:200],  # Use title as filename (truncated)
                file_type="pubmed",  # Mark as PubMed type
                source="pubmed",  # Source classification
                pubmed_id=article["pmid"],  # PubMed ID for reference
            )

            # Store all chunks with embeddings in the vector store
            await store_chunks(doc_id, chunks, embeddings)
            total_indexed += 1  # Increment success counter

            # Log progress every 10 articles
            if (i + 1) % 10 == 0:
                print(f"   Indexed {i + 1}/{len(articles)} articles...")

        except Exception as e:
            # Log the error but continue with remaining articles
            print(f"⚠️ Failed to index article {article.get('pmid', '?')}: {e}")
            continue

    print(f"✅ PubMed ingestion complete: {total_indexed}/{len(articles)} articles indexed")

    return {
        "total_fetched": len(articles),  # Number of articles fetched from PubMed
        "total_indexed": total_indexed,  # Number successfully embedded and stored
    }
