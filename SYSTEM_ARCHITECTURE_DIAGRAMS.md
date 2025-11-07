# 🏗️ CFO Intelligence Platform - System Architecture Diagrams

## Visual Architecture Reference

---

## 1. High-Level System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                      (Streamlit Web App)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI REST API                           │
│                    (http://localhost:8000)                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MASTER CFO ORCHESTRATOR                       │
│                      (Query Classifier)                         │
└─────────┬───────────────────────────────────────┬───────────────┘
          │                                       │
          ▼                                       ▼
┌──────────────────────┐              ┌──────────────────────────┐
│  STRUCTURED AGENT    │              │  UNSTRUCTURED AGENT      │
│  (SQL-Based)         │              │  (RAG-Based)             │
│                      │              │                          │
│  • LangGraph         │              │  • Vector Search         │
│  • Template SQL      │              │  • Semantic Retrieval    │
│  • 39 DB Views       │              │  • GPT-4o Reasoning      │
└──────────┬───────────┘              └──────────┬───────────────┘
           │                                     │
           ▼                                     ▼
┌──────────────────────┐              ┌──────────────────────────┐
│  POSTGRESQL DB       │              │  VECTOR DATABASE         │
│  (Supabase)          │              │  (pgvector)              │
│                      │              │                          │
│  • Financial Data    │              │  • 10-K Embeddings       │
│  • Macro Indicators  │              │  • Document Chunks       │
│  • Stock Prices      │              │  • Metadata              │
└──────────────────────┘              └──────────────────────────┘
```

---

## 2. Structured Agent Pipeline (6-Node LangGraph)

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER QUESTION                            │
│          "Show Apple's revenue with CPI for Q2 2023"            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  NODE 1: QUERY DECOMPOSER                                       │
│  ────────────────────────────────────────────────────────       │
│  Input: Natural language question                               │
│  Process:                                                        │
│    • Extract entities (Apple → AAPL)                            │
│    • Detect intent (macro_context_quarterly)                    │
│    • Parse period (Q2 2023 → fy=2023, fq=2)                     │
│    • Break into tasks                                           │
│  Output: Structured task list                                   │
│  LLM: GPT-4o                                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  NODE 2: ENTITY RESOLVER                                        │
│  ────────────────────────────────────────────────────────       │
│  Input: Task with entities ["AAPL"]                             │
│  Process:                                                        │
│    • Validate ticker exists in database                         │
│    • Resolve company_id (1 for Apple)                           │
│    • Handle aliases (GOOGL → GOOG)                              │
│  Output: Resolved entities with IDs                             │
│  Database: dim_company lookup                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  NODE 3: INTENT ROUTER & TASK PLANNER                           │
│  ────────────────────────────────────────────────────────       │
│  Input: Intent + Entities + Period                              │
│  Process:                                                        │
│    • Match intent to template catalog (29 templates)            │
│    • Select: "complete_macro_context_quarterly"                 │
│    • Choose view: vw_company_macro_context_quarter              │
│    • Build parameters: {ticker: AAPL, fy: 2023, fq: 2}          │
│  Output: Execution plan with SQL template                       │
│  Catalog: templates.json                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  NODE 4: SQL BUILDER & EXECUTOR                                 │
│  ────────────────────────────────────────────────────────       │
│  Input: SQL template + parameters                               │
│  Process:                                                        │
│    • Validate view is whitelisted (18 approved)                 │
│    • Bind parameters (SQL injection prevention)                 │
│    • Execute SELECT query (read-only)                           │
│    • Apply 30s timeout                                          │
│  Output: Raw query results                                      │
│  Database: PostgreSQL execution                                 │
│                                                                  │
│  SQL Generated:                                                  │
│  SELECT ticker, name, fiscal_year, fiscal_quarter,              │
│         revenue/1e9 as revenue_b, net_income/1e9 as net_income_b,│
│         gross_margin, operating_margin, net_margin,              │
│         gdp/1e3 as gdp_t, cpi, unemployment_rate,                │
│         fed_funds_rate, sp500_index                              │
│  FROM vw_company_macro_context_quarter                           │
│  WHERE ticker = 'AAPL' AND fiscal_year = 2023 AND fiscal_quarter = 2│
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  NODE 5: CITATION FETCHER                                       │
│  ────────────────────────────────────────────────────────       │
│  Input: Query results                                           │
│  Process:                                                        │
│    • Map columns to data sources                                │
│    • Revenue → ALPHAVANTAGE_FIN (as_reported)                   │
│    • CPI, GDP → FRED                                            │
│    • Stock prices → Yahoo Finance                               │
│    • Fetch metadata (timestamps, source IDs)                    │
│  Output: Citation metadata                                      │
│  Database: fact_data_sources table                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  NODE 6: RESPONSE FORMATTER                                     │
│  ────────────────────────────────────────────────────────       │
│  Input: Results + Citations + Original Question                 │
│  Process:                                                        │
│    • Detect requested metrics (revenue, CPI)                    │
│    • Format numbers (billions, percentages)                     │
│    • Generate natural language summary                          │
│    • Add macro context section                                  │
│    • Append source citations                                    │
│  Output: Final formatted response                               │
│  LLM: GPT-4o (for natural language generation)                  │
│                                                                  │
│  Final Output:                                                   │
│  "Apple Inc. (AAPL) reported revenue of $81.80B for Q2 FY2023.  │
│   Macro context: GDP $26.79T, CPI 304.13, unemployment 3.50%,   │
│   Fed rate 5.08%, S&P 500 4,179.83.                             │
│                                                                  │
│   Sources: ALPHAVANTAGE_FIN (as_reported, 2025-10-12 10:33:18); │
│   YF; FRED"                                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Unstructured Agent Pipeline (RAG)

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER QUESTION                            │
│         "What are Apple's strategic priorities in 2023?"        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: QUERY CLASSIFICATION                                   │
│  ────────────────────────────────────────────────────────       │
│  Input: Natural language question                               │
│  Process:                                                        │
│    • Identify document type (10-K, earnings transcript)         │
│    • Extract company (Apple)                                    │
│    • Extract year (2023)                                        │
│    • Determine search strategy (semantic search)                │
│  Output: Search parameters                                      │
│  LLM: GPT-4o                                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: VECTOR SEARCH                                          │
│  ────────────────────────────────────────────────────────       │
│  Input: Query + Company + Year                                  │
│  Process:                                                        │
│    • Generate query embedding (OpenAI embedding model)          │
│    • Similarity search in pgvector                              │
│    • Filter by metadata (company=Apple, year=2023)              │
│    • Retrieve top-k chunks (k=5)                                │
│    • Re-rank by relevance score                                 │
│  Output: Relevant document chunks                               │
│  Database: Vector embeddings table                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: CONTEXT ASSEMBLY                                       │
│  ────────────────────────────────────────────────────────       │
│  Input: Retrieved chunks                                        │
│  Process:                                                        │
│    • Combine chunks with metadata                               │
│    • Add document headers (company, year, section)              │
│    • Build RAG prompt with context                              │
│    • Limit to 8000 tokens                                       │
│  Output: Formatted prompt for LLM                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: LLM REASONING                                          │
│  ────────────────────────────────────────────────────────       │
│  Input: Question + Retrieved context                            │
│  Process:                                                        │
│    • Analyze document chunks                                    │
│    • Extract strategic priorities                               │
│    • Identify key quotes                                        │
│    • Synthesize insights                                        │
│    • Generate structured answer                                 │
│  Output: Reasoned response with citations                       │
│  LLM: GPT-4o                                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: RESPONSE FORMATTING                                    │
│  ────────────────────────────────────────────────────────       │
│  Input: LLM response                                            │
│  Process:                                                        │
│    • Structure answer with bullet points                        │
│    • Add document references                                    │
│    • Include relevant quotes                                    │
│    • Format citations                                           │
│  Output: Final formatted response                               │
│                                                                  │
│  Final Output:                                                   │
│  "Based on Apple's 2023 10-K filing, their strategic priorities │
│   include:                                                       │
│                                                                  │
│   1. Services Growth: Expanding Apple Music, iCloud, App Store  │
│   2. Privacy & Security: Maintaining user trust                 │
│   3. Ecosystem Integration: Seamless device experience          │
│   4. Sustainability: Carbon neutral by 2030                     │
│   5. Innovation: AR/VR products and AI integration              │
│                                                                  │
│   Source: Apple Inc. 10-K Filing (FY 2023), Business Strategy"  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Database Schema Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      DIMENSION TABLES                           │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  dim_company     │
├──────────────────┤
│  company_id (PK) │
│  ticker          │  ← AAPL, MSFT, AMZN, GOOG, META
│  name            │
│  sector          │
│  industry        │
└──────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        FACT TABLES                              │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│  fact_financials     │
├──────────────────────┤
│  company_id (FK)     │
│  fiscal_year         │
│  fiscal_quarter      │
│  revenue             │  ← Core financial metrics
│  net_income          │
│  operating_income    │
│  gross_profit        │
│  r_and_d_expenses    │
│  sg_and_a_expenses   │
│  cogs                │
│  total_assets        │
│  total_liabilities   │
│  equity              │
│  ... (30+ columns)   │
└──────────────────────┘

┌──────────────────────┐
│  fact_ratios         │
├──────────────────────┤
│  company_id (FK)     │
│  fiscal_year         │
│  fiscal_quarter      │
│  gross_margin        │  ← Calculated ratios
│  operating_margin    │
│  net_margin          │
│  roe                 │
│  roa                 │
│  debt_to_equity      │
│  debt_to_assets      │
│  ... (20+ ratios)    │
└──────────────────────┘

┌──────────────────────┐
│  fact_stock_prices   │
├──────────────────────┤
│  company_id (FK)     │
│  date                │
│  open_price          │  ← Daily stock data
│  close_price         │
│  high_price          │
│  low_price           │
│  volume              │
└──────────────────────┘

┌──────────────────────────┐
│  fact_macro_indicators   │
├──────────────────────────┤
│  date                    │
│  gdp                     │  ← Economic indicators
│  cpi                     │
│  unemployment_rate       │
│  fed_funds_rate          │
│  sp500_index             │
│  ... (15+ indicators)    │
└──────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   MATERIALIZED VIEWS (39 total)                 │
└─────────────────────────────────────────────────────────────────┘

┌────────────────────────────────┐
│  vw_company_complete_quarter   │  ← Main query surface
├────────────────────────────────┤
│  Joins: financials + ratios +  │
│         stock + macro           │
│  Columns: 50+ metrics           │
│  Use: Complete quarterly data   │
└────────────────────────────────┘

┌────────────────────────────────┐
│  vw_growth_quarter             │  ← Growth calculations
├────────────────────────────────┤
│  Metrics: QoQ, YoY growth      │
│  Columns: revenue_qoq,         │
│           revenue_yoy,         │
│           ni_qoq, ni_yoy, etc. │
└────────────────────────────────┘

┌────────────────────────────────┐
│  vw_peer_stats_quarter         │  ← Peer comparisons
├────────────────────────────────┤
│  Metrics: Rankings, percentiles│
│  Columns: revenue_rank,        │
│           margin_percentile    │
└────────────────────────────────┘

┌────────────────────────────────┐
│  vw_company_macro_context_qtr  │  ← Company + Macro
├────────────────────────────────┤
│  Joins: company + macro data   │
│  Columns: financials + GDP,    │
│           CPI, unemployment     │
└────────────────────────────────┘

┌────────────────────────────────┐
│  vw_macro_sensitivity_rolling  │  ← Beta calculations
├────────────────────────────────┤
│  Metrics: 12Q rolling betas    │
│  Columns: beta_nm_cpi_12q,     │
│           beta_gm_ffr_12q      │
└────────────────────────────────┘
```

---

## 5. Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA INGESTION LAYER                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Alpha Vantage│    │     FRED     │    │Yahoo Finance │
│   API        │    │     API      │    │    API       │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       │ Financials        │ Macro Data        │ Stock Prices
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ETL PROCESSING LAYER                         │
│  • Data validation                                              │
│  • Type conversion                                              │
│  • Null handling                                                │
│  • Deduplication                                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   POSTGRESQL DATABASE                           │
│                      (Supabase)                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Fact Tables  │  │ Dim Tables   │  │ Data Sources │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 MATERIALIZED VIEW LAYER                         │
│  • Auto-refresh on data updates                                 │
│  • Pre-computed joins                                           │
│  • Optimized for query performance                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUERY EXECUTION LAYER                        │
│  • Whitelist validation                                         │
│  • Parameter binding                                            │
│  • Read-only access                                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                          │
│  • FastAPI endpoints                                            │
│  • LangGraph orchestration                                      │
│  • Response formatting                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                            │
└─────────────────────────────────────────────────────────────────┘

Layer 1: INPUT VALIDATION
┌─────────────────────────────────────────────────────────────────┐
│  • User input sanitization                                      │
│  • Parameter type checking                                      │
│  • Length limits                                                │
│  • Special character filtering                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
Layer 2: QUERY VALIDATION
┌─────────────────────────────────────────────────────────────────┐
│  • Whitelist enforcement (18 approved views)                    │
│  • SELECT-only queries                                          │
│  • No DDL/DML operations                                        │
│  • Column existence validation                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
Layer 3: EXECUTION SAFETY
┌─────────────────────────────────────────────────────────────────┐
│  • Parameterized queries (SQL injection prevention)             │
│  • Read-only database user                                      │
│  • Query timeout (30 seconds)                                   │
│  • Connection pooling                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
Layer 4: OUTPUT VALIDATION
┌─────────────────────────────────────────────────────────────────┐
│  • Result size limits                                           │
│  • Data type verification                                       │
│  • Sensitive data filtering                                     │
│  • Citation requirements                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Visualization Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    VISUALIZATION FLOW                           │
└─────────────────────────────────────────────────────────────────┘

User Query → Structured Agent → SQL Results
                                      │
                                      ▼
                            ┌──────────────────┐
                            │ Viz Data Fetcher │
                            └────────┬─────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │ Metric       │ │ Time Series  │ │ Chart Type   │
            │ Detection    │ │ Extraction   │ │ Selection    │
            └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
                   │                │                │
                   └────────────────┼────────────────┘
                                    │
                                    ▼
                          ┌──────────────────┐
                          │ Chart Config     │
                          │ Generator        │
                          └────────┬─────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │ Plotly Chart     │
                          │ Renderer         │
                          └────────┬─────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │ Interactive      │
                          │ Visualization    │
                          └──────────────────┘
```

---

## 8. Template Catalog Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    TEMPLATE CATEGORIES                          │
└─────────────────────────────────────────────────────────────────┘

1. SNAPSHOT TEMPLATES (2)
   ├─ quarter_snapshot
   └─ annual_metrics

2. GROWTH TEMPLATES (2)
   ├─ growth_qoq_yoy
   └─ growth_annual_cagr

3. PEER TEMPLATES (2)
   ├─ peer_leaderboard_quarter
   └─ peer_leaderboard_annual

4. MACRO TEMPLATES (8)
   ├─ macro_values_quarter
   ├─ macro_betas_rolling
   ├─ macro_indicator_quarterly
   ├─ macro_indicator_annual
   ├─ macro_sensitivity_quarterly
   ├─ macro_sensitivity_annual
   ├─ complete_macro_context_quarterly
   └─ complete_macro_context_annual

5. STOCK TEMPLATES (2)
   ├─ stock_price_quarterly
   └─ stock_price_annual

6. COMPLETE TEMPLATES (6)
   ├─ complete_quarterly
   ├─ complete_annual
   ├─ complete_full_quarterly
   ├─ complete_full_annual
   ├─ complete_macro_context_quarterly
   └─ complete_macro_context_annual

7. MULTI-COMPANY TEMPLATES (4)
   ├─ multi_company_quarter
   ├─ multi_company_annual
   ├─ multi_company_macro_quarter
   └─ multi_company_macro_annual

8. HEALTH TEMPLATES (2)
   ├─ health_flags
   └─ outliers

TOTAL: 29 Templates
```

---

*These diagrams provide a visual reference for understanding the CFO Intelligence Platform architecture.*
