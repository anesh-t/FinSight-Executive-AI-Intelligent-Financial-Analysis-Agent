# Module 1: Data Ingestion

**Process 30 JSON files → Generate embeddings → Load to Supabase**

---

## 📦 Components

### 1. `json_processor.py`
**Purpose:** Extract structured chunks from 10-K JSON files

**Features:**
- Processes all 30 JSON files
- Normalizes company names (Amazon, Apple, Google, Meta, Microsoft)
- Maps section codes to readable names (Item 1A → Risk Factors)
- Extracts metadata: company, year, section, heading, subheading, word count
- Returns `ChunkData` objects

**Test:**
```bash
python json_processor.py
```

**Expected Output:**
- 30 files processed
- 6,671 chunks extracted
- Sample chunk displayed

---

### 2. `embedding_generator.py`
**Purpose:** Generate 384-dimensional embeddings using MiniLM-L6-v2

**Features:**
- Loads sentence-transformers model
- Batch processing (configurable batch size)
- Normalizes embeddings for cosine similarity
- GPU support (optional)
- Progress bars for long operations

**Test:**
```bash
python embedding_generator.py
```

**Expected Output:**
- Model loaded successfully
- Dimension: 384
- Similarity test passes (similar texts score high)

---

### 3. `database_loader.py`
**Purpose:** Load chunks and embeddings to Supabase database

**Features:**
- Direct PostgreSQL connection (faster than REST API)
- Batch insertion (500 rows per batch)
- Error handling and retry logic
- Verification queries
- Progress tracking

**Test:**
```bash
python database_loader.py
```

**Expected Output:**
- Connection established
- Test row inserted
- Verification successful

---

### 4. `run_ingestion.py`
**Purpose:** Main orchestrator - runs complete pipeline

**Pipeline Steps:**
1. Process JSON files
2. Generate embeddings
3. Load to database
4. Verify insertion

**Run:**
```bash
python run_ingestion.py
```

**Duration:** ~2-3 minutes

---

## 🚀 Quick Start

```bash
# From rag_system directory
cd 1_ingestion
python run_ingestion.py
```

---

## 📊 Pipeline Flow

```
JSON Files (30)
    ↓
json_processor.py → 6,671 ChunkData objects
    ↓
embedding_generator.py → 6,671 × 384 embeddings
    ↓
database_loader.py → Insert to Supabase
    ↓
✅ 6,671 rows in sec_10k_embeddings table
```

---

## 🔧 Configuration

All settings in `.env`:

```bash
JSON_FOLDER_PATH=/path/to/parsed_10k_json
EMBEDDING_BATCH_SIZE=32
DB_BATCH_SIZE=500
```

---

## ✅ Success Criteria

- [x] All 30 files processed
- [x] 6,671 chunks extracted
- [x] 6,671 embeddings generated
- [x] 6,671 rows inserted to database
- [x] No errors
- [x] Verification passes

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Files/second | ~10 |
| Chunks/second | ~45 |
| Embeddings/second | ~750 |
| DB inserts/second | ~1,300 |
| **Total time** | **~2-3 min** |

---

## 🐛 Troubleshooting

See `../RUN_PIPELINE.md` for detailed troubleshooting guide.

---

*Module 1 Complete - Ready to Run*
