# 🔍 HOW YOUR SQL AGENT ACTUALLY WORKS - CODE ANALYSIS

## Complete Code-by-Code Breakdown

---

## ⚠️ CRITICAL FINDING

**Your agent is using TEMPLATES by default, NOT GPT-4o!**

---

## 📊 THE ACTUAL FLOW (Code Evidence)

### **Step 1: User Question**
```
User: "Show Apple's revenue for Q2 2023"
```

### **Step 2: Graph Orchestration** (`graph.py`)

**File:** `cfo_agent/graph.py`  
**Line 163 & 187:**
```python
sql, params, is_generative = await self.sql_builder.build_sql(
    plan, 
    use_generative=False  # ← HARDCODED TO FALSE!
)
```

**Evidence:**
- Line 163: `use_generative=False` (for multi-entity queries)
- Line 187: `use_generative=False` (for single entity queries)

**Conclusion:** Graph is FORCING template mode!

---

### **Step 3: SQL Builder** (`sql_builder.py`)

**File:** `cfo_agent/sql_builder.py`  
**Line 15:**
```python
async def build_sql(self, plan: Dict, use_generative: bool = True):
```

**Default:** `use_generative = True`

**BUT:** Graph.py overrides this with `use_generative=False`!

**Line 26-31:**
```python
if use_generative:
    # Generative path
    return await self._build_generative(plan)  # ← NOT CALLED
else:
    # Template path (default)
    return await self._build_from_template(plan)  # ← THIS IS CALLED
```

**What happens:**
- Since graph.py passes `use_generative=False`
- It goes to `_build_from_template()` (Line 33)

---

### **Step 4: Template Path** (`sql_builder.py`)

**Line 33-44:**
```python
async def _build_from_template(self, plan: Dict) -> Tuple[str, Dict, bool]:
    """Build SQL from template"""
    sql = plan['sql']  # ← Gets SQL from plan (which came from template!)
    params = plan['params']
    
    # Validate SQL
    is_valid, error_msg = validate_sql(sql, params)
    
    if not is_valid:
        raise ValueError(f"Template SQL validation failed: {error_msg}")
    
    return sql, params, False  # ← Returns template SQL
```

**Evidence:** SQL comes from `plan['sql']`, which is the template!

---

### **Step 5: Where Does Template SQL Come From?** (`planner.py`)

**File:** `cfo_agent/planner.py`  
**Line 47-48:**
```python
# Get SQL from template
sql = template['sql']  # ← Template SQL!
```

**Line 50-57:**
```python
return {
    'sql': sql,  # ← This is template SQL
    'params': params,
    'surfaces': routed_task['surfaces'],
    'entities_resolved': entities_resolved,
    'template_name': routed_task['template_name'],
    'intent': routed_task['intent']
}
```

**Evidence:** The plan contains pre-written SQL from templates!

---

### **Step 6: Where Are Templates Stored?** (`router.py`)

**File:** `cfo_agent/router.py`  
**Templates loaded from:** `catalog/templates.json`

**Example Template:**
```json
{
  "quarter_snapshot": {
    "sql": "SELECT c.ticker, cc.revenue / 1e9 as revenue_b FROM vw_company_complete_quarter cc JOIN dim_company c USING (company_id) WHERE c.ticker = :ticker AND cc.fiscal_year = :fy AND cc.fiscal_quarter = :fq LIMIT :limit",
    "params": ["ticker", "fy", "fq", "limit"],
    "surfaces": ["vw_company_complete_quarter"]
  }
}
```

---

## 🎯 THE COMPLETE ACTUAL FLOW

```
User Question: "Show Apple's revenue for Q2 2023"
        ↓
Decomposer (decomposer.py)
  - Extracts: intent, entities, period
        ↓
Router (router.py)
  - Matches intent to template
  - Loads template from catalog/templates.json
  - Template contains PRE-WRITTEN SQL
        ↓
Planner (planner.py)
  - Gets SQL from template: sql = template['sql']
  - Builds params: {ticker: "AAPL", fy: 2023, fq: 2}
  - Returns plan with template SQL
        ↓
Graph (graph.py) - Line 187
  - Calls: sql_builder.build_sql(plan, use_generative=FALSE)
        ↓
SQL Builder (sql_builder.py) - Line 26
  - use_generative is FALSE
  - Goes to _build_from_template()
  - Returns: plan['sql'] (the template SQL)
        ↓
Validator (whitelist.py)
  - Validates template SQL
        ↓
Executor (sql_exec.py)
  - Executes template SQL
        ↓
Formatter (formatter.py)
  - Formats results
```

---

## 🔍 PROOF: YOUR TESTS USED TEMPLATES

### **Test File:** `test_llm_sql_generation.py`

**Line 43-44:**
```python
# Generate SQL with GPT-4o
candidates = await builder.generate_sql(context)
```

**This test directly calls `GenerativeSQLBuilder.generate_sql()`**

**BUT:** Your actual agent (graph.py) does NOT call this!

---

### **What Actually Happens in Production:**

**In Streamlit/Production:**
```
graph.py → sql_builder.build_sql(plan, use_generative=False)
                    ↓
            Uses template SQL from plan
```

