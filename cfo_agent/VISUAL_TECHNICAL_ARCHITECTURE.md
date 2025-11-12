# CFO Intelligence Platform - Technical Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                           CFO INTELLIGENCE PLATFORM                                     │
│                          Technical Architecture Diagram                                 │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘


┌──────────────────────┐
│                      │
│   👥 CFO Analysts    │────────┐
│   & Managers         │        │
│                      │        │
└──────────────────────┘        │
                                │ Question + Context
                                │
                                ▼
                    ┌───────────────────────────┐
                    │                           │
                    │   🎯 QUERY ROUTER         │
                    │   (Intent Classifier)     │
                    │   • GPT-4o-mini           │
                    │   • Detects query type    │
                    │                           │
                    └───────────┬───────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
    │                  │ │              │ │                  │
    │  📊 SQL AGENT    │ │ 📚 RAG AGENT │ │ 🔄 HYBRID AGENT  │
    │  (Structured)    │ │ (Unstructured│ │ (SQL + RAG)      │
    │                  │ │              │ │                  │
    │  LangGraph       │ │ Vector Search│ │ Orchestrator     │
    │  5-Node Pipeline │ │ + LLM Format │ │ Parallel Exec    │
    │                  │ │              │ │                  │
    └────────┬─────────┘ └──────┬───────┘ └────────┬─────────┘
             │                  │                  │
             │                  │                  │ (Parallel)
             │                  │         ┌────────┴────────┐
             │                  │         │                 │
             ▼                  ▼         ▼                 ▼
    ┌─────────────────┐ ┌─────────────────┐        ┌─────────────────┐
    │                 │ │                 │        │                 │
    │  🗄️ PostgreSQL  │ │  🧠 Vector DB   │        │  🗄️ PostgreSQL  │
    │  (Structured)   │ │  (pgvector)     │        │  (Both Sources) │
    │                 │ │                 │        │                 │
    │  • Quarterly    │ │  • 10-K Chunks  │        │  • Metrics      │
    │  • Annual       │ │  • Embeddings   │        │  • Documents    │
    │  • Stock Prices │ │  • Metadata     │        │                 │
    │                 │ │                 │        │                 │
    └────────┬────────┘ └────────┬────────┘        └────────┬────────┘
             │                   │                          │
             │                   │                          │
             │                   │         ┌────────────────┘
             │                   │         │
             │                   │         ▼
             │                   │  ┌──────────────────┐
             │                   │  │                  │
             │                   │  │  🤖 LLM SYNTHESIS│
             │                   │  │  (GPT-4o-mini)   │
             │                   │  │                  │
             │                   │  │  Combines SQL    │
             │                   │  │  + RAG Results   │
             │                   │  │                  │
             │                   │  └────────┬─────────┘
             │                   │           │
             └───────────────────┴───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │                        │
                    │  📈 VISUALIZATION      │
                    │  ENGINE                │
                    │                        │
                    │  • Chart Generator     │
                    │  • Metric Detector     │
                    │  • Plotly Renderer     │
                    │                        │
                    └───────────┬────────────┘
                                │
                                │ Answers + Charts
                                │
                                ▼
                    ┌───────────────────────────┐
                    │                           │
                    │  💻 STREAMLIT UI          │────────► React + FastAPI
                    │  (Interactive Dashboard)  │
                    │                           │
                    └───────────────────────────┘
                                │
                                │ Export
                                │
                                ▼
                    ┌───────────────────────────┐
                    │                           │
                    │  📊 Built-in Dashboard    │────────► Dashboard & Reports
                    │  & Data Exports           │
                    │                           │
                    └───────────────────────────┘
                                │
                                │ Notifications
                                │
                                ▼
                    ┌───────────────────────────┐
                    │                           │
                    │  📧 Email + Slack         │────────► Email + Slack
                    │  Integration              │          Integration
                    │                           │
                    └───────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                              DATA SOURCES & PROCESSING                                  │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│                      │
│  📄 Data Sources     │
│                      │
│  • Quarterly Metrics │
│  • Annual Metrics    │
│  • Stock Prices      │──────────┐
│  • 10-K Filings      │          │
│  • 10-Q Filings      │          │
│                      │          │
└──────────────────────┘          │
                                  │ Embedding
                                  │
                                  ▼
                      ┌───────────────────────────┐
                      │                           │
                      │  ⚙️ ETL + Processing      │
                      │                           │
                      │  • OpenAI Embeddings      │
                      │  • Text Chunking          │
                      │  • Metadata Extraction    │
                      │                           │
                      └───────────┬───────────────┘
                                  │
                                  │ Storage
                                  │
                                  ▼
                      ┌───────────────────────────┐
                      │                           │
                      │  🗄️ PostgreSQL + pgvector│
                      │  (Supabase)               │
                      │                           │
                      │  • Structured Tables      │
                      │  • Vector Embeddings      │
                      │  • Hybrid Queries         │
                      │                           │
                      └───────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                              AGENT DETAILS                                              │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────┐
│  📊 SQL AGENT (Structured Data)                                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  Pipeline: LangGraph State Machine (5 Nodes)                                          │
│                                                                                        │
│  1. PLANNER (GPT-4o-mini)                                                             │
│     Input: Question + Session Context                                                 │
│     Output: {intent, params, metrics}                                                 │
│                                                                                        │
│  2. TICKER RESOLVER                                                                   │
│     Fuzzy Matching: "Apple" → "AAPL"                                                  │
│     Cache: ticker_cache                                                               │
│                                                                                        │
│  3. SQL GENERATOR (GPT-4o-mini)                                                       │
│     Input: Plan + Schema Whitelist                                                    │
│     Output: PostgreSQL Query                                                          │
│                                                                                        │
│  4. SQL EXECUTOR                                                                      │
│     Connection Pool: asyncpg                                                          │
│     Execute: Against PostgreSQL                                                       │
│                                                                                        │
│  5. RESPONSE FORMATTER (GPT-4o-mini)                                                  │
│     Input: Raw Data + Question                                                        │
│     Output: Natural Language Answer                                                   │
│                                                                                        │
│  Performance: 1-2 seconds | Success Rate: 91.9%                                       │
└────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────┐
│  📚 RAG AGENT (Unstructured Data - 10-K Filings)                                      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  Pipeline: Enhanced Table Retrieval                                                   │
│                                                                                        │
│  1. QUERY ENHANCEMENT                                                                 │
│     Add Keywords: "table", "segment", "breakdown"                                     │
│                                                                                        │
│  2. VECTOR SEARCH                                                                     │
│     Embedding: OpenAI text-embedding-3-small (1536 dims)                              │
│     Database: PostgreSQL pgvector                                                     │
│     Retrieve: Top 10 chunks                                                           │
│                                                                                        │
│  3. RE-RANKING (Table Likelihood Scoring)                                             │
│     Factors:                                                                          │
│     • Semantic similarity (0.0-1.0)                                                   │
│     • Table indicators (+0.1)                                                         │
│     • Dollar signs (+0.05)                                                            │
│     • "Products" + "Services" (+0.3)                                                  │
│     • Numbers, percentages, word count                                                │
│     Return: Top 3 chunks                                                              │
│                                                                                        │
│  4. LLM FORMATTING (GPT-4o-mini)                                                      │
│     Convert: Raw text → Markdown tables                                               │
│     Cleanup: Remove extra whitespace                                                  │
│                                                                                        │
│  Performance: 3-5 seconds | Accuracy: 85% table retrieval                             │
└────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────┐
│  🔄 HYBRID AGENT (SQL + RAG Combined)                                                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  Pipeline: Master Orchestrator                                                        │
│                                                                                        │
│  1. QUERY CLASSIFICATION (GPT-4o-mini)                                                │
│     Detect: HYBRID intent                                                             │
│     Extract: Entities, keywords                                                       │
│                                                                                        │
│  2. PARALLEL EXECUTION (asyncio.gather)                                               │
│     ┌─────────────────┬─────────────────┐                                            │
│     │  SQL Agent      │  RAG Agent      │                                            │
│     │  (2-3s)         │  (3-4s)         │                                            │
│     │  Gets numbers   │  Gets context   │                                            │
│     └─────────────────┴─────────────────┘                                            │
│                                                                                        │
│  3. LLM SYNTHESIS (GPT-4o-mini)                                                       │
│     Combine: SQL data + RAG insights                                                  │
│     Max Tokens: 800 (concise)                                                         │
│     Output: Unified answer with citations                                             │
│                                                                                        │
│  Performance: 6-10 seconds | Optimization: Parallel execution                         │
└────────────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                              TECHNOLOGY STACK                                           │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

Backend:
  • Framework: FastAPI
  • Orchestration: LangGraph (State Machine)
  • Async: asyncio, asyncpg
  • LLM: OpenAI GPT-4o-mini
  • Embeddings: OpenAI text-embedding-3-small

Frontend:
  • Framework: Streamlit
  • Visualization: Plotly
  • HTTP Client: requests

Database:
  • Primary: PostgreSQL (Supabase)
  • Vector Extension: pgvector
  • Connection Pool: asyncpg
  • Indexing: HNSW (vector similarity)

Infrastructure:
  • Backend: http://localhost:8000 (FastAPI)
  • Frontend: http://localhost:8501 (Streamlit)
  • Deployment: Local/Cloud-ready


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                              LLM USAGE SUMMARY                                          │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

SQL Agent (3 LLM calls):
  1. Planner: GPT-4o-mini (plan generation)
  2. SQL Generator: GPT-4o-mini (SQL query)
  3. Response Formatter: GPT-4o-mini (natural language)

RAG Agent (1 LLM call):
  1. Table Formatter: GPT-4o-mini (markdown tables)

Hybrid Agent (5 LLM calls):
  1. Classifier: GPT-4o-mini (intent detection)
  2-4. SQL Agent: 3 calls (planner, generator, formatter)
  5. Synthesizer: GPT-4o-mini (combine results)

All using GPT-4o-mini for speed and cost efficiency


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                              PERFORMANCE METRICS                                        │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┬──────────┬──────────────┬───────────┐
│ Agent           │ Latency  │ Success Rate │ LLM Calls │
├─────────────────┼──────────┼──────────────┼───────────┤
│ SQL Agent       │ 1-2s     │ 91.9%        │ 3         │
│ RAG Agent       │ 3-5s     │ 85%          │ 1         │
│ Hybrid Agent    │ 6-10s    │ Working      │ 5         │
│ Visualization   │ 2-3s     │ N/A          │ 0         │
└─────────────────┴──────────┴──────────────┴───────────┘
```
