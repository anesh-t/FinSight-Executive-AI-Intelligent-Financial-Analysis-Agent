# 📊 CFO Assistant Agent

> **AI-Powered Financial Analysis System** | LangChain + GPT-3.5-Turbo + Supabase

A sophisticated LangChain-based CFO Assistant Agent that queries structured financial data from Supabase PostgreSQL and delivers executive-level insights with beautiful visualizations.

## 🎯 Overview

The CFO Assistant acts as a junior financial consultant analyzing **Apple, Microsoft, Amazon, Google, and Meta's** financial data from **2019-2025**. It combines:

- **Natural Language Queries** → SQL generation via LangChain
- **Structured Database** → Supabase PostgreSQL with optimized views
- **Executive Visualizations** → Plotly charts with company-specific colors
- **CFO-Style Narratives** → GPT-3.5-Turbo powered insights

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Edit `.env` file and add your Supabase database password:

```env
SUPABASE_DB_URL=postgresql://postgres:YOUR_PASSWORD@db.ikhrfgywojsrvxgdojxd.supabase.co:5432/postgres
```

### 3. Test Connection

```bash
python test_connection.py
```

### 4. Launch Dashboard

```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

## 💡 Example Queries

- "Compare Apple's revenue growth and stock return since 2020"
- "Show GDP and CPI trends alongside Meta's operating margin"
- "Which quarters were most impacted by COVID-19 for Amazon?"
- "Visualize debt-to-equity ratios across all companies for 2023"
- "Plot Apple's ROE vs. Fed Funds rate over time"

## 📦 Database Schema

### Fact Tables
- **fact_financials** – Revenue, income, assets, liabilities, cash flows
- **fact_ratios** – ROE, ROA, profit margins, leverage ratios
- **fact_stock_prices** – Stock prices, returns, volatility, dividends
- **fact_macro_indicators** – GDP, CPI, Fed Funds rate, S&P 500

### Dimension Tables
- **dim_company** – Company master data
- **dim_financial_metric** – Financial metric definitions
- **dim_ratio** – Ratio metric definitions
- **dim_stock_metric** – Stock metric definitions
- **dim_macro_indicator** – Macro indicator definitions
- **dim_event** – Event timeline (COVID-19, product launches, etc.)

### Analytical Views
- **vw_company_summary** – Comprehensive company financials + ratios + stock
- **vw_macro_overlay** – Company data with macro indicators
- **vw_event_timeline** – Financial data with event context
- **vw_macro_long** – Long-format macro data
- **vw_data_dictionary** – Metadata for all metrics

## 🎨 Visualization Features

All charts use company-specific colors:

- 🍎 **Apple** – Blue (#007AFF)
- 🪟 **Microsoft** – Teal (#00A4EF)
- 📦 **Amazon** – Orange (#FF9900)
- 🔍 **Google** – Yellow (#FBBC04)
- 👥 **Meta** – Purple (#8B5CF6)

## 📁 Project Structure

```
windsurf-project-2/
├── app.py                  # Streamlit dashboard
├── cfo_assistant.py        # Main agent with LangChain
├── database.py             # Supabase connector
├── visualizations.py       # Plotly chart generator
├── example_usage.py        # Usage examples
├── test_connection.py      # Connection testing
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── README.md              # This file
```

## 🔧 Configuration

The system uses environment variables in `.env`:

```env
# OpenAI
OPENAI_API_KEY=your_key_here

# Supabase
SUPABASE_URL=https://ikhrfgywojsrvxgdojxd.supabase.co
SUPABASE_KEY=your_key_here
SUPABASE_DB_URL=postgresql://postgres:password@host:5432/postgres

# Agent Settings
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.0
MAX_ITERATIONS=15
VERBOSE=true
```

## 🛠️ Troubleshooting

### Database Connection Issues

```bash
# Test connection
python test_connection.py
```

Make sure you've replaced `[YOUR_PASSWORD]` in the `SUPABASE_DB_URL` with your actual Supabase database password.

### OpenAI API Errors

- Verify API key is valid
- Check rate limits
- Ensure sufficient credits

## 📝 License

MIT License

---

**Built with** ❤️ **using LangChain, GPT-3.5-Turbo, Supabase, Plotly, and Streamlit**