**In Your Tests:**
```
test_llm_sql_generation.py → builder.generate_sql(context)
                                      ↓
                              Calls GPT-4o directly
```

**These are DIFFERENT code paths!**

---

## 📊 EVIDENCE SUMMARY

| Component | File | Line | Evidence |
|-----------|------|------|----------|
| **Graph** | graph.py | 163, 187 | `use_generative=False` hardcoded |
| **SQL Builder** | sql_builder.py | 26-31 | Goes to `_build_from_template()` |
| **Template Fetch** | sql_builder.py | 35 | `sql = plan['sql']` |
| **Plan Creation** | planner.py | 48 | `sql = template['sql']` |
| **Template Source** | router.py | - | Loads from `catalog/templates.json` |

---

## 🆚 WHAT YOU TESTED vs WHAT RUNS

### **What You Tested (test_llm_sql_generation.py):**
```python
builder = GenerativeSQLBuilder()
candidates = await builder.generate_sql(context)  # ← GPT-4o
```
**Result:** 100% success with GPT-4o

### **What Actually Runs (graph.py):**
```python
sql, params, is_generative = await self.sql_builder.build_sql(
    plan, 
    use_generative=False  # ← Templates
)
```
**Result:** Uses pre-written templates

---

## 🎯 WHY YOUR END-TO-END TEST WORKED

**Test File:** `test_complete_nl_to_nl_flow.py`

**Line 90-91:**
```python
# Generate SQL with GPT-4o
candidates = await builder.generate_sql(context)
```

**This ALSO directly calls GPT-4o, bypassing the graph!**

---

## 🔧 HOW TO ACTUALLY ENABLE GPT-4o

### **Option 1: Change graph.py (Recommended)**

**File:** `cfo_agent/graph.py`

**Change Line 163:**
```python
# FROM:
sql, params, is_generative = await self.sql_builder.build_sql(single_plan, use_generative=False)

# TO:
sql, params, is_generative = await self.sql_builder.build_sql(single_plan, use_generative=True)
```

**Change Line 187:**
```python
# FROM:
sql, params, is_generative = await self.sql_builder.build_sql(plan, use_generative=False)

# TO:
sql, params, is_generative = await self.sql_builder.build_sql(plan, use_generative=True)
```

---

### **Option 2: Make it Configurable**

**Add to graph.py __init__:**
```python
def __init__(self, use_llm_sql: bool = True):
    self.use_llm_sql = use_llm_sql
    # ... rest of init
```

**Then use:**
```python
sql, params, is_generative = await self.sql_builder.build_sql(
    plan, 
    use_generative=self.use_llm_sql
)
```

---

## 📋 CURRENT TEMPLATE CATALOG

**File:** `cfo_agent/catalog/templates.json`

**Available Templates (14 total):**
1. `quarter_snapshot` - Single quarter metrics
2. `annual_metrics` - Annual data
3. `growth_qoq_yoy` - Growth rates
4. `stock_price_quarterly` - Stock prices
5. `complete_quarterly` - All metrics (Layer 1)
6. `complete_macro_context_quarterly` - With macro (Layer 2)
7. `complete_full_quarterly` - With sensitivity (Layer 3)
8. `macro_sensitivity_quarterly` - Sensitivity analysis
9. `multi_company_quarter` - Multi-company comparison
10. `peer_leaderboard_quarter` - Peer rankings
11. `macro_indicator_quarterly` - Macro-only queries
12. ... and 3 more

**Each template has:**
- Pre-written SQL query
- Parameter list
- Surface (table/view) list
- Default parameters

---

## 🎯 FINAL ANSWER

### **Q: How is your structured SQL agent working?**

**A: Using PRE-WRITTEN TEMPLATES from `catalog/templates.json`**

### **Q: Is it using GPT-4o?**

**A: NO - graph.py has `use_generative=False` hardcoded**

### **Q: But the tests passed with GPT-4o?**

**A: Yes, because the tests BYPASS graph.py and call GPT-4o directly**

### **Q: How to actually use GPT-4o in production?**

**A: Change `use_generative=False` to `use_generative=True` in graph.py lines 163 and 187**

---

## 🔍 CODE LOCATIONS TO VERIFY

1. **Check graph.py line 163:**
   ```bash
   grep -n "use_generative=False" cfo_agent/graph.py
   ```

2. **Check template loading:**
   ```bash
   cat cfo_agent/catalog/templates.json | head -20
   ```

3. **Check planner getting SQL from template:**
   ```bash
   grep -n "sql = template\['sql'\]" cfo_agent/planner.py
   ```

---

## ✅ SUMMARY

**Current System:**
- ✅ Uses 14 pre-written SQL templates
- ✅ Templates stored in `catalog/templates.json`
- ✅ Graph.py forces `use_generative=False`
- ✅ Fast and predictable
- ❌ Limited to 14 query types
- ❌ NOT using GPT-4o in production

**To Enable GPT-4o:**
- Change 2 lines in graph.py (lines 163, 187)
- Change `use_generative=False` to `use_generative=True`
- Restart the application

---

**🎯 Your agent is currently template-based, NOT GPT-4o based! 🎯**
