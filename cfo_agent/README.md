# CFO Agent - Structured-Only Analytics Agent

> **LangGraph + LangChain powered CFO analytics agent with template-first SQL, guarded generation, and human-in-the-loop approval.**

## 🎯 Overview

The CFO Agent is a production-ready financial analytics system that:

- **Decomposes** multi-part questions into ordered tasks
- **Routes** queries to appropriate database surfaces (templates-first)
- **Validates** all SQL against strict safety rules
- **Executes** read-only queries with 5s timeout
- **Cites** data sources with full provenance
- **Formats** responses with tables + CFO insights + sources
- **Remembers** session context (tickers, periods, surfaces)

## 🏗️ Architecture

```
User Question
    ↓
┌─────────────────────────────────────────┐
│  LangGraph State Machine                │
│                                         │
│  1. Decompose → ordered tasks           │
│  2. Resolve Entities → tickers          │
│  3. Run Tasks → SQL exec                │
│  4. Fetch Citations → provenance        │
│  5. Format Response → table + insights  │
│  6. Update Memory → session context     │
└─────────────────────────────────────────┘
    ↓
Formatted Response (table + insights + sources)
```

## 📊 Database Surfaces

The agent queries **18 whitelisted surfaces** only:

### Core Views
- `vw_cfo_answers` - Main answer surface (50+ metrics)
- `vw_company_quarter` - Per-quarter unified
- `vw_company_quarter_macro` - Company + macro overlay

### Materialized Views
- `mv_financials_annual`, `mv_ratios_annual` - Annual aggregates
- `mv_financials_ttm`, `mv_ratios_ttm` - TTM rolling

### Growth Views
- `vw_growth_quarter` - QoQ/YoY growth
- `vw_growth_annual` - Annual YoY + CAGR
- `vw_growth_ttm` - TTM deltas

### Analytics Views
- `vw_peer_stats_quarter`, `vw_peer_stats_annual` - Peer rankings
- `vw_macro_sensitivity_rolling` - Macro correlations
- `vw_financial_health_quarter` - Balance sheet health
- `vw_outliers_quarter` - Anomaly detection

### Citations Views
- `vw_fact_citations`, `vw_stock_citations`, `vw_macro_citations`

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd cfo_agent
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `SUPABASE_DB_URL` - PostgreSQL connection string

### 3. Start the Server

```bash
python app.py
```

Server starts at `http://localhost:8000`

