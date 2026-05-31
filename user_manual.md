# 📖 User Manual — ConstitutionGPT

This guide explains how to install, run, and use ConstitutionGPT as an end user.

---

## What is ConstitutionGPT?

ConstitutionGPT is a chat application that lets you ask questions about the United States Constitution in plain English. It finds the most relevant sections of the Constitution and uses AI to give you a clear, sourced answer.

**You can ask things like:**
- *"What rights does the First Amendment protect?"*
- *"How does a bill become a law?"*
- *"What are the qualifications to run for President?"*
- *"What does the 14th Amendment say about citizenship?"*
- *"How can the Constitution be amended?"*

---

## System Requirements

| Requirement | Minimum |
|-------------|---------|
| OS | Windows 10, macOS 11, or Linux |
| RAM | 4 GB (8 GB recommended) |
| Python | 3.10 or higher |
| Node.js | 18 or higher |
| Internet | Required (for Claude API calls) |
| Disk space | ~500 MB (for model + dependencies) |

---

## Installation

### Step 1 — Get the code

```bash
git clone https://code.swecha.org/<team>/<repo>.git
cd constitution-gpt
```

### Step 2 — Get the Constitution PDF

```bash
curl -o data/constitution.pdf \
  "https://constitutioncenter.org/media/files/constitution.pdf"
```

If `curl` isn't available, download the PDF manually from
[constitutioncenter.org](https://constitutioncenter.org/media/files/constitution.pdf)
and save it as `data/constitution.pdf`.

### Step 3 — Get an Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up / log in
3. Navigate to **API Keys** → **Create Key**
4. Copy the key (starts with `sk-ant-...`)

### Step 4 — Install backend

```bash
cd backend

# Create isolated Python environment
python -m venv .venv

# Activate it
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\activate             # Windows

# Install all dependencies
pip install -r requirements.txt

# Add your API key
echo "ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE" > .env
```

### Step 5 — Install frontend

```bash
cd ../frontend
npm install
```

---

## Running the App

You need **two terminals** running simultaneously.

### Terminal 1 — Backend

```bash
cd backend
source .venv/bin/activate    # skip if already active
python app.py
```

Expected output:
```
[vector_store] Loading existing vector store...    ← after first run
Starting ConstitutionGPT backend on port 5000...
 * Running on http://0.0.0.0:5000
```

> ⏳ **First run only**: you'll see embedding progress for ~30 seconds while the vector index is built. This is normal.

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

Expected output:
```
  VITE v5.x.x  ready in 300ms
  ➜  Local:   http://localhost:5173/
```

### Open the app

Open your browser and go to: **http://localhost:5173**

---

## Using the Chat Interface

### Landing Screen

When you first open the app, you'll see:
- The **ConstitutionGPT** header with a scroll icon
- A preamble quote
- **8 suggested questions** you can click to get started instantly

### Asking a Question

**Option A — Click a suggestion**
Click any of the pre-written question pills to immediately send it.

**Option B — Type your own**
Click the input box at the bottom, type your question, and press:
- **Enter** to send
- **Shift + Enter** to add a new line without sending

### Reading an Answer

Each AI response shows:
- The **answer text**, grounded in the Constitution
- A **"Show X sources"** button below the answer

### Viewing Sources

Click **"Show sources"** to expand the source panel. Each source card shows:
- **Page number** (gold badge) — which page of the PDF it came from
- **Match %** — how relevant this excerpt was to your question (higher = more relevant)
- Click the card to expand and read the actual excerpt text

### Follow-up Questions

You can ask follow-up questions naturally. ConstitutionGPT remembers the context of your conversation:

```
You:  What does the First Amendment say?
Bot:  [answer about free speech, religion, press...]

You:  Which of those rights can be limited?   ← follow-up
Bot:  [answer referencing the previous context]
```

### Starting a New Conversation

Click **"New chat"** in the top-right corner to clear the conversation and start fresh.

---

## Troubleshooting

### "Failed to fetch" or blank answer
- Make sure the **backend is running** (`python app.py` in Terminal 1)
- Check that it's running on port 5000: visit http://localhost:5000/health — you should see `{"status":"ok"}`

### Backend crashes on startup with "FileNotFoundError"
- The PDF is missing. Run:
  ```bash
  curl -o data/constitution.pdf "https://constitutioncenter.org/media/files/constitution.pdf"
  ```

### "ANTHROPIC_API_KEY not found"
- The `.env` file is missing or has the wrong format. Check:
  ```bash
  cat backend/.env
  # Should show: ANTHROPIC_API_KEY=sk-ant-...
  ```

### First query is very slow (30+ seconds)
- Normal! The vector index is being built for the first time. Subsequent queries will be fast (~2–3 seconds).

### Frontend shows blank page
- Run `npm install` inside the `frontend/` folder if you haven't
- Check the browser console (F12) for errors

### Port already in use
```bash
# Kill whatever is using port 5000
lsof -ti:5000 | xargs kill     # macOS/Linux
# or change the port in backend/.env:
PORT=5001
```

---

## FAQ

**Q: Does this work offline?**
No. The app needs internet access to call the Claude API. The embedding model runs locally, but answer generation requires an API call.

**Q: How accurate are the answers?**
Answers are grounded in real excerpts from the Constitution PDF. The AI only uses what it retrieves — if an excerpt is relevant, the answer will be accurate. Always check the source cards to verify.

**Q: Can I use a different document instead of the Constitution?**
Yes! Replace `data/constitution.pdf` with any PDF, then hit the rebuild endpoint:
```bash
curl -X POST http://localhost:5000/api/rebuild-index
```

**Q: Is my conversation stored anywhere?**
No. Conversations exist only in your browser's memory and are cleared when you refresh the page or click "New chat".

**Q: How much does it cost to run?**
Each question costs roughly $0.001–$0.003 in Anthropic API credits depending on answer length.