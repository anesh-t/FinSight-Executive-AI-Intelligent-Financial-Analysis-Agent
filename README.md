# 📊 CFO Assistant Project

> **AI-Powered Financial Analysis System** | LangGraph + LangChain + GPT-4o + Supabase

## 🚀 **New Implementation: CFO Agent**

The CFO Assistant has been **upgraded to a new Structured-Only CFO Agent** with:

- ✅ **LangGraph State Machine** - 6-node workflow for robust execution
- ✅ **Template-First SQL** - 14 pre-defined templates for common queries
- ✅ **Guarded Generative SQL** - LLM fallback with strict validation
- ✅ **Full Provenance** - Citations from Alpha Vantage, FRED, Yahoo Finance
- ✅ **Human-in-the-Loop** - Optional approval gates
- ✅ **Session Memory** - Context retention across queries
- ✅ **CFO-Grade Formatting** - Tables + insights + sources

### 🎯 Overview

The CFO Agent analyzes **Apple, Microsoft, Amazon, Google, and Meta's** financial data from **2019-2025** using:

- **Natural Language** → Decomposed tasks → Template-first SQL
- **18 Whitelisted Surfaces** → Validated queries → Read-only execution
- **Citations & Provenance** → CFO insights → Formatted responses

## 🚀 Quick Start

### 1. Navigate to CFO Agent

```bash
cd cfo_agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and SUPABASE_DB_URL
```

### 4. Start the API Server

```bash
python app.py
```

Server starts at `http://localhost:8000`

### 5. Test the API

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Show AAPL latest quarter revenue and ROE"}'
```

## 💡 Example Queries

### Quarter Snapshots
- "Show AAPL latest quarter revenue, gross margin, and ROE with GP source"
- "What were Microsoft revenue and net income in FY 2023?"

### Growth Analysis
- "Latest quarter revenue QoQ and YoY for AAPL"
- "Amazon 5-year revenue CAGR ending FY 2024"

### Peer Comparisons
- "Who led on net margin last quarter? show ranks/percentiles"
- "Rank peers by operating margin in FY 2023"

### Macro Analysis
- "For AAPL, show net margin with CPI & Fed Funds this quarter"
- "Over the last 12 quarters, AAPL beta of net margin vs CPI?"

### Health Checks
- "Is AMZN balance sheet in balance last quarter? gap?"
- "Flag any 3σ outliers in net margin for META since 2021"

### Multi-Task
- "hey hi, tell me Apple revenue in 2022, compare its ROE with Google and tell which is better"

## 📚 Documentation

### CFO Agent (New Implementation)
- **[CFO Agent README](cfo_agent/README.md)** - Complete user guide
- **[Build Specification](cfo_agent/CFO_AGENT_BUILD_SPEC.md)** - Technical details
- **[Implementation Summary](CFO_AGENT_IMPLEMENTATION_SUMMARY.md)** - What was built

### Database Migrations
All database migrations are complete. See:
- **[Complete Migration Status](COMPLETE_MIGRATION_STATUS.md)** - Full migration summary
- **[Final Validation Report](FINAL_VALIDATION_REPORT.md)** - Validation results
- **[Schema Validation Report](SCHEMA_VALIDATION_REPORT.md)** - Schema completeness

### Database Schema

The database has **39 core objects** (100% complete):

**Key Surfaces:**
- `vw_cfo_answers` - Main answer surface (50+ metrics per company-quarter)
- `mv_financials_annual`, `mv_ratios_annual` - Annual aggregates
- `mv_financials_ttm`, `mv_ratios_ttm` - TTM rolling metrics
- `vw_growth_quarter`, `vw_growth_annual`, `vw_growth_ttm` - Growth calculations
- `vw_peer_stats_quarter`, `vw_peer_stats_annual` - Peer rankings
- `vw_macro_sensitivity_rolling` - Macro sensitivities
- `vw_financial_health_quarter`, `vw_outliers_quarter` - Health checks

See [SCHEMA_VALIDATION_REPORT.md](SCHEMA_VALIDATION_REPORT.md) for complete schema.

## 📁 Project Structure

```
windsurf-project-2/
├── cfo_agent/              # New CFO Agent (29 files)
│   ├── app.py              # FastAPI service
│   ├── graph.py            # LangGraph state machine
│   ├── decomposer.py       # Query decomposition
│   ├── router.py           # Intent routing
│   ├── planner.py          # Task planning
│   ├── sql_builder.py      # Template-first SQL
│   ├── db/                 # Database layer
│   ├── catalog/            # Templates & examples
│   ├── prompts/            # System prompts
│   └── tests/              # Testing suite
├── database.py             # Supabase connector (for migrations)
├── db_migration_*.py       # Database migration scripts
├── validate_*.py           # Validation scripts
├── old_implementation/     # Backup of old files
└── requirements.txt        # Python dependencies
```

## 🔧 Configuration

Create `.env` in `cfo_agent/` directory:

```env
# OpenAI
OPENAI_API_KEY=your_key_here

# Supabase
SUPABASE_DB_URL=postgresql://postgres:password@db.ikhrfgywojsrvxgdojxd.supabase.co:5432/postgres

# LLM Configuration
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.0

# HITL (Human-in-the-Loop)
HITL_ENABLED=false
```

## 🛠️ Troubleshooting

### Database Connection Issues

Check your `SUPABASE_DB_URL` in `.env` file.

### API Not Starting

```bash
cd cfo_agent
pip install -r requirements.txt
python app.py
```

### Old Implementation

Old files have been moved to `old_implementation/` directory. You can:
- Restore them if needed
- Delete the directory after testing: `rm -rf old_implementation/`

## 📝 License

MIT License

---

**Built with** ❤️ **using LangGraph, LangChain, GPT-4o, FastAPI, and Supabase**
