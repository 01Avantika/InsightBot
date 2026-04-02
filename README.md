# InsightBot — AI-Powered Data Analytics Platform

InsightBot is a full-stack AI data analytics platform that lets anyone — technical or not — upload a dataset or document and instantly get automated analysis, interactive visualizations, AI-generated insights, and conversational Q&A. No code required.

---

## Features

| # | Feature | Description |
|---|---------|-------------|
| 01 | Secure Authentication | Login / signup with bcrypt password hashing and persistent SQLite storage |
| 02 | Multi-Format Upload | CSV, Excel (.xlsx/.xls), PDF — up to 100 MB. Resume previous files anytime |
| 03 | Automated EDA | Shape, types, missing values, distributions, outliers, correlations — auto-generated |
| 04 | Dynamic Visualizations | 6 chart types (scatter, bar, line, histogram, box, pie) via a custom chart builder |
| 05 | AI-Generated Insights | Executive summaries powered by Groq, OpenAI GPT-4o, or Google Gemini |
| 06 | Conversational Q&A | Natural language questions answered by Pandas engine + LLM fallback |
| 07 | PDF Document Q&A | FAISS vector index enables RAG-based answers over any PDF |
| 08 | AutoML Predictions | Automated classification/regression pipeline with feature importance and AI explanation |
| 09 | History & Export | All sessions persisted. Resume any conversation. Download full analysis report |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | Python 3.11+ |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly, Seaborn, Matplotlib |
| Machine Learning | Scikit-learn |
| LLM Orchestration | LangChain |
| LLM Providers | Groq (Llama 3.1), OpenAI GPT-4o-mini, Google Gemini 1.5 |
| Document Q&A | LangChain + FAISS + Sentence Transformers |
| Database | SQLite via SQLAlchemy |
| Auth | bcrypt |
| PDF Parsing | PDFPlumber, PyPDF |

---

## Project Structure

```
insightbot2/
├── app.py                   # Entry point — redirects to landing page
├── requirements.txt
├── .env.example             # API key template
├── .streamlit/
│   └── config.toml          # Dark theme defaults
│
├── pages/
│   ├── home.py              # Landing page
│   ├── login.py             # Auth — login & signup
│   ├── dashboard.py         # Main dashboard with metrics & report download
│   ├── analyze.py           # File upload + EDA + AutoML + AI insights
│   ├── chat.py              # Conversational Q&A
│   └── history.py           # Full activity history
│
├── utils/
│   ├── eda.py               # EDA engine — stats, charts, auto-visualization
│   ├── llm.py               # LLM abstraction — Groq / OpenAI / Gemini / fallback
│   ├── file_handler.py      # File I/O, PDF extraction, format validation
│   └── theme.py             # Shared dark/light theme CSS helper
│
├── db/
│   ├── database.py          # SQLite schema + all CRUD operations
│   └── insightbot.db        # Auto-created on first run
│
└── uploads/                 # User-uploaded files (auto-created)
```

---

## Database Schema

```sql
users     (id, username, email, password_hash, created_at)
uploads   (id, user_id, filename, file_type, file_path, file_size, uploaded_at)
analyses  (id, user_id, upload_id, analysis, insights, created_at)
chats     (id, user_id, upload_id, role, message, created_at)
```

---

## Installation & Setup

### 1. Unzip and enter the project folder

```bash
cd insightbot2
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt --only-binary :all:
```

> If any package fails, install it individually:
> ```bash
> pip install <package-name> --only-binary :all:
> ```

### 4. Configure API keys

```bash
copy .env.example .env      # Windows
```

Open `.env` and add your key — **no spaces around `=`**:

```env
# Choose one or more:
GROQ_API_KEY=gsk_your_key_here
OPENAI_API_KEY=sk_your_key_here
GOOGLE_API_KEY=AIza_your_key_here
```


> **No API key?** The app still works fully for EDA, charts, and Pandas-based Q&A. Only AI insights and natural language chat require a key.

### 5. Run the app

```bash
streamlit run app.py
```

Opens at **http://localhost:8501**

---

## Usage Guide

### Analyzing a CSV / Excel File

1. Go to **Upload & Analyze** → upload your file
2. View auto-generated statistics, column details, and charts
3. Use the **Custom Chart Builder** to create specific visualizations
4. Click **Generate AI Insights** for executive-level analysis
5. Go to **Chat** → ask questions like:
   - *"What are the key statistics?"*
   - *"Which column has the most missing values?"*
   - *"Show me the correlation between X and Y"*

### Analyzing a PDF

1. Upload a PDF in **Upload & Analyze**
2. Click **Index Document** to build the FAISS vector index
3. Click **Summarize Document** for an AI summary
4. Go to **Chat** → ask questions about the document content

### Running AutoML

1. Upload a CSV/Excel file
2. Scroll to the **AutoML** section in **Upload & Analyze**
3. Select your target column
4. Click **Run AutoML** — the system trains multiple models and picks the best
5. View accuracy metrics, feature importance chart, and AI explanation

### Downloading a Report

1. Go to **Dashboard**
2. Click **Download Report**
3. Choose `.txt` (full report) or `.csv` (uploads summary)

---

## Common Issues & Fixes

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'X'` | `pip install X --only-binary :all:` |
| `No LLM API Key` warning | Add key to `.env` with no spaces around `=` |
| `Gemini 429 quota exceeded` | Switch to Groq (free, 14,400 req/day) |
| Duplicate file shown multiple times | Fixed in latest `analyze.py` — upgrade the file |
| `StreamlitDuplicateElementKey` | Pass unique `key=` to each widget |
| `.env` key not loading | Add `load_dotenv()` at top of `app.py` and `utils/llm.py` |
| numpy / pandas build error on Windows | Use `--only-binary :all:` flag |

---

## Security Notes

- Passwords hashed with **bcrypt** (12 rounds) — never stored in plaintext
- All database queries use **parameterized statements** — no SQL injection
- Files stored with **user-namespaced paths** — no cross-user access
- API keys loaded from `.env` — never hardcoded or committed

---

## Architecture Overview

```
Browser
  │
  ▼
Streamlit Frontend (Multi-page)
  │
  ├── Auth Layer          bcrypt + SQLite
  ├── File Handler        Upload, parse, extract
  ├── EDA Engine          Pandas + Plotly auto-analysis
  ├── AutoML Pipeline     Scikit-learn multi-model training
  ├── LLM Layer           Groq / OpenAI / Gemini abstraction
  │     ├── Data Q&A      Pandas compute + LLM fallback
  │     └── Document Q&A  FAISS RAG pipeline
  └── History Store       SQLite persistence
```

---

*InsightBot — Making Data Intelligence Accessible to Everyone*