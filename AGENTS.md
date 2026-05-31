# 🤖 AGENTS.md — ConstitutionGPT

This document describes the AI agents, models, prompts, and decision-making components used in ConstitutionGPT. It is intended for developers who want to understand, modify, or extend the AI behaviour of the system.

---

## Overview

ConstitutionGPT uses a **single-agent RAG architecture** — one LLM agent (Claude) that answers questions based on context retrieved by a deterministic search pipeline. There is no multi-agent orchestration, tool use, or autonomous planning in the current version.

```
┌─────────────────────────────────────────────────────────┐
│                    AGENT SYSTEM                         │
│                                                         │
│   ┌──────────────────┐      ┌───────────────────────┐  │
│   │  Retrieval Agent │      │   Answer Agent        │  │
│   │  (deterministic) │─────▶│   (Claude LLM)        │  │
│   │  vector_store.py │      │   rag.py              │  │
│   └──────────────────┘      └───────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Agent 1 — Retrieval Agent

**File**: `backend/vector_store.py`
**Type**: Deterministic (no LLM involved)
**Purpose**: Find the most relevant sections of the Constitution for a given query

### How it works

1. **Ingestion** (runs once on first startup):
   - Loads `constitution.pdf` using `pypdf`
   - Splits text into overlapping chunks of 500 characters (100-char overlap)
   - Embeds every chunk using `all-MiniLM-L6-v2`
   - Saves embeddings + chunk metadata to `vector_store.pkl`

2. **Retrieval** (runs on every query):
   - Embeds the user's question using the same model
   - Computes cosine similarity between the question vector and all chunk vectors
   - Returns the top-K chunks (default: 5) ranked by similarity score

### Embedding Model

| Property | Value |
|----------|-------|
| Model name | `all-MiniLM-L6-v2` |
| Provider | Hugging Face / sentence-transformers |
| Runs | Locally (no API call) |
| Vector dimensions | 384 |
| Speed | ~500 chunks in ~20–30 seconds |
| License | Apache 2.0 |

### Chunking Strategy

```
Original page text (1500 chars):
│◄──── chunk 1 (500) ────►│
                  │◄──── chunk 2 (500) ────►│
                                    │◄──── chunk 3 (500) ────►│
         ◄── overlap (100) ──►
```

**Why overlap?** Constitutional text often has context that spans sentence boundaries. Overlapping ensures no clause is split across chunks and lost.

### Retrieval Parameters

| Parameter | Default | Effect |
|-----------|---------|--------|
| `CHUNK_SIZE` | 500 | Larger = more context per chunk but less precision |
| `CHUNK_OVERLAP` | 100 | Larger = fewer lost boundary sentences, more storage |
| `TOP_K` | 5 | More chunks = richer context but longer prompt |

---

## Agent 2 — Answer Agent (Claude)

**File**: `backend/rag.py`
**Type**: LLM-based (Anthropic Claude)
**Purpose**: Read retrieved excerpts and generate a clear, cited answer

### Model Configuration

| Property | Value |
|----------|-------|
| Model | `claude-opus-4-5` |
| Provider | Anthropic API |
| Max tokens | 1024 |
| Temperature | default (1.0) |
| Context window | 200k tokens |

### System Prompt

The system prompt defines the agent's persona, constraints, and output style:

```
You are ConstitutionGPT, an expert on the United States Constitution.
You answer questions strictly based on the provided excerpts from the Constitution.

Guidelines:
- Cite the article, section, or amendment when relevant
  (e.g. "Article I, Section 8" or "14th Amendment").
- If the excerpts don't contain enough information, say so honestly.
- Be precise, clear, and educational. Avoid speculation beyond the text.
- Format your answer with clear structure when listing multiple points.
```

**Key constraints enforced by the prompt:**
- Answers must be grounded in retrieved text only
- Must cite specific articles/amendments when possible
- Must acknowledge when information is insufficient (no hallucination)
- No speculation beyond what the Constitution says

### Prompt Construction

Each request to Claude is built as follows:

```
SYSTEM: <system prompt above>

