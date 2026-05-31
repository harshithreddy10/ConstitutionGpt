"""
app.py
Flask API server for Constitution GPT.
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from rag import query_rag

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])


# ── Health check ────────────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "ConstitutionGPT"})


# ── Main chat endpoint ──────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def chat():
    """
    POST /api/chat
    Body: {
        "question": str,
        "history": [{"role": "user"|"assistant", "content": str}]  // optional
    }
    Response: {
        "answer": str,
        "sources": [{"page": int, "text": str, "score": float}]
    }
    """
    data = request.get_json(force=True)

    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400

    history = data.get("history", [])

    try:
        result = query_rag(question, chat_history=history or None)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        app.logger.exception("RAG pipeline error")
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500


# ── Rebuild index endpoint ──────────────────────────────────────────────────────
@app.route("/api/rebuild-index", methods=["POST"])
def rebuild_index():
    """Force-rebuild the vector store (useful after replacing the PDF)."""
    import vector_store as vs
    if os.path.exists(vs.VECTOR_STORE_PATH):
        os.remove(vs.VECTOR_STORE_PATH)
    try:
        vs.build_vector_store(vs.PDF_PATH if hasattr(vs, "PDF_PATH") else "../data/constitution.pdf")
        return jsonify({"status": "index rebuilt"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    print(f"Starting ConstitutionGPT backend on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=debug)