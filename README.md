# BFSI Call Center AI Assistant

## Overview

A lightweight, compliant, and efficient AI assistant for handling Banking, Financial Services, and Insurance (BFSI) call center queries. The system employs a **3-tier response pipeline** to ensure fast, accurate, and standardized responses while maintaining safety and regulatory compliance.

### Key Features

**Three-Tier Response Pipeline**
- **Tier 1**: Dataset Similarity Matching (150+ curated responses)
- **Tier 2**: RAG-Augmented Generation (knowledge-grounded)
- **Tier 3**: Fine-Tuned Small Language Model (novel queries)

**Safety & Compliance**
- Built-in guardrails for unsafe/out-of-domain queries
- RBI-compliant response generation
- Privacy and data security enforced

**Efficient & Lightweight**
- Runs locally (no cloud dependency)
- Small LLM (1.1B parameters)
- Fast inference (<2 seconds per query)

**Production Ready**
- Interactive Streamlit demo
- API-ready architecture
- Comprehensive documentation

---

## System Architecture

```
User Query
    ↓
┌─────────────────────────────────────┐
│    Safety & Compliance Guardrails   │ ← Blocks unsafe/out-of-domain
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ TIER 1: Dataset Similarity Matching  │ ← 150+ curated responses
│ (Embedding-based retrieval)          │   (85% queries matched)
└─────────────────────────────────────┘
    ↓ (if no match)
┌─────────────────────────────────────┐
│ TIER 2: RAG + SLM Generation         │ ← Knowledge-grounded generation
│ (Complex financial queries)          │   (10% queries)
└─────────────────────────────────────┘
    ↓ (if no RAG docs)
┌─────────────────────────────────────┐
│ TIER 3: Fine-Tuned SLM               │ ← Direct SLM generation
│ (Fallback generation)                │   (5% queries)
└─────────────────────────────────────┘
    ↓
Final Response (with confidence score & source)
```