USER:
  Relevant excerpts from the U.S. Constitution:

  [Excerpt 1 — Page 3]
  Congress shall make no law respecting an establishment of religion,
  or prohibiting the free exercise thereof...

  [Excerpt 2 — Page 3]
  ...or abridging the freedom of speech, or of the press...

  [Excerpt 3 — Page 7]
  ...

  ---

  Question: What does the First Amendment protect?

ASSISTANT: <generated answer>
```

### Conversation History

The agent supports multi-turn conversations. Previous turns are passed as `messages` in the API call:

```python
messages = [
    {"role": "user",      "content": "What is the First Amendment?"},
    {"role": "assistant", "content": "The First Amendment protects..."},
    {"role": "user",      "content": "Can those rights ever be limited?"},  # current
]
```

**Important**: Each turn includes freshly retrieved context for the current question. The history provides conversational continuity; the retrieval provides factual grounding.

---

## Data Flow — End to End

```
User types: "What powers does Congress have?"
      │
      ▼
frontend/src/App.jsx
  POST /api/chat
  { question: "What powers does Congress have?", history: [...] }
      │
      ▼
backend/app.py  →  query_rag(question, history)
      │
      ▼
backend/rag.py
  _get_store()  →  loads vector_store.pkl
  similarity_search("What powers does Congress have?", store, top_k=5)
      │
      ▼
backend/vector_store.py
  encode("What powers does Congress have?")  →  384-dim vector
  cosine_similarity(query_vec, all_chunk_vecs)
  return top 5 chunks  →  [{"text": "...", "page": 4, "score": 0.87}, ...]
      │
      ▼
backend/rag.py
  _build_context(chunks)  →  formatted string of excerpts
  build messages array with history + context + question
  anthropic.messages.create(model, system, messages)
      │
      ▼
  Anthropic Claude API
  returns: "Article I, Section 8 grants Congress the power to..."
      │
      ▼
backend/app.py
  return { "answer": "...", "sources": [...] }
      │
      ▼
frontend/src/Message.jsx
  renders answer bubble + source cards
```

---

## Limitations & Known Constraints

| Limitation | Details |
|------------|---------|
| **No tool use** | Claude cannot browse the web or call external APIs |
| **Static knowledge** | Answers are limited to the Constitution PDF provided |
| **No re-ranking** | Retrieval is purely cosine similarity — no cross-encoder re-ranking |
| **No query rewriting** | Multi-turn history is passed as-is; no query reformulation |
| **Context window** | Top-5 chunks (~2500 chars) is well within Claude's limits, but large TOP_K values could hit token limits |
| **English only** | Embedding model and system prompt are English-only |

---

## Extending the Agent System

### Add a different document
Replace `data/constitution.pdf` and call `POST /api/rebuild-index`.

### Change the LLM
Edit `rag.py`:
```python
model="claude-opus-4-5"   # change to any supported Anthropic model
```

### Add query rewriting (multi-turn improvement)
Before calling `similarity_search`, add a step that rewrites the question using history:
```python
# Example: use Claude to rewrite "what about the second one?" 
# → "What does the Second Amendment say?"
rewritten = rewrite_query(question, chat_history)
chunks = similarity_search(rewritten, store, top_k=TOP_K)
```

### Add re-ranking
After cosine retrieval, add a cross-encoder pass for better precision:
```python
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
scores = reranker.predict([(question, c["text"]) for c in chunks])
chunks = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
```

### Add streaming responses
Replace `client.messages.create` with `client.messages.stream` and use Flask's `stream_with_context` to push tokens to the frontend as they arrive.

---

## Security Notes

- The `ANTHROPIC_API_KEY` must never be committed to the repository
- The `.env` file is listed in `.gitignore`
- The `/api/rebuild-index` endpoint has no authentication — restrict it in production
- User messages are forwarded to the Anthropic API; do not deploy publicly without input sanitization