# ============================================================================
# document_service.py — Document Parsing and Chunking Service
# Handles extraction of text from PDF, TXT, and MD files, then splits into
# overlapping chunks optimized for RAG retrieval.
# Source: https://www.pinecone.io/learn/chunking-strategies/
# Source: https://arxiv.org/abs/2312.06648 (chunking strategies for RAG)
# ============================================================================

import re  # Regular expressions for text cleaning — Source: https://docs.python.org/3/library/re.html
from typing import List, Dict, Any  # Type hints — Source: https://docs.python.org/3/library/typing.html
from pypdf import PdfReader  # PDF text extraction library — Source: https://pypdf.readthedocs.io/
import markdown  # Markdown to HTML converter (used to strip MD formatting) — Source: https://python-markdown.github.io/
from config import settings  # Centralized configuration — Source: ./config.py


def extract_text_from_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Extract text from a PDF file, page by page.
    Returns a list of dicts with 'text' and 'page_num' for each page.

    Source: https://pypdf.readthedocs.io/en/stable/user/extract-text.html
    """
    import io  # BytesIO for reading PDF from bytes — Source: https://docs.python.org/3/library/io.html

    # Create a PdfReader from the raw bytes (no need to save to disk)
    # Source: https://pypdf.readthedocs.io/en/stable/user/extract-text.html
    reader = PdfReader(io.BytesIO(file_bytes))

    pages = []  # Accumulator for extracted pages

    # Iterate through each page in the PDF
    # Source: https://pypdf.readthedocs.io/en/stable/user/extract-text.html#extract-text-from-a-pdf
    for page_num, page in enumerate(reader.pages, start=1):
        # Extract text content from this page
        text = page.extract_text() or ""  # Returns empty string if extraction fails

        # Only include pages that have meaningful text content
        if text.strip():
            pages.append({
                "text": text.strip(),  # The extracted text with whitespace trimmed
                "page_num": page_num,  # 1-indexed page number for citation
            })

    return pages  # Return list of page dicts


def extract_text_from_txt(file_bytes: bytes) -> str:
    """
    Extract text from a plain text file.
    Handles common encodings (UTF-8, Latin-1).

    Source: https://docs.python.org/3/howto/unicode.html
    """
    try:
        # Try UTF-8 first (most common encoding for text files)
        # Source: https://docs.python.org/3/library/codecs.html#standard-encodings
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        # Fall back to Latin-1 which can decode any byte sequence
        # Source: https://docs.python.org/3/library/codecs.html#standard-encodings
        return file_bytes.decode("latin-1")


def extract_text_from_markdown(file_bytes: bytes) -> str:
    """
    Extract plain text from a Markdown file by stripping formatting.
    Converts MD to HTML, then strips HTML tags to get clean text.

    Source: https://python-markdown.github.io/reference/
    """
    # Decode the markdown file content
    md_text = file_bytes.decode("utf-8", errors="replace")  # Replace invalid chars — Source: https://docs.python.org/3/library/codecs.html

    # Convert Markdown to HTML using the markdown library
    # Source: https://python-markdown.github.io/reference/#markdown
    html = markdown.markdown(md_text)

    # Strip all HTML tags to get plain text
    # Source: https://docs.python.org/3/library/re.html#re.sub
    clean_text = re.sub(r"<[^>]+>", "", html)  # Remove anything between < and >

    return clean_text.strip()  # Return cleaned text


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text for better chunking and embedding quality.
    Removes excessive whitespace, special characters, and normalizes line breaks.

    Source: https://www.pinecone.io/learn/chunking-strategies/#preprocessing
    """
    # Replace multiple newlines with a single newline
    # Source: https://docs.python.org/3/library/re.html#re.sub
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Replace multiple spaces with a single space
    text = re.sub(r" {2,}", " ", text)

    # Remove non-printable characters (keep basic ASCII + common Unicode)
    # Source: https://docs.python.org/3/library/re.html
    text = re.sub(r"[^\S\n]+", " ", text)

    return text.strip()  # Return the cleaned text


