"""
rag.py
Retrieval-Augmented Generation pipeline using Anthropic Claude.
"""

import os
import anthropic
from dotenv import load_dotenv
from vector_store import get_vector_store, similarity_search

load_dotenv()

PDF_PATH = "../data/constitution.pdf"
TOP_K = 5

# ── Module-level state ─────────────────────────────────────────────────────────
_store = None
_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def _get_store() -> dict:
    global _store
    if _store is None:
        _store = get_vector_store(PDF_PATH)
    return _store


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[Excerpt {i} — Page {chunk['page']}]\n{chunk['text']}"
        )
    return "\n\n".join(parts)


SYSTEM_PROMPT = """You are ConstitutionGPT, an expert on the United States Constitution.
You answer questions strictly based on the provided excerpts from the Constitution.

Guidelines:
- Cite the article, section, or amendment when relevant (e.g. "Article I, Section 8" or "14th Amendment").
- If the excerpts don't contain enough information, say so honestly.
- Be precise, clear, and educational. Avoid speculation beyond the text.
- Format your answer with clear structure when listing multiple points."""


def query_rag(question: str, chat_history: list[dict] | None = None) -> dict:
    """
    Run a RAG query:
    1. Retrieve relevant chunks from the vector store.
    2. Build a prompt with context + conversation history.
    3. Call Claude and return answer + source chunks.

    Args:
        question: The user's question.
        chat_history: Optional list of {"role": ..., "content": ...} dicts
                      representing prior turns (excluding system).

    Returns:
        {
            "answer": str,
            "sources": [{"page": int, "text": str, "score": float}, ...]
        }
    """
    store = _get_store()
    chunks = similarity_search(question, store, top_k=TOP_K)
    context = _build_context(chunks)

    user_message = (
        f"Relevant excerpts from the U.S. Constitution:\n\n"
        f"{context}\n\n"
        f"---\n\n"
        f"Question: {question}"
    )

    # Build messages array
    messages: list[dict] = []
    if chat_history:
        messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    client = _get_client()
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    answer = response.content[0].text

    sources = [
        {"page": c["page"], "text": c["text"][:300], "score": round(c["score"], 4)}
        for c in chunks
    ]

    return {"answer": answer, "sources": sources}