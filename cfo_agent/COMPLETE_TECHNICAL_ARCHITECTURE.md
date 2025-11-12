# 🏗️ Complete Technical Architecture - CFO Intelligence Platform

## System Overview

**Three Query Pipelines:**
1. **Structured (SQL)**: Fast database queries (1-2s)
2. **Unstructured (RAG)**: 10-K semantic search (3-5s)
3. **Hybrid**: Combined SQL + RAG (6-10s)

**Plus Visualization Pipeline**: Chart generation (2-3s)

---

## 🔄 PIPELINE 1: Structured Query (SQL)

### Flow Diagram
```
User Question → Streamlit → FastAPI /ask → LangGraph → PostgreSQL → Response
     ↓
"Show Apple, Microsoft revenue Q1 2023"
     ↓
┌─────────────────────────────────────────────┐
│ LangGraph State Machine (5 Nodes)          │
├─────────────────────────────────────────────┤
│ 1. PLANNER (LLM: GPT-4o-mini)              │
│    Input: Question + context                │
│    Output: {intent, params, metrics}        │
│                                             │
│ 2. TICKER RESOLVER                          │
│    "Apple" → "AAPL" (fuzzy match)          │
│                                             │
│ 3. SQL GENERATOR (LLM: GPT-4o-mini)        │
│    Input: Plan + schema whitelist          │
│    Output: SELECT ... FROM quarterly_metrics│
│                                             │
│ 4. SQL EXECUTOR                             │
│    Execute against PostgreSQL               │
│    Returns: Raw data rows                   │
│                                             │
│ 5. RESPONSE FORMATTER (LLM: GPT-4o-mini)   │
│    Input: Raw data + question               │
│    Output: Natural language answer          │
└─────────────────────────────────────────────┘
     ↓
"Apple: $94.8B, Microsoft: $52.9B in Q1 2023"
```

### Components
- **LLMs**: 3 calls to GPT-4o-mini (planner, generator, formatter)
- **Database**: PostgreSQL (Supabase) with connection pooling
- **Tables**: `quarterly_metrics`, `annual_metrics`, `daily_stock_prices`
- **Caches**: Schema whitelist, ticker mapping, session memory

### Performance
- **Latency**: 1-2 seconds
- **Success Rate**: 91.9%

---

## 📚 PIPELINE 2: Unstructured Query (10-K RAG)

### Flow Diagram
```
User Question → Streamlit → Table Retriever → Vector DB → LLM Format → Response
     ↓
"Show Apple's gross margin breakdown from 10-K"
     ↓
┌─────────────────────────────────────────────┐
│ Enhanced Table Retriever                    │
├─────────────────────────────────────────────┤
│ 1. QUERY ENHANCEMENT                        │
│    Add keywords: "table", "segment", etc    │
│                                             │
│ 2. VECTOR SEARCH                            │
│    Embedding: OpenAI text-embedding-3-small │
│    PostgreSQL pgvector similarity search    │
│    Retrieve top 10 chunks                   │
│                                             │
│ 3. RE-RANKING (Table Likelihood)            │
│    Score factors:                           │
│    • Semantic similarity (0.0-1.0)          │
│    • Table indicators (+0.1 each)           │
│    • Dollar signs (+0.05 each)              │
│    • "Products" + "Services" (+0.3)         │
│    • Numbers, percentages, word count       │
│    Return top 3 chunks                      │
│                                             │
│ 4. LLM FORMATTING (GPT-4o-mini)            │
│    Convert raw text to markdown tables      │
│                                             │
│ 5. WHITESPACE CLEANUP                       │
│    Remove extra blank lines                 │
└─────────────────────────────────────────────┘
     ↓
Formatted table with Products vs Services breakdown
```

### Components
- **Vector DB**: PostgreSQL with pgvector extension
- **Embedding Model**: OpenAI text-embedding-3-small (1536 dims)
- **LLM**: GPT-4o-mini for formatting
- **Table Retriever**: Custom scoring algorithm

### Performance
- **Latency**: 3-5 seconds (10-15 with formatting)
- **Accuracy**: 85% table retrieval success

---

## 🔄 PIPELINE 3: Hybrid Query (SQL + RAG)

