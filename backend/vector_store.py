"""
vector_store.py
Handles document chunking, embedding, and FAISS vector store creation/loading.
"""

import os
import pickle
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

VECTOR_STORE_PATH = "vector_store.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500        # characters per chunk
CHUNK_OVERLAP = 100     # character overlap between chunks

_model = None


def get_embedding_model(local_files_only: bool = True) -> SentenceTransformer:
    """Load the embedding model once and reuse it across requests."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME, local_files_only=local_files_only)
    return _model


def load_pdf(pdf_path: str) -> list[dict]:
    """Load a PDF and return a list of {text, page} dicts."""
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append({"text": text, "page": i + 1})
    print(f"[vector_store] Loaded {len(pages)} pages from {pdf_path}")
    return pages


def chunk_pages(pages: list[dict]) -> list[dict]:
    """Split pages into overlapping text chunks."""
    chunks = []
    for page_info in pages:
        text = page_info["text"]
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "page": page_info["page"],
                    "chunk_id": len(chunks),
                })
            start += CHUNK_SIZE - CHUNK_OVERLAP
    print(f"[vector_store] Created {len(chunks)} chunks")
    return chunks


def build_vector_store(pdf_path: str) -> dict:
    """Build and cache a FAISS-style vector store from a PDF."""
    print("[vector_store] Building vector store...")
    model = get_embedding_model(local_files_only=False)

    pages = load_pdf(pdf_path)
    chunks = chunk_pages(pages)

    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    store = {
        "chunks": chunks,
        "embeddings": embeddings,  # shape: (N, dim)
        "model_name": MODEL_NAME,
    }

    with open(VECTOR_STORE_PATH, "wb") as f:
        pickle.dump(store, f)

    print(f"[vector_store] Saved vector store to {VECTOR_STORE_PATH}")
    return store


def load_vector_store() -> dict:
    """Load cached vector store from disk."""
    with open(VECTOR_STORE_PATH, "rb") as f:
        return pickle.load(f)


def get_vector_store(pdf_path: str) -> dict:
    """Return cached store if available, otherwise build it."""
    if os.path.exists(VECTOR_STORE_PATH):
        print("[vector_store] Loading existing vector store...")
        return load_vector_store()
    return build_vector_store(pdf_path)


def similarity_search(query: str, store: dict, top_k: int = 5) -> list[dict]:
    """
    Retrieve the top_k most relevant chunks for a query using cosine similarity.
    Returns list of chunk dicts with an added 'score' field.
    """
    model = get_embedding_model(local_files_only=True)
    query_vec = model.encode([query], convert_to_numpy=True)[0]  # (dim,)

    embeddings = store["embeddings"]  # (N, dim)

    # Cosine similarity
    norms = np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_vec)
    norms = np.where(norms == 0, 1e-10, norms)
    scores = (embeddings @ query_vec) / norms

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        chunk = dict(store["chunks"][idx])
        chunk["score"] = float(scores[idx])
        results.append(chunk)

    return results
