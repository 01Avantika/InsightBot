"""
utils/llm.py — LLM abstraction layer for InsightBot
Supports OpenAI GPT, Google Gemini, and a fallback rule-based engine
"""

import os
import json
import re
import pandas as pd
from typing import Optional


# ── LLM Provider Detection ────────────────────────────────────────────────────

def get_llm_provider() -> str:
    """Determine which LLM provider to use based on available API keys."""
    if os.getenv("GROQ_API_KEY"):
        return "groq"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("GOOGLE_API_KEY"):
        return "gemini"
    return "fallback"


def call_llm(prompt: str, system: str = "", max_tokens: int = 1500) -> str:
    provider = get_llm_provider()
    if provider == "groq":
        return _call_groq(prompt, system, max_tokens)
    elif provider == "openai":
        return _call_openai(prompt, system, max_tokens)
    elif provider == "gemini":
        return _call_gemini(prompt, system, max_tokens)
    else:
        return _fallback_response(prompt)


def _call_openai(prompt: str, system: str, max_tokens: int) -> str:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI Error] {e}"


def _call_gemini(prompt: str, system: str, max_tokens: int) -> str:
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-2.0-flash")
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = model.generate_content(
            full_prompt,
            generation_config={"max_output_tokens": max_tokens, "temperature": 0.3},
        )
        return response.text.strip()
    except Exception as e:
        return f"[Gemini Error] {e}"
    
def _call_groq(prompt: str, system: str, max_tokens: int) -> str:
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Groq Error] {e}"



def _fallback_response(prompt: str) -> str:
    """Rule-based fallback when no LLM key is set."""
    prompt_lower = prompt.lower()
    if any(w in prompt_lower for w in ["insight", "summary", "overview", "describe"]):
        return (
            "⚠️ **No LLM API key configured.** Add OPENAI_API_KEY or GOOGLE_API_KEY to your .env file.\n\n"
            "**Basic Auto-Summary:** The dataset has been loaded and basic EDA has been performed. "
            "Review the charts and statistics above for patterns and insights."
        )
    return (
        "⚠️ **No LLM API key configured.**\n\n"
        "To enable AI-powered Q&A and insights, please add your API key to the `.env` file:\n"
        "```\nOPENAI_API_KEY=sk-...\n# or\nGOOGLE_API_KEY=AIza...\n```"
    )


# ── AI Insight Generation ─────────────────────────────────────────────────────

INSIGHT_SYSTEM = """You are an expert data analyst. Analyze the dataset summary provided and generate:
1. Key findings (3-5 bullet points)
2. Notable patterns or anomalies
3. Business recommendations
4. Potential data quality issues

Be concise, specific, and actionable. Use markdown formatting."""


def generate_insights(summary_text: str, filename: str = "") -> str:
    prompt = f"Dataset: {filename}\n\n{summary_text}\n\nGenerate executive insights for this dataset."
    return call_llm(prompt, system=INSIGHT_SYSTEM, max_tokens=1200)


# ── Data Q&A ──────────────────────────────────────────────────────────────────

DATA_QA_SYSTEM = """You are an expert data analyst assistant. Answer questions about the dataset using the provided summary and statistics. 
Be precise, cite specific numbers where possible, and suggest follow-up analyses. 
If asked to perform calculations or aggregations, explain what you would compute. Use markdown for clarity."""


def answer_data_question(question: str, df_summary: str, chat_history: list = None) -> str:
    history_text = ""
    if chat_history:
        history_text = "\n".join([
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['message']}"
            for m in chat_history[-6:]  # Last 3 exchanges
        ])
        history_text = f"\nPrevious conversation:\n{history_text}\n"

    prompt = f"""Dataset context:
{df_summary}
{history_text}
User question: {question}

Answer the question about this dataset:"""
    return call_llm(prompt, system=DATA_QA_SYSTEM, max_tokens=1000)


def pandas_query(df: pd.DataFrame, question: str) -> tuple[str, pd.DataFrame | None]:
    """Try to answer a question with actual pandas computation."""
    q = question.lower()
    result_df = None
    answer = ""

    try:
        num_cols = df.select_dtypes(include="number").columns.tolist()
        cat_cols = df.select_dtypes(exclude="number").columns.tolist()

        if any(w in q for w in ["average", "mean"]):
            if num_cols:
                result = df[num_cols].mean().round(2)
                answer = f"**Column Means:**\n{result.to_string()}"

        elif any(w in q for w in ["max", "maximum", "highest", "largest"]):
            if num_cols:
                result = df[num_cols].max()
                answer = f"**Maximum Values:**\n{result.to_string()}"

        elif any(w in q for w in ["min", "minimum", "lowest", "smallest"]):
            if num_cols:
                result = df[num_cols].min()
                answer = f"**Minimum Values:**\n{result.to_string()}"

        elif any(w in q for w in ["count", "how many", "total rows"]):
            answer = f"**Total rows:** {len(df):,}\n**Total columns:** {len(df.columns)}"

        elif any(w in q for w in ["missing", "null", "nan"]):
            miss = df.isnull().sum()
            miss = miss[miss > 0]
            if len(miss):
                answer = f"**Missing Values:**\n{miss.to_string()}"
            else:
                answer = "✅ No missing values found in the dataset."

        elif any(w in q for w in ["duplicate"]):
            n = df.duplicated().sum()
            answer = f"**Duplicate rows:** {n}"

        elif "correlation" in q and len(num_cols) >= 2:
            corr = df[num_cols].corr().round(3)
            result_df = corr
            answer = "**Correlation Matrix:**"

        elif any(w in q for w in ["describe", "summary", "statistics"]):
            result_df = df.describe().round(2)
            answer = "**Descriptive Statistics:**"

        elif any(w in q for w in ["shape", "size", "dimension"]):
            answer = f"**Shape:** {df.shape[0]:,} rows × {df.shape[1]} columns"

    except Exception:
        pass

    return answer, result_df


# ── PDF Q&A with FAISS ────────────────────────────────────────────────────────

def build_faiss_index(file_path: str):
    """Build FAISS index from PDF for document Q&A."""
    try:
        from langchain_community.document_loaders import PDFPlumberLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.vectorstores import FAISS
        from langchain_openai import OpenAIEmbeddings
        from langchain_community.embeddings import HuggingFaceEmbeddings

        loader = PDFPlumberLoader(file_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)

        # Try OpenAI embeddings first, fall back to HuggingFace
        if os.getenv("OPENAI_API_KEY"):
            embeddings = OpenAIEmbeddings()
        else:
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        vectorstore = FAISS.from_documents(chunks, embeddings)
        return vectorstore, len(chunks)

    except Exception as e:
        return None, str(e)


def answer_pdf_question(question: str, vectorstore, chat_history: list = None) -> str:
    """Answer a question from the PDF using RAG."""
    try:
        docs = vectorstore.similarity_search(question, k=4)
        context = "\n\n".join([d.page_content for d in docs])

        history_text = ""
        if chat_history:
            history_text = "\n".join([
                f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['message']}"
                for m in chat_history[-4:]
            ])

        system = """You are a helpful assistant that answers questions based on document content.
Use only the provided context. If the answer isn't in the context, say so clearly."""

        prompt = f"""Context from document:
{context}

{f'Previous conversation:{chr(10)}{history_text}' if history_text else ''}

Question: {question}

Answer based on the document:"""

        return call_llm(prompt, system=system, max_tokens=800)

    except Exception as e:
        return f"Error during PDF Q&A: {e}"
