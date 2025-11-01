# Module 2: Query Processing & Retrieval

**Intelligent query routing, semantic search, and context assembly for RAG**

---

## 📦 Components

### 1. `query_router.py` - Query Analysis & Routing
**Purpose:** Classify queries and extract metadata

**Features:**
- LLM-based query classification (semantic/SQL/hybrid)
- Intent extraction
- Company/year/section filter detection
- Complexity assessment
- Fallback to rule-based routing

**Query Types:**
- **Semantic**: Text understanding (e.g., "What are the risks?")
- **SQL**: Structured queries (e.g., "Compare revenue growth")
- **Hybrid**: Both needed (e.g., "Analyze profit trends")

---

### 2. `semantic_retriever.py` - Advanced Vector Search
**Purpose:** Retrieve relevant chunks with filtering

**Features:**
- Vector similarity search with pgvector
- Multi-filter support (company, year, section)
- Diversity filtering (remove near-duplicates)
- Context expansion (retrieve neighboring chunks)
- Hybrid search (vector + keyword)
- Similarity thresholds

---

### 3. `context_builder.py` - Context Assembly
**Purpose:** Format chunks for LLM consumption

**Features:**
- Multiple format styles (detailed/compact/minimal)
- Token limit management
- Citation tracking
- Metadata inclusion
- RAG prompt generation

**Format Styles:**
- **Detailed**: Full metadata + content
- **Compact**: Essential info + content
- **Minimal**: Just content with attribution

---

### 4. `retrieval_pipeline.py` - Main Orchestrator
**Purpose:** End-to-end retrieval pipeline

**Flow:**
1. Route query → Analyze
2. Retrieve chunks → Filter
3. Expand context → Optional
4. Build formatted context
5. Generate RAG prompt

---

## 🚀 Quick Start

### Basic Usage

```python
from retrieval_pipeline import RetrievalPipeline

# Initialize pipeline
pipeline = RetrievalPipeline()

# Process query
result = pipeline.process_query(
    "What are the main cybersecurity risks?",
    top_k=5
)

# Use the result
print(result.rag_prompt)  # Ready for LLM
print(result.context.formatted_context)  # Retrieved info
print(result.query_analysis)  # Query classification
```

### Advanced Usage

```python
# Custom configuration
pipeline = RetrievalPipeline(
    use_llm_routing=True,  # Use OpenAI for routing
    enable_hybrid_search=True,  # Vector + keyword
    enable_context_expansion=True  # Get neighbors
)

# Process with options
result = pipeline.process_query(
    query="Compare Apple and Microsoft AI strategies",
    top_k=10,
    min_similarity=0.4,
    format_style="compact"
)

# Access components
chunks = result.chunks  # Retrieved chunks
analysis = result.query_analysis  # Query metadata
context = result.context  # Formatted context
```

---

## 🧪 Testing

### Test Individual Components

```bash
# Test query router
cd 2_retrieval
python query_router.py

# Test semantic retriever
python semantic_retriever.py

# Test context builder
python context_builder.py

# Test full pipeline
python retrieval_pipeline.py
```

### Run Demo

```bash
python retrieval_pipeline.py
```

This will run 3 demo queries showing the complete pipeline in action.

---

## 📊 Pipeline Flow

```
User Query
    ↓
┌─────────────────┐
│  Query Router   │  → Classify & extract metadata
└─────────────────┘
    ↓
┌─────────────────┐
│ Semantic Search │  → Retrieve top-K chunks
│  + Filtering    │     • Company filter
│  + Hybrid (opt) │     • Year filter
└─────────────────┘     • Section filter
    ↓
┌─────────────────┐
│ Context Expand  │  → Get neighboring chunks (optional)
└─────────────────┘
    ↓
┌─────────────────┐
│Context Builder  │  → Format for LLM
│  + Citations    │     • Add metadata
│  + Token Mgmt   │     • Manage length
└─────────────────┘     • Add citations
    ↓
Complete RAG Prompt
```

---

## 🎯 Configuration

Settings from `.env`:

```bash
# LLM for query routing
OPENAI_API_KEY=sk-...
DEFAULT_LLM_PROVIDER=openai

# Feature flags
ENABLE_HYBRID_SEARCH=true
ENABLE_CONTEXT_EXPANSION=true

# Retrieval parameters
DEFAULT_TOP_K=5
SIMILARITY_THRESHOLD=0.3
MAX_CONTEXT_LENGTH=8000
```

---

## 📈 Performance

| Operation | Time |
|-----------|------|
| Query routing (LLM) | ~500ms |
| Semantic search | ~100-300ms |
| Context expansion | ~50-100ms |
| Context building | ~10-50ms |
| **Total pipeline** | **~1-2 seconds** |

*Times with model already loaded*

---

## 🔍 Query Examples

### Semantic Queries
- "What are the main business risks?"
- "Explain the AI strategy"
- "Describe regulatory challenges"

### Filtered Queries
- "Apple's risks in 2024" → Auto-filters to Apple + 2024
- "Meta privacy concerns" → Auto-filters to Meta + Risk Factors
- "Google AI initiatives 2023" → Auto-filters both

### Comparison Queries
- "Compare cybersecurity approaches"
- "How do AI strategies differ?"
- "Revenue trends across companies"

---

## 🛠️ Customization

### Custom Query Router

```python
from query_router import QueryRouter

router = QueryRouter(use_llm=False)  # Rule-based only
analysis = router.route("your query")
```

### Custom Retrieval

```python
from semantic_retriever import SemanticRetriever

retriever = SemanticRetriever()

# Manual retrieval
chunks = retriever.retrieve(
    query="risks",
    top_k=10,
    companies=["Apple", "Google"],
    years=[2023, 2024],
    min_similarity=0.5
)

# Hybrid search
chunks = retriever.hybrid_search(
    query="AI initiatives",
    top_k=5,
    vector_weight=0.7  # 70% vector, 30% keyword
)
```

### Custom Context

```python
from context_builder import ContextBuilder

builder = ContextBuilder(max_tokens=4000)

context = builder.build_context(
    chunks,
    format_style="compact",
    include_citations=True
)

# Build custom prompt
prompt = builder.build_rag_prompt(
    query="...",
    context=context,
    instruction="Custom instruction..."
)
```

---

## 🐛 Troubleshooting

### Error: "OpenAI API key not found"
**Fix:** Set `OPENAI_API_KEY` in `.env` or use `use_llm_routing=False`

### Low similarity scores
**Fix:** 
- Try `min_similarity=0.0` to see all results
- Use more specific queries
- Enable hybrid search

### Context too long
**Fix:**
- Reduce `top_k`
- Use `format_style="compact"` or `"minimal"`
- Adjust `MAX_CONTEXT_LENGTH` in `.env`

---

## ✅ Success Criteria

Module 2 is working if:
- [x] Query routing classifies queries correctly
- [x] Semantic search returns relevant chunks
- [x] Filters work (company, year, section)
- [x] Context building formats properly
- [x] RAG prompt is LLM-ready
- [x] Pipeline completes in < 2 seconds

---

## 🎯 What's Next?

**Module 3: SQL Bridge & Integration**
- Connect to existing SQL database
- Structured query generation
- Hybrid RAG+SQL queries
- Result fusion

**Module 4: Response Generation**
- LLM integration
- Answer synthesis
- Citation handling
- Streaming responses

---

*Module 2 Complete - Advanced Retrieval System*