### 4. Test the API

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Show AAPL latest quarter revenue and ROE"}'
```

## 📝 Example Queries

### Quarter Snapshot
```
"Show AAPL latest quarter revenue, gross margin, and ROE with GP source."
```

### Annual Metrics
```
"What were Microsoft revenue and net income in FY 2023?"
```

### Growth Analysis
```
"Latest quarter revenue QoQ and YoY for AAPL."
"Amazon 5-year revenue CAGR ending FY 2024."
```

### Peer Comparison
```
"Who led on net margin last quarter? show ranks/percentiles."
"Rank peers by operating margin in FY 2023."
```

### Macro Analysis
```
"For AAPL, show net margin with CPI & Fed Funds this quarter."
"Over the last 12 quarters, AAPL beta of net margin vs CPI?"
```

### Health Checks
```
"Is AMZN balance sheet in balance last quarter? gap?"
"Flag any 3σ outliers in net margin for META since 2021."
```

### Multi-Task
```
"hey hi, tell me Apple revenue in 2022, compare its ROE with Google and tell which is better."
```

## 🔒 Safety & Guardrails

### SQL Validation Rules
- ✅ SELECT-only (no DDL/DML)
- ✅ Single statement (no semicolons)
- ✅ No `SELECT *` (explicit columns)
- ✅ Whitelisted surfaces only (18 approved)
- ✅ Whitelisted columns (schema cache)
- ✅ Bound parameters only (`:ticker`, `:fy`, `:fq`, `:limit`)
- ✅ LIMIT ≤ 200 enforced
- ✅ No cross joins
- ✅ 5s query timeout

### Execution Modes

**Template-First (Default):**
- Uses pre-defined SQL templates
- Fastest and safest
- Auto-approved

**Generative SQL (Guarded):**
- LLM generates SQL when templates don't fit
- Validates against all safety rules
- Dry-run before execution
- HITL approval required (when enabled)

## 🧠 Session Memory

The agent remembers:
- **Last 3 tickers** used
- **Last period** queried
- **Last surfaces** accessed
- **Alias resolutions** (e.g., "Apple" → "AAPL")

### Check Session Context

```bash
curl http://localhost:8000/session/my-session/context
```

### Clear Session

```bash
curl -X DELETE http://localhost:8000/session/my-session
```

## 🎯 Testing

### Router Evaluation

```bash
python tests/eval_router.py
```

Tests routing accuracy against golden prompts.

### End-to-End Testing

Follow the checklist in `tests/eval_end_to_end.md`

### Golden Prompts

See `tests/golden_prompts.yaml` for acceptance test suite.

## 📊 Response Format

Every response includes:

1. **Compact Table** (only necessary columns)
2. **2-3 CFO Insights:**
   - Growth deltas (QoQ/YoY/CAGR/TTM)
   - Peer ranks/percentiles
   - Risk flags (GP reconciliation, balance sheet, outliers)
3. **Provenance Line:**
   - `Sources: ALPHAVANTAGE_FIN (as_reported, 2025-02-10); FRED; YF`

## 🔧 Configuration

### Enable HITL (Human-in-the-Loop)

```python
# In request
{
  "question": "...",
  "enable_hitl": true
}
```

Or set environment variable:
```bash
HITL_ENABLED=true
```

### Adjust LLM Model

```bash
LLM_MODEL=gpt-4o  # or gpt-3.5-turbo
LLM_TEMPERATURE=0.0
```

### Database Pool

```bash
DB_POOL_MIN_SIZE=2
DB_POOL_MAX_SIZE=10
QUERY_TIMEOUT=5.0
```

## 📁 Project Structure

```
cfo_agent/
├── app.py                      # FastAPI entrypoint
├── graph.py                    # LangGraph state machine
├── decomposer.py               # Query decomposition
├── router.py                   # Intent routing
├── planner.py                  # Task planning
├── sql_builder.py              # Template-first SQL builder
├── generative_sql.py           # Guarded SQL generation
├── sql_exec.py                 # Async query execution
├── citations.py                # Provenance fetching
├── formatter.py                # Response formatting
├── memory.py                   # Session memory
├── hitl.py                     # Human-in-the-loop gate
├── db/
│   ├── pool.py                 # Async connection pool
│   ├── whitelist.py            # SQL validation
│   └── resolve.py              # Entity resolution
├── catalog/
│   ├── templates.json          # SQL templates
│   └── routing_examples.json   # Few-shot examples
├── prompts/
│   ├── system_prompt.md        # System prompt
│   ├── router_planner_prompt.md
│   └── generative_sql_prompt.md
└── tests/
    ├── golden_prompts.yaml     # Acceptance tests
    ├── eval_router.py          # Router evaluation
    └── eval_end_to_end.md      # E2E checklist
```

## 🎯 Performance Targets

- **p95 Latency:** < 2.5s (warmed cache)
- **Router Accuracy:** > 90%
- **SQL Validation:** 100% (all queries pass)
- **Results Non-Empty:** > 95%

## 🔄 Maintenance

### Refresh Materialized Views

After data loads:

```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_financials_annual;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_financials_ttm;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ratios_annual;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ratios_ttm;
```

### Update Schema Cache

The agent loads schema cache on startup from `vw_schema_cache`.

## 📚 API Reference

### POST /ask

Ask a question to the CFO Agent.

**Request:**
```json
{
  "question": "Show AAPL latest quarter revenue and ROE",
  "session_id": "optional-session-id",
  "enable_hitl": false
}
```

**Response:**
```json
{
  "response": "```\nticker  revenue_b  roe\n  AAPL      94.04 0.52\n```\n\n- Revenue: $94.0B (+9.6% YoY)\n- ROE: 52% (rank #1 among peers)\n- GP reconciliation: within tolerance\n\nSources: ALPHAVANTAGE_FIN (as_reported, 2025-02-10); YF",
  "session_id": "optional-session-id"
}
```

### GET /session/{session_id}/context

Get session context and memory.

### DELETE /session/{session_id}

Clear session memory.

### GET /health

Health check endpoint.

## 🐛 Troubleshooting

### Database Connection Failed

Check `SUPABASE_DB_URL` in `.env` file.

### Schema Cache Not Loaded

Ensure `vw_schema_cache` view exists in database.

### Router Accuracy Low

Review `catalog/routing_examples.json` and add more examples.

### Slow Queries

Check materialized views are refreshed and indexes exist.

## 📄 License

MIT License

---

**Built with ❤️ using LangGraph, LangChain, GPT-4o, FastAPI, and Supabase**