### Flow Diagram
```
User Question → FastAPI /ask/hybrid → MasterOrchestrator → Parallel Execution → Synthesis
     ↓
"What drove Apple's margin changes with 10-K citations?"
     ↓
┌─────────────────────────────────────────────┐
│ MasterOrchestrator                          │
├─────────────────────────────────────────────┤
│ 1. QUERY CLASSIFICATION (GPT-4o-mini)      │
│    Detect: HYBRID intent                    │
│    Extract: entities, keywords              │
│                                             │
│ 2. PARALLEL EXECUTION (asyncio.gather)     │
│    ┌──────────────┬──────────────┐         │
│    │ SQL Agent    │ RAG Agent    │         │
│    │ (2-3s)       │ (3-4s)       │         │
│    │ Gets numbers │ Gets context │         │
│    └──────────────┴──────────────┘         │
│                                             │
│ 3. LLM SYNTHESIS (GPT-4o-mini)             │
│    Combine SQL data + RAG insights          │
│    Max tokens: 800 (concise)                │
└─────────────────────────────────────────────┘
     ↓
"Margin improved 41.8%→43.3% driven by services (71.7% margin)"
```

### Components
- **QueryClassifier**: LLM-based intent detection
- **AgentCoordinator**: Unified interface to both agents
- **LLMs**: 5 total calls (1 classifier + 3 SQL + 1 RAG + 1 synthesis)

### Performance
- **Latency**: 6-10 seconds
- **Optimization**: Parallel execution (saves 3-4s)

---

## 📈 PIPELINE 4: Visualization

### Flow Diagram
```
User Clicks "View Chart" → /api/visualize → VizDataFetcher → Chart Config → Plotly
     ↓
┌─────────────────────────────────────────────┐
│ Visualization Pipeline                      │
├─────────────────────────────────────────────┤
│ 1. METADATA EXTRACTION                      │
│    From previous query response             │
│    {intent, params, chart_type}             │
│                                             │
│ 2. EXTENDED DATA FETCH                      │
│    Query DB for 5 years of historical data  │
│    (Not just the queried period)            │
│                                             │
│ 3. METRIC DETECTION                         │
│    Analyze question for metrics:            │
│    "revenue" → revenue_b                    │
│    "margin" → gross_margin_pct              │
│                                             │
│ 4. CHART CONFIG GENERATION                  │
│    Create Plotly configuration              │
│    {x_labels, y_values, title, colors}      │
│                                             │
│ 5. RENDER IN STREAMLIT                      │
│    st.plotly_chart() with config            │
└─────────────────────────────────────────────┘
```

### Components
- **VizDataFetcher**: Determines chart applicability
- **Metric Detection**: Keyword matching from question
- **Chart Types**: Line, bar, combo (multi-metric)

### Performance
- **Latency**: 2-3 seconds

---

## 🧠 LLM Usage Map

### Where LLMs Are Used

**Structured Pipeline (3 LLM calls):**
1. Planner: GPT-4o-mini (plan generation)
2. SQL Generator: GPT-4o-mini (SQL query)
3. Response Formatter: GPT-4o-mini (natural language)

**Unstructured Pipeline (1 LLM call):**
1. Table Formatter: GPT-4o-mini (markdown tables)

**Hybrid Pipeline (5 LLM calls):**
1. Classifier: GPT-4o-mini (intent detection)
2-4. SQL Agent: 3 calls (planner, generator, formatter)
5. Synthesizer: GPT-4o-mini (combine results)

**Total LLM Calls:**
- Structured: 3
- Unstructured: 1
- Hybrid: 5

---

## 🗄️ Data Architecture

### PostgreSQL Database

**Tables:**
```sql
-- Structured Data
quarterly_metrics (ticker, quarter, fy, revenue_b, net_income_b, ...)
annual_metrics (ticker, fy, revenue_b, net_income_b, ...)
daily_stock_prices (ticker, date, open_price, close_price, ...)

-- Unstructured Data (Vector DB)
document_chunks (
  chunk_id,
  company_name,
  ticker,
  fiscal_year,
  section,
  section_type,
  chunk_text,
  embedding vector(1536)  -- pgvector
)
```

### Vector Search
- **Index**: HNSW (Hierarchical Navigable Small World)
- **Similarity**: Cosine similarity
- **Embedding**: OpenAI text-embedding-3-small

---

## 🔧 Technology Stack

### Backend
- **Framework**: FastAPI
- **Orchestration**: LangGraph (state machine)
- **Async**: asyncio, asyncpg
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small

### Frontend
- **Framework**: Streamlit
- **Visualization**: Plotly
- **HTTP Client**: requests

