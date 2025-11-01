# 🔍 SEMANTIC SEARCH TESTING GUIDE

Your vector database is loaded with 6,671 chunks! Now let's test the semantic search.

---

## 🚀 QUICK START

### Option 1: Interactive Mode (Recommended)

```bash
cd /Users/aneshthangaraj/CascadeProjects/windsurf-project-2/cfo_agent/rag_system
../venv/bin/python test_search.py
```

**Then type queries like:**
- "What are the main business risks?"
- "AI and machine learning investments"
- "regulatory challenges"
- "cloud computing revenue"
- "supply chain issues"

Type `demo` to run pre-built demo queries  
Type `quit` to exit

---

### Option 2: Demo Mode

Run pre-built demo queries automatically:

```bash
../venv/bin/python test_search.py demo
```

**Demo Queries:**
1. General business risks
2. AI investments in 2024
3. Meta's regulatory challenges
4. Amazon's cloud revenue
5. Apple's supply chain

---

### Option 3: Single Query

Run a single query from command line:

```bash
../venv/bin/python test_search.py "What are Apple's main risks?"
```

---

## 📊 WHAT YOU'LL SEE

For each query, you'll get:

```
🔎 QUERY: What are the main business risks?
================================================================================

📄 RESULT #1
--------------------------------------------------------------------------------
Company:    Amazon (AMZN) - 2024
Section:    Item 1A - Risk Factors
Heading:    Risk Factors
Subheading: Business and Operational Risks
Similarity: 0.7823
Words:      285

Text:
Our business faces substantial risks from intense competition...
[Preview of relevant text from 10-K filing]

📄 RESULT #2
...
```

**Each result shows:**
- ✅ Company, ticker, and year
- ✅ Section and heading from 10-K
- ✅ Similarity score (0-1, higher is better)
- ✅ Relevant text preview

---

## 🎯 TEST QUERIES TO TRY

### General Queries:
- "What are the biggest risks?"
- "Revenue growth drivers"
- "competitive advantages"
- "research and development"

### Company-Specific:
- "Apple's supply chain strategy"
- "Amazon's cloud business"
- "Google's advertising revenue"
- "Meta's user privacy concerns"
- "Microsoft's AI initiatives"

### Year-Specific:
- "2024 financial performance"
- "2023 regulatory changes"
- "2022 market conditions"

### Topic-Specific:
- "cybersecurity threats"
- "intellectual property"
- "employee retention"
- "environmental sustainability"
- "data privacy regulations"

---

## 🔍 HOW IT WORKS

1. **Your Query** → Converted to 384-dim embedding vector
2. **Database Search** → Find most similar chunk embeddings using cosine similarity
3. **Results Ranked** → Top-K most relevant chunks returned
4. **Metadata Included** → Company, year, section info preserved

**Technology:**
- Sentence-transformers (MiniLM-L6-v2)
- pgvector for similarity search
- PostgreSQL for storage

---

## ⚡ ADVANCED FEATURES

### Filtering

The system auto-detects filters in your query:

**Company Filter:**
- "Apple's risks" → Filters to Apple only
- "Amazon cloud" → Filters to Amazon only

**Year Filter:**
- "2024 challenges" → Filters to 2024 filings
- "2023 revenue" → Filters to 2023 filings

**Combined:**
- "Apple 2024 risks" → Apple + 2024
- "Meta 2023 privacy" → Meta + 2023

---

## 📈 EXPECTED PERFORMANCE

| Metric | Value |
|--------|-------|
| Query Speed | ~100-300ms |
| Top-5 Results | < 1 second |
| Similarity Range | 0.3 - 0.9 |
| Relevant Results | 80-90% accuracy |

**Similarity Score Guide:**
- **0.8-1.0**: Highly relevant (exact match)
- **0.6-0.8**: Very relevant (semantic match)
- **0.4-0.6**: Somewhat relevant
- **< 0.4**: Weak match

---

## 🐛 TROUBLESHOOTING

### Error: "Module not found"
**Fix:**
```bash
# Make sure you're using venv python
../venv/bin/python test_search.py
```

### Error: "Database connection failed"
**Fix:** Check your `.env` has correct `DB_PASSWORD`

### No results / Low similarity scores
**Tip:** Try:
- More specific queries
- Different wording
- Topic-focused queries (not too broad)

---

## ✅ SUCCESS CRITERIA

Your semantic search is working if:
- ✅ Queries return relevant results
- ✅ Similarity scores > 0.5 for good matches
- ✅ Results match the query topic
- ✅ Company/year filters work correctly
- ✅ Fast response (< 1 second)

---

## 🎯 WHAT'S NEXT?

After testing, we'll build **Module 2**:

**Query Routing System:**
- Classify queries (semantic vs structured)
- Route to RAG or SQL engine
- Combine results intelligently

**Enhanced Retrieval:**
- Hybrid search (vector + keyword)
- Context expansion
- Multi-document retrieval
- Ranking optimization

---

## 🚀 RUN YOUR FIRST TEST

```bash
cd /Users/aneshthangaraj/CascadeProjects/windsurf-project-2/cfo_agent/rag_system
../venv/bin/python test_search.py
```

**Try this query:** *"What are the main AI and machine learning initiatives?"*

**See how the system finds relevant chunks across all companies and years!**

---

*Testing Guide - Module 1 Complete*
