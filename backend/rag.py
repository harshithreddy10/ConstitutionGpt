"""
rag.py
Retrieval-Augmented Generation pipeline using Google Gemini.
"""

import os
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv
from vector_store import get_vector_store, similarity_search

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

PDF_PATH = str(BASE_DIR.parent / "data" / "constitution.pdf")
TOP_K = 5
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ── Module-level state ─────────────────────────────────────────────────────────
_store = None
_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        _client = genai.Client(api_key=api_key)
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


def _build_history(chat_history: list[dict] | None) -> str:
    if not chat_history:
        return "No previous conversation."

    lines = []
    for message in chat_history:
        role = message.get("role", "user").title()
        content = str(message.get("content", "")).strip()
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines) if lines else "No previous conversation."


SYSTEM_PROMPT = """You are ConstitutionGPT, an expert on the Constitution represented by the provided excerpts.
You answer questions strictly based on those excerpts.

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
    3. Call Gemini and return answer + source chunks.

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
    history = _build_history(chat_history)

    prompt = (
        f"Conversation so far:\n{history}\n\n"
        f"Relevant excerpts from the Constitution:\n\n"
        f"{context}\n\n"
        f"---\n\n"
        f"Question: {question}"
    )

    client = _get_client()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=1024,
            temperature=1.0,
        ),
    )

    answer = response.text or "I could not generate an answer from the retrieved excerpts."

    sources = [
        {"page": c["page"], "text": c["text"][:300], "score": round(c["score"], 4)}
        for c in chunks
    ]

    return {"answer": answer, "sources": sources}
