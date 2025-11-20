# Hybrid Query Issue - Event Loop Conflict

## Problem
Hybrid queries are failing with async/event loop errors:
```
RuntimeError: Task got Future attached to a different loop
asyncpg.exceptions._base.InterfaceError: cannot perform operation: another operation is in progress
```

## Root Cause
The hybrid orchestrator (`MasterOrchestrator`) is calling:
1. **SQL Agent** (async database operations via LangGraph)
2. **RAG Agent** (async database operations for vector search)

Both are trying to use the same database connection pool in different async contexts, causing conflicts.

## Current Behavior
- Hybrid queries timeout after 60 seconds
- Backend shows event loop errors
- Query completes but returns incomplete/empty results

## Temporary Workaround
**Increase timeout in frontend:**
```python
# In streamlit_app_enhanced.py, line ~538
response = requests.post(
    f"{API_BASE_URL}/ask/hybrid",
    json={"question": prompt, "session_id": st.session_state.session_id},
    timeout=120  # Increased from 60 to 120 seconds
)
```

## Proper Fix (TODO)
Need to refactor the database connection handling to avoid event loop conflicts:

### Option 1: Separate Connection Pools
```python
# Create separate pools for SQL and RAG
sql_pool = await create_pool(...)  # For SQL agent
rag_pool = await create_pool(...)  # For RAG agent
```

### Option 2: Sequential Execution
```python
# Execute SQL and RAG sequentially instead of parallel
sql_result = await coordinator.query_sql(question)
rag_result = await coordinator.query_rag(question)
```

### Option 3: Use asyncio.create_task() properly
```python
# Ensure tasks run in same event loop
async with asyncio.TaskGroup() as tg:
    sql_task = tg.create_task(coordinator.query_sql(question))
    rag_task = tg.create_task(coordinator.query_rag(question))
```

## Testing
Test with simple hybrid query:
```bash
curl -X POST http://localhost:8000/ask/hybrid \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me Apple gross margin in 2023 and explain risks", "session_id": "test"}' \
  --max-time 120
```

## Status
- ⚠️ **PARTIAL**: Hybrid queries work but with errors
- ❌ **PERFORMANCE**: Slow due to error handling overhead
- ✅ **WORKAROUND**: Increase timeout to 120s

## Priority
**HIGH** - This affects the core hybrid functionality which is a key feature of the platform.
