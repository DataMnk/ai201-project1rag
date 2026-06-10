import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_documents

# Load the embedding model — this runs locally, no API key needed
# all-MiniLM-L6-v2 is a lightweight model that works well for English text
model = SentenceTransformer("all-MiniLM-L6-v2")

# Set up ChromaDB — this creates a local folder called chroma_db/ to store vectors
# PersistentClient means the data survives between runs (not just in memory)
client = chromadb.PersistentClient(path="./chroma_db")

# Create (or get if it already exists) a collection — think of it like a table in a DB
# This is where all our chunk embeddings will live
#collection = client.get_or_create_collection(name="internship_guides") #this line was giving distances too high. LEts use cosine instead of euclid.
collection = client.get_or_create_collection(
    name="internship_guides",
    metadata={"hnsw:space": "cosine"}  # cosine similarity gives distances between 0-1
)


def embed_and_store(chunks: list[dict]) -> None:
    """
    Take the chunks from ingest.py and store them in ChromaDB.
    
    For each chunk we store three things:
    - The text itself (so we can return it later)
    - Its embedding (the vector ChromaDB uses to search)
    - Its metadata (source filename, for attribution)
    """
    print(f"Embedding and storing {len(chunks)} chunks...")

    # Extract just the text strings — the embedding model needs a list of strings
    texts = [chunk["text"] for chunk in chunks]

    # Generate embeddings for all chunks at once (faster than one by one)
    # This returns a numpy array of shape (num_chunks, 384)
    embeddings = model.encode(texts, show_progress_bar=True)

    # Build the metadata list — one dict per chunk with the source filename
    metadatas = [{"source": chunk["source"]} for chunk in chunks]

    # Build unique IDs for each chunk — ChromaDB requires unique string IDs
    ids = [f"chunk_{i}" for i in range(len(chunks))]

    # Store everything in ChromaDB
    # documents = the raw text (returned in query results)
    # embeddings = the vectors (used for similarity search)
    # metadatas = source info (used for attribution)
    # ids = unique identifiers
    collection.add(
        documents=texts,
        embeddings=embeddings.tolist(),  # ChromaDB needs a plain list, not numpy array
        metadatas=metadatas,
        ids=ids
    )

    print(f"Stored {len(chunks)} chunks in ChromaDB.")


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """
    Given a user query, find the most semantically similar chunks in ChromaDB.
    
    How it works:
    1. Embed the query using the same model we used for the chunks
    2. ChromaDB compares that vector against all stored vectors
    3. Returns the top_k closest matches (lowest distance = most similar)
    
    Returns a list of dicts:
    {
        "text": "the chunk content",
        "source": "01_google_internship.txt",
        "distance": 0.23  # lower = more similar
    }
    """
    # Embed the query — must use same model as the chunks
    query_embedding = model.encode(query).tolist()

    # Query ChromaDB — it returns nested lists (one inner list per query)
    # Since we're only querying one string at a time, our results are at index [0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # Unpack the nested structure — results["documents"][0] is the list of chunk texts
    chunks = []
    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        chunks.append({
            "text": text,
            "source": metadata["source"],
            "distance": round(distance, 3)
        })

    return chunks


# Quick test — runs only when you execute: py retriever.py directly
if __name__ == "__main__":
    # First time: load documents and store them in ChromaDB
    # If you've already run this once, the data is already there
    chunks = load_documents()
    embed_and_store(chunks)

    print("\n--- Testing retrieval ---\n")

    # Test with 3 of our evaluation plan questions
    test_queries = [
        "What do students say about work-life balance at Google?",
        "How much do FAANG interns make per month?",
        "What are red flags in internship job descriptions?"
    ]

    for query in test_queries:
        print(f"Query: {query}")
        results = retrieve(query)
        for r in results:
            print(f"  [{r['source']}] (dist: {r['distance']}) {r['text'][:80]}...")
        print()