# 📜 ConstitutionGPT

> A Retrieval-Augmented Generation (RAG) chatbot that answers questions about the United States Constitution using Google Gemini and local vector search.

---

## 🧠 What is ConstitutionGPT?

ConstitutionGPT is an AI-powered question answering system built on top of the full text of the U.S. Constitution. It uses **RAG (Retrieval-Augmented Generation)** — meaning it doesn't just rely on the LLM's memory, it actually retrieves relevant excerpts from the Constitution in real time and grounds every answer in the source text.

### Key Features
- 🔍 **Semantic search** over the full Constitution text
- 📄 **Source citations** — every answer shows which page/section it came from
- 💬 **Multi-turn conversation** — remembers context across a chat session
- ⚡ **Fast responses** — vector index is built once and cached locally
- 🔒 **No external vector DB** — runs entirely on your machine

---

## 🏗️ Architecture

```
User Question
      │
      ▼
┌─────────────────┐        POST /api/chat        ┌──────────────────────────┐
│  React Frontend │ ──────────────────────────▶  │     Flask Backend        │
│  (Vite + TW)    │ ◀──────────────────────────  │     app.py               │
└─────────────────┘     { answer, sources }       └────────────┬─────────────┘
                                                               │
                                                    ┌──────────▼──────────┐
                                                    │    RAG Pipeline      │
                                                    │    rag.py            │
                                                    │                      │
                                                    │  1. Embed question   │
                                                    │  2. Cosine search    │
                                                    │  3. Top-5 chunks     │
                                                    │  4. Build prompt     │
                                                    │  5. Gemini API call  │
                                                    └──────────┬──────────┘
                                                               │
                                                    ┌──────────▼──────────┐
                                                    │   vector_store.py    │
                                                    │  PDF → chunks →      │
                                                    │  embeddings →        │
                                                    │  vector_store.pkl    │
                                                    └─────────────────────┘
```

**Embedding model**: `all-MiniLM-L6-v2` (runs locally via sentence-transformers)
**LLM**: Gemini via Google AI API
**Vector search**: Cosine similarity over NumPy (no external DB)
**Frontend**: React 18 + Vite + Tailwind CSS
**Backend**: Python 3.11 + Flask

---

## 📁 Project Structure

```
constitution-gpt/
├── backend/
│   ├── app.py              # Flask REST API server
│   ├── rag.py              # RAG pipeline (retrieval + Gemini)
│   ├── vector_store.py     # PDF loading, chunking, embedding, search
│   ├── .env                # API keys (never commit this)
│   └── requirements.txt    # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main layout + state management
│   │   ├── Message.jsx     # Chat bubble component
│   │   ├── SourceCard.jsx  # Collapsible source excerpt card
│   │   ├── main.jsx        # React entry point
│   │   └── index.css       # Tailwind directives + global styles
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── vite.config.js
│
├── data/
│   └── constitution.pdf    # Add this yourself (see setup)
│
├── README.md
├── CONTRIBUTING.md
├── USER_MANUAL.md
└── AGENTS.md
```

---

## ⚙️ Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.10+ | python.org |
| Node.js | 18+ | nodejs.org |
| npm | 9+ | Comes with Node |
| Git | any | git-scm.com |
| Google AI API Key | — | aistudio.google.com |

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://code.swecha.org/<your-team>/<your-repo>.git
cd constitution-gpt
```

### 2. Add the Constitution PDF

```bash
curl -o data/constitution.pdf \
  "https://constitutioncenter.org/media/files/constitution.pdf"
```

### 3. Set up the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
echo "GOOGLE_API_KEY=your-google-ai-key-here" > .env
python app.py
```

> First startup takes ~30 seconds to build the vector index. Subsequent starts are instant.

Backend runs at: **http://localhost:5001**

### 4. Set up the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## 🔌 API Reference

### `POST /api/chat`

```json
// Request
{ "question": "What does the First Amendment protect?", "history": [] }

// Response
{
  "answer": "The First Amendment protects...",
  "sources": [{ "page": 3, "text": "Congress shall make no law...", "score": 0.89 }]
}
```

### `GET /health`
```json
{ "status": "ok", "service": "ConstitutionGPT" }
```

### `POST /api/rebuild-index`
Force-rebuilds the vector store after replacing the PDF.

---

## 🛠️ Configuration

| Setting | File | Default | Description |
|---------|------|---------|-------------|
| `CHUNK_SIZE` | `vector_store.py` | `500` | Characters per chunk |
| `CHUNK_OVERLAP` | `vector_store.py` | `100` | Overlap between chunks |
| `TOP_K` | `rag.py` | `5` | Chunks retrieved per query |
| `GEMINI_MODEL` | `.env` | `gemini-2.5-flash` | Gemini model used |
| `PORT` | `.env` | `5001` | Backend server port |

---

## 👥 Team

| Name | Role |
|------|------|
| Member 1 | Backend — RAG pipeline, vector store |
| Member 2 | Frontend — React UI, Tailwind CSS |
| Member 3 | Integration, documentation, deployment |

---

## 📄 License

MIT © 2025 — Built for Swecha PoC Demo