def chunk_text(
    text: str,
    chunk_size: int = None,
    chunk_overlap: int = None,
    metadata: Dict[str, Any] = None,
) -> List[Dict[str, Any]]:
    """
    Split text into overlapping chunks using sentence-aware boundaries.
    This ensures chunks don't break mid-sentence, improving retrieval quality.

    Chunking strategy: Split on sentence boundaries (periods, newlines) and
    maintain overlap between adjacent chunks to preserve cross-boundary context.

    Args:
        text: The full text to split into chunks
        chunk_size: Maximum characters per chunk (defaults to config CHUNK_SIZE)
        chunk_overlap: Characters of overlap between chunks (defaults to config CHUNK_OVERLAP)
        metadata: Additional metadata to attach to each chunk (page_num, source, etc.)

    Returns:
        List of chunk dicts with 'content' and 'metadata' keys

    Source: https://www.pinecone.io/learn/chunking-strategies/
    Source: https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/modules/#sentencesplitter
    """
    # Use config defaults if not specified
    effective_chunk_size = chunk_size or settings.CHUNK_SIZE  # Default: 512 chars
    effective_overlap = chunk_overlap or settings.CHUNK_OVERLAP  # Default: 50 chars

    # Clean the text before chunking
    text = clean_text(text)

    # If text is shorter than chunk size, return it as a single chunk
    if len(text) <= effective_chunk_size:
        return [{"content": text, "metadata": metadata or {}}]

    # Split text into sentences using regex (handles ., !, ?, and newlines)
    # Source: https://docs.python.org/3/library/re.html#re.split
    sentences = re.split(r"(?<=[.!?\n])\s+", text)

    chunks = []  # Accumulator for final chunks
    current_chunk = ""  # Buffer for building the current chunk

    for sentence in sentences:
        # If adding this sentence would exceed chunk size, save current chunk and start new one
        if len(current_chunk) + len(sentence) > effective_chunk_size and current_chunk:
            # Save the current chunk
            chunks.append({
                "content": current_chunk.strip(),  # The chunk text
                "metadata": {**(metadata or {}), "chunk_index": len(chunks)},  # Merge in metadata
            })

            # Start new chunk with overlap from the end of the previous chunk
            # Source: https://www.pinecone.io/learn/chunking-strategies/#fixed-size-chunking
            overlap_text = current_chunk[-effective_overlap:] if effective_overlap > 0 else ""
            current_chunk = overlap_text + " " + sentence  # New chunk starts with overlap
        else:
            # Add sentence to current chunk
            current_chunk = (current_chunk + " " + sentence).strip()

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append({
            "content": current_chunk.strip(),  # Final chunk text
            "metadata": {**(metadata or {}), "chunk_index": len(chunks)},  # Merge in metadata
        })

    return chunks  # Return all chunks


def process_document(file_bytes: bytes, filename: str, file_type: str) -> List[Dict[str, Any]]:
    """
    Main entry point for document processing.
    Routes to the appropriate extractor based on file type, then chunks the text.

    Args:
        file_bytes: Raw bytes of the uploaded file
        filename: Original filename for metadata
        file_type: File type string: 'pdf', 'txt', or 'md'

    Returns:
        List of chunk dicts ready for embedding and storage

    Source: https://www.pinecone.io/learn/chunking-strategies/
    """
    all_chunks = []  # Accumulator for all chunks from this document

    if file_type == "pdf":
        # Extract text page by page from PDF
        pages = extract_text_from_pdf(file_bytes)
        for page in pages:
            # Chunk each page separately, preserving page number in metadata
            page_chunks = chunk_text(
                page["text"],
                metadata={"filename": filename, "page_num": page["page_num"], "source": "upload"},
            )
            all_chunks.extend(page_chunks)  # Add all chunks from this page

    elif file_type == "txt":
        # Extract text from plain text file
        text = extract_text_from_txt(file_bytes)
        all_chunks = chunk_text(
            text,
            metadata={"filename": filename, "source": "upload"},
        )

    elif file_type == "md":
        # Extract text from Markdown file (strip formatting)
        text = extract_text_from_markdown(file_bytes)
        all_chunks = chunk_text(
            text,
            metadata={"filename": filename, "source": "upload"},
        )

    else:
        raise ValueError(f"Unsupported file type: {file_type}")  # Reject unknown file types

    return all_chunks  # Return all chunks ready for embedding
