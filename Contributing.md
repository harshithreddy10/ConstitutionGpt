# 🤝 Contributing to ConstitutionGPT

Welcome! This document explains how our team of 3 collaborates on this project — branching strategy, commit conventions, code style, and the full Git workflow for committing and pushing to [code.swecha.org](https://code.swecha.org).

---

## 👥 Team Roles & Ownership

| Member | Username | Primary Responsibility | Files Owned |
|--------|----------|----------------------|-------------|
| **Harshith** | `Harshith_2006` | Backend — RAG & vector store | `backend/rag.py`, `backend/vector_store.py` |
| **Rohith** | `Rohith` | Frontend — React UI | `frontend/src/` |
| **Shashank** | `shashank_bodala` | Integration, API, Docs | `backend/app.py`, `*.md` files |

Each member owns their area but reviews each other's MRs before merging.

---

## 🌿 Branch Strategy

```
main                        ← stable, always working, demo-ready
  └── dev                   ← integration branch, merge features here first
        ├── feat/rag-backend         (Harshith)
        ├── feat/react-frontend      (Rohith)
        └── feat/docs-integration    (Shashank)
```

**Rules:**
- Never commit directly to `main`
- All features go through a branch → MR → review → merge to `dev`
- Merge `dev` → `main` only when everything works end-to-end

---

## 👤 Individual Workflows

### Harshith — `feat/rag-backend`

```bash
git checkout -b feat/rag-backend
# work on backend/rag.py and backend/vector_store.py
git add backend/rag.py backend/vector_store.py
git commit -m "feat(rag): add RAG pipeline with cosine similarity search"
git push origin feat/rag-backend
```

---

### Rohith — `feat/react-frontend`

```bash
git checkout -b feat/react-frontend
# work on frontend/src/
git add frontend/src/
git commit -m "feat(frontend): add React chat UI with Tailwind CSS"
git push origin feat/react-frontend
```

---

### Shashank — `feat/docs-integration`

```bash
git checkout -b feat/docs-integration
# work on backend/app.py and all .md files
git add backend/app.py README.md CONTRIBUTING.md USER_MANUAL.md AGENTS.md
git commit -m "feat: add Flask API, CORS integration and project documentation"
git push origin feat/docs-integration
```

---

## 📝 Commit Message Convention

We follow **Conventional Commits**:

```
<type>(<scope>): <short description>

[optional body]
[optional footer]
```

### Types

| Type | When to use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code restructure, no feature change |
| `chore` | Dependency updates, config changes |
| `test` | Adding or updating tests |

### Examples per person

```bash
# Harshith
feat(rag): add multi-turn conversation history support
fix(vector_store): handle empty pages in PDF gracefully
refactor(rag): extract context builder into separate function

# Rohith
feat(frontend): add collapsible source cards to chat UI
fix(frontend): fix textarea auto-resize on mobile
style(frontend): fix inconsistent padding in Message component

# Shashank
feat(api): add Flask REST endpoints for chat and health check
docs(readme): add full API reference section
chore: add .gitignore to exclude env, pkl and node_modules
```

---

## 🔄 Full Git Workflow — Step by Step

### First-time setup (do this once)

```bash
# 1. Clone the repo (or fork it)
git clone https://code.swecha.org/Harshith_2006/constitutiongpt.git
cd constitutiongpt

# 2. Set your identity
git config user.name "Your Name"       # Harshith / Rohith / Shashank
git config user.email "your@email.com"

# 3. Verify remotes
git remote -v
# Should show: origin  https://code.swecha.org/Harshith_2006/constitutiongpt.git
```

---

### Daily workflow (do this every time you work)

```bash
# Step 1: Always start from an updated main branch
git checkout main
git pull origin main

# Step 2: Switch to your branch
# Harshith:
git checkout feat/rag-backend
# Rohith:
git checkout feat/react-frontend
# Shashank:
git checkout feat/docs-integration

# Step 3: Make your changes, then stage your files only
# Harshith:
git add backend/rag.py backend/vector_store.py
# Rohith:
git add frontend/src/
# Shashank:
git add backend/app.py README.md CONTRIBUTING.md USER_MANUAL.md AGENTS.md

# Step 4: Commit with a clear message
git commit -m "feat(rag): add cosine similarity score threshold filter"

# Step 5: Push your branch
git push origin feat/rag-backend      # Harshith
git push origin feat/react-frontend   # Rohith
git push origin feat/docs-integration # Shashank

# Step 6: Go to code.swecha.org → open a Merge Request (MR)
#   Source branch: your feature branch
#   Target branch: main
#   Get at least 1 teammate to review it
```

---

### If you are forking (Rohith & Shashank)

```bash
# 1. Go to https://code.swecha.org/Harshith_2006/constitutiongpt
# 2. Click Fork → select your own account
# 3. Clone your fork
git clone https://code.swecha.org/<your-username>/constitutiongpt.git
cd constitutiongpt

# 4. Create your branch and push
git checkout -b feat/react-frontend    # Rohith
git checkout -b feat/docs-integration  # Shashank

git add .
git commit -m "feat(frontend): add React chat UI with Tailwind CSS"
git push origin feat/react-frontend

# 5. Open MR from your fork → Harshith_2006/constitutiongpt → main
```

---

### Merging into main (for demo/release)

```bash
# Only Harshith does this after reviewing all MRs
git checkout main
git pull origin main
git merge feat/rag-backend
git push origin main
```

---

### Handling merge conflicts

```bash
# If git tells you there's a conflict after merging:
git status                        # see which files conflict

# Open the conflicting file — look for:
# <<<<<<< HEAD
# your changes
# =======
# their changes
# >>>>>>> branch-name

# Edit the file to keep the right code, then:
git add <resolved-file>
git commit -m "fix: resolve merge conflict in rag.py"
```

---

## ✅ Merge Request Checklist

Before opening a Merge Request, make sure:

- [ ] Code runs without errors (`python app.py` / `npm run dev`)
- [ ] No `.env` file or `vector_store.pkl` accidentally committed
- [ ] No `node_modules/` or `.venv/` in the commit
- [ ] No `.DS_Store` or OS junk files committed
- [ ] Commit messages follow the convention above
- [ ] At least one teammate has reviewed the MR

---

## 🚫 What NOT to Commit

```
# Python
.venv/
__pycache__/
*.pyc
*.pkl                  ← vector store cache
.env                   ← API keys — NEVER commit this

# Node
node_modules/
dist/

# OS
.DS_Store
Thumbs.db
```

---

## 🧪 Before Pushing — Quick Checks

```bash
# Backend (Harshith / Shashank): does it start?
cd backend && python app.py

# Backend: does the health check pass?
curl http://localhost:5000/health

# Frontend (Rohith): does it build?
cd frontend && npm run build

# Frontend: does it run in dev?
npm run dev
```

---

## 💬 Team Communication

- **Harshith** owns `main` — only he merges MRs into main
- **Rohith & Shashank** fork and send MRs from their forks
- Coordinate on **WhatsApp** before starting a feature to avoid conflicts
- Commit **often** — small commits are easier to review and debug

---

## 🆘 Common Git Issues

| Problem | Fix |
|---------|-----|
| `git push` rejected (403) | Fork the repo and push to your fork instead |
| `git push` rejected (non-fast-forward) | Run `git pull origin <branch>` first, then push |
| Committed `.env` by mistake | `git rm --cached backend/.env` then commit |
| Wrong commit message | `git commit --amend -m "correct message"` (before pushing) |
| Need to undo last commit | `git reset --soft HEAD~1` (keeps your changes) |
| Accidentally on wrong branch | `git stash`, `git checkout correct-branch`, `git stash pop` |
| `.DS_Store` committed | `git rm --cached .DS_Store` then add to `.gitignore` |