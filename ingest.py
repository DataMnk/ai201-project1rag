import os
import re

# pathlib lets us work with file paths in a clean, OS-independent way
from pathlib import Path


def clean_text(text: str) -> str:
    """
    Remove the SOURCE/TOPIC header lines that our .txt files start with.
    We don't want those lines showing up in chunks — they're metadata, not content.
    """
    lines = text.split("\n")
    cleaned_lines = []
    skip_header = True

    for line in lines:
        # The header ends at the "---" separator line
        if skip_header and line.strip() == "---":
            skip_header = False
            continue  # skip the "---" line itself too
        if skip_header:
            continue  # skip SOURCE: and TOPIC: lines
        cleaned_lines.append(line)

    # Join back into one string and strip leading/trailing whitespace
    cleaned = "\n".join(cleaned_lines).strip()

    # Remove any leftover HTML entities just in case (e.g. &amp; &nbsp;)
    cleaned = re.sub(r"&\w+;", " ", cleaned)

    # Collapse multiple blank lines into one
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split a long string into overlapping chunks of `chunk_size` characters.
    
    The overlap means each chunk shares `overlap` characters with the previous one —
    this prevents a key idea from being cut in half at a boundary and lost.
    
    Example with chunk_size=10, overlap=3:
      text = "ABCDEFGHIJKLMNOP"
      chunk 1: "ABCDEFGHIJ"
      chunk 2: "HIJKLMNOP"   <- starts 3 chars before chunk 1 ended
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Only keep chunks that have actual content (skip empty strings)
        if chunk.strip():
            chunks.append(chunk.strip())

        # Move forward by (chunk_size - overlap) so the next chunk overlaps
        start += chunk_size - overlap

    return chunks


def load_documents(docs_folder: str = "documents") -> list[dict]:
    """
    Load all .txt files from the documents/ folder.
    
    For each file, we:
    1. Read the raw text
    2. Clean it (remove headers)
    3. Split it into chunks
    4. Attach the source filename to each chunk as metadata
    
    Returns a list of dicts, each representing one chunk:
    {
        "text": "the actual chunk content",
        "source": "01_google_internship.txt"
    }
    """
    docs_path = Path(docs_folder)
    all_chunks = []

    # Iterate over every .txt file in the documents/ folder
    for filepath in sorted(docs_path.glob("*.txt")):
        
        # Read the file content
        raw_text = filepath.read_text(encoding="utf-8")
        
        # Clean it — remove SOURCE/TOPIC headers
        cleaned = clean_text(raw_text)
        
        # Split into chunks
        chunks = chunk_text(cleaned)
        
        # Attach source filename to each chunk so we can cite it later
        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "source": filepath.name  # e.g. "01_google_internship.txt"
            })

    print(f"Loaded {len(all_chunks)} chunks from {docs_folder}/")
    return all_chunks


# This block only runs if you execute this file directly: python ingest.py
# It's a quick sanity check — print 5 chunks and make sure they look right
if __name__ == "__main__":
    chunks = load_documents()
    print(f"\nTotal chunks: {len(chunks)}")
    print("\n--- Sample chunks ---\n")
    for i, chunk in enumerate(chunks[:5]):
        print(f"[{chunk['source']}]")
        print(chunk['text'])
        print("-" * 60)