### Database
- **Primary**: PostgreSQL (Supabase)
- **Vector Extension**: pgvector
- **Connection Pool**: asyncpg

### Infrastructure
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:8501
- **Deployment**: Local (can deploy to cloud)

---

## 📊 Complete Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                      (Streamlit - Port 8501)                     │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                    User selects mode
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────────┐
│ Structured   │   │ Unstructured │   │ Hybrid           │
│ (SQL)        │   │ (10-K RAG)   │   │ (SQL + RAG)      │
└──────┬───────┘   └──────┬───────┘   └──────┬───────────┘
       │                  │                   │
       │ HTTP POST        │ Direct call       │ HTTP POST
       │                  │                   │
       ▼                  ▼                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                             │
│                      (Port 8000)                                 │
│                                                                  │
│  /ask           Streamlit           /ask/hybrid                 │
│  (SQL)          (RAG Direct)        (Orchestrator)              │
└──────┬──────────────────┬──────────────────┬────────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────────┐
│ LangGraph    │   │ Table        │   │ Master           │
│ (5 nodes)    │   │ Retriever    │   │ Orchestrator     │
└──────┬───────┘   └──────┬───────┘   └──────┬───────────┘
       │                  │                  │
       │                  │                  │ (parallel)
       │                  │           ┌──────┴──────┐
       │                  │           │             │
       ▼                  ▼           ▼             ▼
┌──────────────┐   ┌──────────────┐   │      ┌──────────────┐
│ PostgreSQL   │   │ PostgreSQL   │   │      │ PostgreSQL   │
│ (Structured) │   │ (pgvector)   │   │      │ (Both)       │
└──────────────┘   └──────────────┘   │      └──────────────┘
       │                  │           │             │
       │                  │           └──────┬──────┘
       │                  │                  │
       │                  │                  ▼
       │                  │           ┌──────────────────┐
       │                  │           │ LLM Synthesis    │
       │                  │           │ (GPT-4o-mini)    │
       │                  │           └──────┬───────────┘
       │                  │                  │
       └──────────────────┴──────────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ Response     │
                   │ + viz_metadata│
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ Streamlit    │
                   │ Display      │
                   └──────────────┘
```

---

## 🎯 Query Routing Logic

### How Mode is Determined

**Streamlit (User Selection):**
```python
mode = st.radio("Mode:", [
    "Structured Data (SQL)",
    "Unstructured Data (10-K)",
    "Hybrid (SQL + 10-K)"
])
```

**Routing:**
- **Structured**: → `/ask` endpoint → LangGraph
- **Unstructured**: → Direct TableRetriever call
- **Hybrid**: → `/ask/hybrid` endpoint → MasterOrchestrator

### Hybrid Query Detection (Automatic)

**Keywords that trigger hybrid:**
- "10-K citations"
- "what drove"
- "macro context"
- "business drivers"
- "explain why"

---

## ⚡ Performance Summary

| Pipeline | Latency | Success Rate | LLM Calls |
|----------|---------|--------------|-----------|
| Structured (SQL) | 1-2s | 91.9% | 3 |
| Unstructured (RAG) | 3-5s | 85% | 1 |
| Hybrid | 6-10s | Working | 5 |
| Visualization | 2-3s | N/A | 0 |

---

## 🔐 Security & Best Practices

1. **SQL Injection Prevention**: Schema whitelist, parameterized queries
2. **Rate Limiting**: Session-based throttling
3. **Error Handling**: Graceful degradation, retry logic
4. **Caching**: Schema, ticker, session memory
5. **Connection Pooling**: Efficient database connections

---

## 🚀 Deployment Architecture

```
Production Setup:
├── Frontend: Streamlit (Cloud/Docker)
├── Backend: FastAPI (Cloud/Docker)
├── Database: PostgreSQL (Supabase/Cloud)
├── Vector DB: pgvector (same PostgreSQL)
└── LLM: OpenAI API (external)
```

---

## 📝 Summary

**Three Pipelines, One Platform:**
1. **SQL**: Fast, reliable, quantitative (1-2s)
2. **RAG**: Contextual, qualitative, tables (3-5s)
3. **Hybrid**: Comprehensive, synthesized (6-10s)

**Plus visualization for all query types.**

**Total LLM Calls per Query:**
- SQL: 3
- RAG: 1
- Hybrid: 5

**All powered by GPT-4o-mini for speed and cost efficiency.**
