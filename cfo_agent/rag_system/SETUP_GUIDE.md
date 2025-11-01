# 🚀 RAG SYSTEM - SETUP GUIDE

## ✅ WHAT WE JUST BUILT (Module 0: Foundation)

### Files Created:

```
rag_system/
├── setup_database.sql          ✅ Complete PostgreSQL schema
├── requirements.txt            ✅ All Python dependencies
├── .env.example               ✅ Configuration template
├── .gitignore                 ✅ Protect sensitive files
├── setup.sh                   ✅ Automated setup script
├── README.md                  ✅ Complete documentation
└── 0_foundation/
    ├── __init__.py            ✅ Module initialization
    └── config.py              ✅ Configuration management
```

---

## 🎯 WHAT YOU NEED TO DO NOW

### Option A: Quick Setup (Recommended)

```bash
# 1. Navigate to rag_system directory
cd cfo_agent/rag_system

# 2. Run automated setup
./setup.sh

# 3. Edit .env file with your credentials
nano .env

# 4. Set up database (see below)
```

### Option B: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env from template
cp .env.example .env
nano .env  # Edit with your credentials
```

---

## 🔑 REQUIRED CREDENTIALS

You need to add these to your `.env` file:

### 1. Supabase (Required)
```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOi...
DB_PASSWORD=your-database-password
```

**Where to find:**
- Go to [Supabase Dashboard](https://app.supabase.com)
- Select your project
- Settings → API → Project URL & Service Role Key
- Settings → Database → Database Password

### 2. LLM Provider (Choose One)

**OpenAI (Recommended):**
```bash
OPENAI_API_KEY=sk-...
DEFAULT_LLM_PROVIDER=openai
```

**Or Anthropic:**
```bash
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_LLM_PROVIDER=anthropic
```

### 3. Data Path
```bash
JSON_FOLDER_PATH=../parsed_10k_json
```

---

## 🗄️ DATABASE SETUP

### Method 1: Supabase SQL Editor (Easiest)

1. Go to https://app.supabase.com
2. Select your project
3. Go to **SQL Editor**
4. Click **New Query**
5. Copy entire contents of `setup_database.sql`
6. Paste and click **Run**

**Expected Output:**
```
CREATE EXTENSION
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE INDEX
...
Success. No rows returned
```

### Method 2: psql Command Line

```bash
# Get connection string from Supabase Settings → Database → Connection String
psql "postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres" \
  -f setup_database.sql
```

---

## ✅ VERIFICATION

### 1. Test Configuration

```bash
python -m 0_foundation.config
```

**Expected Output:**
```
======================================================================
RAG SYSTEM CONFIGURATION
======================================================================
Environment: development
Debug Mode: True
Log Level: INFO

DATABASE:
  Supabase URL: https://xxxxx.supabase...
  DB Host: db.xxxxx.supabase.co
  Pool Size: 10

LLM:
  Provider: openai
  Model: gpt-4-turbo-preview
  Max Context: 8000

EMBEDDING:
  Model: sentence-transformers/all-MiniLM-L6-v2
  Dimension: 384
  Batch Size: 32
  GPU: False

✅ Configuration is valid!
```

### 2. Test Database Connection

```python
# Quick test
python3 << EOF
from 0_foundation.config import config
from supabase import create_client

client = create_client(config.database.supabase_url, 
                       config.database.supabase_service_key)

# Test query
result = client.table('companies').select('*').execute()
print(f"✅ Database connected! Found {len(result.data)} companies")
EOF
```

**Expected Output:**
```
✅ Database connected! Found 5 companies
```

---

## 🐛 TROUBLESHOOTING

### Error: "No module named 'sentence_transformers'"
**Fix:** Virtual environment not activated
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "Database connection failed"
**Fix:** Check your `.env` file
```bash
# Verify these are set correctly:
grep SUPABASE_URL .env
grep DB_PASSWORD .env
```

### Error: "Extension vector does not exist"
**Fix:** Run in Supabase SQL Editor:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Error: "JSON_FOLDER_PATH not found"
**Fix:** Update path in `.env`:
```bash
# Relative to rag_system directory
JSON_FOLDER_PATH=../parsed_10k_json
```

---

## 📊 WHAT'S IN THE DATABASE?

After running `setup_database.sql`, you have:

### Tables Created:
- ✅ `sec_10k_embeddings` - Ready for 6,671 embeddings
- ✅ `companies` - 5 tech companies pre-loaded
- ✅ `section_mapping` - 16 10-K sections mapped
- ✅ `query_cache` - For performance optimization

### Indexes Created:
- ✅ Vector index (HNSW) for fast similarity search
- ✅ Metadata indexes (company, year, section)
- ✅ Full-text search index
- ✅ Composite indexes for common queries

### Functions Created:
- ✅ `semantic_search()` - Helper function for queries
- ✅ `update_full_text_search()` - Auto-update trigger

---

## 🎯 CURRENT STATUS

```
✅ MODULE 0: FOUNDATION - COMPLETE
   ├── ✅ Database schema
   ├── ✅ Dependencies installed
   ├── ✅ Configuration system
   └── ✅ Documentation

⏳ MODULE 1: DATA INGESTION - READY TO START
   ├── JSON processor
   ├── Embedding generator
   ├── Database loader
   └── Run ingestion pipeline
```

---

## 🚀 NEXT STEPS

Once you've completed setup and verification:

1. **Confirm everything works:**
   ```bash
   python -m 0_foundation.config
   # Should show ✅ Configuration is valid!
   ```

2. **Ready for Module 1:**
   - I'll build the data ingestion pipeline
   - Process all 30 JSON files
   - Generate 6,671 embeddings
   - Load to Supabase

**Total time: ~2-3 minutes to run**

---

## 📞 NEED HELP?

### Quick Checks:

```bash
# 1. Virtual environment active?
which python
# Should show: /path/to/rag_system/venv/bin/python

# 2. Dependencies installed?
pip list | grep sentence-transformers

# 3. .env file exists?
ls -la .env

# 4. Database accessible?
python -m 0_foundation.config
```

---

## ✅ READY TO PROCEED?

Once you see:
```
✅ Configuration is valid!
✅ Database connected!
```

**You're ready for Module 1: Data Ingestion!**

Let me know when you're ready and I'll build the ingestion pipeline.

---

*Setup Guide - Module 0 Complete*
