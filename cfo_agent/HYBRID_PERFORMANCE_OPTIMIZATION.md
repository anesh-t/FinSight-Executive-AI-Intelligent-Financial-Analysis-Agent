# Hybrid Query Performance Optimization

## 🎯 Goal
Reduce hybrid query response time from 120s+ to **15-30 seconds** for multi-company analysis.

---

## 📊 Current Performance Baseline

### Query: "Across Apple, Microsoft, Amazon, Meta and Google, what were the top three drivers of gross margin expansion or compression over the last five years?"

**Current Breakdown:**
- SQL Query: ~5-10s (5 companies × multiple metrics)
- RAG Query: ~60-90s (5 companies × 5 years × 10-K retrieval)
- LLM Synthesis: ~5-10s (GPT-5.1 processing)
- **Total: 70-110s** (often times out at 120s)

---

## ✅ Optimizations Applied

### 1. Parallel Execution (ALREADY IMPLEMENTED)
```python
# Execute SQL and RAG in parallel
sql_task = asyncio.create_task(...)
rag_task = asyncio.create_task(...)
sql_response, rag_response = await asyncio.gather(sql_task, rag_task)
```
**Impact**: 50% time reduction (sequential would be 2x slower)

### 2. Enhanced Synthesis Prompt
**Before**: Generic prompt, limited guidance
**After**: Structured prompt with specific instructions for multi-company analysis

**Changes**:
- Clear formatting rules
- Company-by-company breakdown instructions
- Emphasis on combining quant + qual data
- Specific output structure

**Impact**: Better quality answers, no time impact

### 3. Increased Token Limit
**Before**: max_tokens=800
**After**: max_completion_tokens=2000

**Impact**: Allows comprehensive multi-company answers without truncation

---

## 🚀 Additional Optimizations Needed

### Priority 1: Fix Async Database Conflict (HIGH IMPACT)
**Problem**: Event loop conflicts slow down database operations
**Solution**: Implement separate connection pools

```python
# Create separate pools
sql_pool = await create_pool(...)  # For SQL agent
rag_pool = await create_pool(...)  # For RAG agent
```

**Expected Impact**: 30-50% time reduction (eliminate retry overhead)

---

### Priority 2: Optimize RAG Retrieval (HIGH IMPACT)
**Current**: Retrieves full 10-K sections for each company
**Optimization**: Targeted retrieval with filters

```python
# Instead of retrieving all 10-K data
chunks = retriever.retrieve(
    query="gross margin drivers",
    companies=['AAPL', 'MSFT', 'AMZN', 'META', 'GOOGL'],
    years=[2019, 2020, 2021, 2022, 2023, 2024],
    sections=['Item 7'],  # MD&A only
    top_k=3  # Reduced from 5
)
```

**Expected Impact**: 40-60% RAG time reduction (90s → 35-55s)

---

### Priority 3: Add Query Result Caching (MEDIUM IMPACT)
**Implementation**: Cache SQL results for common queries

```python
import redis
cache = redis.Redis()

# Cache key based on query + companies + timeframe
cache_key = f"sql:{hash(question)}:{companies}:{years}"
if cached := cache.get(cache_key):
    return cached
```

**Expected Impact**: 80-90% time reduction for repeated queries

---

### Priority 4: Implement Streaming Responses (UX IMPROVEMENT)
**Current**: User waits 120s with no feedback
**Better**: Stream partial results as they arrive

```python
# Stream SQL results first
yield {"type": "sql", "data": sql_response}

# Then stream RAG insights
yield {"type": "rag", "data": rag_response}

# Finally stream synthesis
yield {"type": "synthesis", "data": synthesized_answer}
```

**Expected Impact**: Better UX, perceived time reduction

---

### Priority 5: Optimize SQL Queries (LOW-MEDIUM IMPACT)
**Current**: Multiple queries for each company
**Better**: Single optimized query with JOINs

```sql
-- Instead of 5 separate queries
SELECT 
    c.ticker,
    c.name,
    mv.fiscal_year,
    mv.gross_margin,
    mv.revenue_annual,
    mv.cost_of_revenue_annual
FROM mv_financials_annual mv
JOIN companies c ON c.ticker = mv.ticker
WHERE c.ticker IN ('AAPL', 'MSFT', 'AMZN', 'META', 'GOOGL')
    AND mv.fiscal_year BETWEEN 2019 AND 2024
ORDER BY c.ticker, mv.fiscal_year;
```

**Expected Impact**: 20-30% SQL time reduction (10s → 7-8s)

---

## 📈 Expected Performance After All Optimizations

| Component | Current | Optimized | Improvement |
|-----------|---------|-----------|-------------|
| SQL Query | 5-10s | 3-7s | 30% faster |
| RAG Query | 60-90s | 25-40s | 55% faster |
| LLM Synthesis | 5-10s | 5-10s | Same |
| **Total** | **70-110s** | **33-57s** | **50-60% faster** |

**Target**: < 30s for most hybrid queries

---

## 🔧 Implementation Plan

### Phase 1: Quick Wins (1-2 hours)
1. ✅ Enhanced synthesis prompt
2. ✅ Increased token limit
3. ⏳ Optimize RAG retrieval parameters
4. ⏳ Optimize SQL queries

### Phase 2: Infrastructure (2-4 hours)
1. ⏳ Fix async database conflict
2. ⏳ Implement separate connection pools
3. ⏳ Add query result caching

### Phase 3: UX Improvements (2-3 hours)
1. ⏳ Implement streaming responses
2. ⏳ Add progress indicators
3. ⏳ Add timeout handling with partial results

---

## 🧪 Testing Strategy

### Test Queries (Simple → Complex)

**Level 1: Single Company (Target: < 10s)**
```
What were Apple's gross margin drivers from 2019-2024?
```

**Level 2: Two Companies (Target: < 15s)**
```
Compare Apple and Microsoft's gross margin drivers over the last 5 years
```

**Level 3: Five Companies (Target: < 30s)**
```
Across Apple, Microsoft, Amazon, Meta and Google, what were the top three drivers of gross margin expansion or compression over the last five years?
```

### Performance Metrics to Track
- Total query time
- SQL execution time
- RAG retrieval time
- LLM synthesis time
- Cache hit rate (after caching implemented)
- Error rate

---

## 🎯 Success Criteria

✅ **Minimum Viable**:
- Single company queries: < 10s
- Multi-company queries: < 30s
- Error rate: < 5%

✅ **Target**:
- Single company queries: < 5s
- Multi-company queries: < 20s
- Error rate: < 2%
- Cache hit rate: > 30%

✅ **Stretch Goal**:
- Single company queries: < 3s
- Multi-company queries: < 15s
- Error rate: < 1%
- Cache hit rate: > 50%

---

## 📝 Current Status

### Completed
- ✅ Parallel execution (SQL + RAG)
- ✅ Enhanced synthesis prompt
- ✅ Increased token limit to 2000

### In Progress
- ⏳ Async database conflict fix

### Pending
- ⏳ RAG retrieval optimization
- ⏳ SQL query optimization
- ⏳ Query result caching
- ⏳ Streaming responses
- ⏳ Progress indicators

---

## 🚦 Next Steps

1. **Immediate**: Restart backend with optimizations
2. **Test**: Run simple hybrid query to verify improvements
3. **Measure**: Benchmark current performance
4. **Optimize**: Implement Priority 1 & 2 fixes
5. **Re-test**: Verify 50%+ improvement

---

**Last Updated**: November 19, 2025
**Status**: Optimizations in progress, targeting 50-60% performance improvement
