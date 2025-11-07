# 🔧 Issues Found & Fixes Required

## Test Results Summary
- **Total Queries:** 110
- **Passed:** 102 (92.7%)
- **Failed:** 8 (7.3%)
- **Macro Display Issue:** 9 queries

---

## 🐛 Issue #1: SQL Syntax Error with Colon (7 queries)

### **Symptoms:**
```
Error: syntax error at or near ":"
```

### **Affected Queries:**
1. "Who had the highest net margin Q2 2023?"
2. "Show margins for all companies Q3 2023"
3. "What is the average revenue across all companies Q2 2023?"
4. "What is Tesla's revenue Q2 2023?" (invalid company)
5. "Show Netflix's net income Q1 2023" (invalid company)
6. "Show margins" (incomplete query)

### **Root Cause:**
The `_convert_params` function in `/cfo_agent/db/pool.py` is doing simple string replacement of `:param` with `$1`, `$2`, etc. However, there might be edge cases where:
1. PostgreSQL's `::` type cast operator is being confused with parameter placeholders
2. Parameters in `CAST(:param AS TYPE)` expressions are causing issues
3. Invalid company names or incomplete queries generate malformed SQL

### **Investigation Needed:**
Check if the SQL being generated has issues with:
- `CAST(:fy AS INTEGER)` - This should work fine
- `::jsonb` or `::text` type casts - These might conflict
- NULL parameters causing syntax errors

### **Fix:**
Improve the `_convert_params` function to:
1. Use regex for more precise parameter matching
2. Avoid replacing `::` (PostgreSQL type cast)
3. Add better error handling for malformed SQL

---

## 🐛 Issue #2: Missing Database View (1 query)

### **Symptoms:**
```
Error: relation "vw_peer_stats_annual" does not exist
```

### **Affected Query:**
- "Who led on net income FY 2023?"

### **Root Cause:**
The `vw_peer_stats_annual` view doesn't exist in the database.

### **Fix:**
Create the `vw_peer_stats_annual` view in the database, mirroring the structure of `vw_peer_stats_quarter`.

---

## 🐛 Issue #3: Macro Context Not Displayed (9 queries)

### **Symptoms:**
Queries asking for macro context (CPI, GDP, etc.) retrieve the data from database but don't display it in the response.

### **Affected Queries:**
1. "Show Apple's revenue with CPI for Q2 2023"
2. "Get Microsoft's performance with GDP context Q1 2023"
3. "Show Google's revenue with unemployment rate Q3 2023"
4. "What is Amazon's revenue with Fed rate Q2 2023?"
5. "Show Meta's margins with CPI Q1 2023"
6. "Show Apple's revenue with GDP and CPI Q2 2023"
7. "Get Microsoft's performance with CPI, unemployment, and Fed rate Q1 2023"
8. "Show Google's financials with macro context Q3 2023"
9. "What was the Fed rate in Q1 2023?"

### **Root Cause:**
The queries are NOT being routed to the `complete_macro_context_quarterly` template. Instead, they're being routed to simpler templates like `quarter_snapshot` which don't include macro columns in the SQL.

**Evidence:**
- The formatter HAS the code to display macro context (lines 702-727 in formatter.py)
- The template `complete_macro_context_quarterly` HAS the macro columns in SQL
- BUT the queries aren't using this template

### **Investigation:**
Check the decomposer and router to see why queries with "with CPI", "with GDP", "macro context" aren't being classified as `complete_macro_context_quarterly` intent.

### **Fix:**
Update the decomposer to better detect macro context queries and route them to the correct template.

---

## 📋 Detailed Fix Plan

### **Fix #1: Improve Parameter Conversion (Priority: High)**

**File:** `/cfo_agent/db/pool.py`

**Current Code:**
```python
def _convert_params(self, sql: str, params: dict):
    """Convert :named params to $1, $2, etc."""
    positional_sql = sql
    positional_params = []
    param_index = 1
    
    for key, value in params.items():
        placeholder = f":{key}"
        if placeholder in positional_sql:
            positional_sql = positional_sql.replace(placeholder, f"${param_index}")
            positional_params.append(value)
            param_index += 1
    
    return positional_sql, positional_params
```

**Improved Code:**
```python
import re

def _convert_params(self, sql: str, params: dict):
    """Convert :named params to $1, $2, etc. using regex for precision"""
    positional_sql = sql
    positional_params = []
    param_index = 1
    
    for key, value in params.items():
        # Use word boundary to match :param but not ::type_cast
        pattern = r'(?<![:])\b:' + re.escape(key) + r'\b'
        
        # Count occurrences
        matches = list(re.finditer(pattern, positional_sql))
        
        if matches:
            # Replace all occurrences with the same positional parameter
            positional_sql = re.sub(pattern, f"${param_index}", positional_sql)
            positional_params.append(value)
            param_index += 1
    
    return positional_sql, positional_params
```

**Benefits:**
- Uses regex with word boundaries to avoid false matches
- Negative lookbehind `(?<![:])` prevents matching `::type_cast`
- More robust parameter replacement

---

### **Fix #2: Create Missing Database View (Priority: Medium)**

**File:** Create new SQL migration

**SQL to Execute:**
```sql
CREATE OR REPLACE VIEW vw_peer_stats_annual AS
SELECT 
    company_id,
    fiscal_year,
    revenue_annual,
    net_income_annual,
    operating_income_annual,
    gross_profit_annual,
    net_margin_annual,
    operating_margin_annual,
    gross_margin_annual,
    roe_annual_avg_equity,
    roa_annual_avg_assets,
    -- Rankings
    RANK() OVER (PARTITION BY fiscal_year ORDER BY revenue_annual DESC) as rank_revenue_annual,
    RANK() OVER (PARTITION BY fiscal_year ORDER BY net_margin_annual DESC) as rank_net_margin_annual,
    RANK() OVER (PARTITION BY fiscal_year ORDER BY roe_annual_avg_equity DESC) as rank_roe_annual,
    -- Percentiles
    PERCENT_RANK() OVER (PARTITION BY fiscal_year ORDER BY revenue_annual) as pct_revenue_annual,
    PERCENT_RANK() OVER (PARTITION BY fiscal_year ORDER BY net_margin_annual) as pct_net_margin_annual,
    -- Z-scores
    (revenue_annual - AVG(revenue_annual) OVER (PARTITION BY fiscal_year)) / 
        NULLIF(STDDEV(revenue_annual) OVER (PARTITION BY fiscal_year), 0) as z_revenue_annual
FROM mv_financials_annual
WHERE revenue_annual IS NOT NULL;
```

---

### **Fix #3: Improve Macro Context Detection (Priority: High)**

**File:** `/cfo_agent/decomposer.py`

**Current Issue:**
The decomposer might not be detecting queries like "Show Apple's revenue with CPI" as macro context queries.

**Fix Approach:**
1. Check the LLM prompt to ensure it understands macro keywords
2. Add rule-based override for macro keywords (CPI, GDP, unemployment, Fed rate, macro context)
3. Ensure intent is set to `complete_macro_context_quarterly` when macro keywords are present

**Code Location to Check:**
Look for the section that overrides intent based on keywords (around line 200-250 in decomposer.py based on previous session notes).

**Expected Logic:**
```python
# Check for macro keywords
macro_keywords = ['cpi', 'gdp', 'unemployment', 'fed rate', 'fed funds', 'macro context', 'economic context', 's&p 500', 'inflation']
has_macro_keywords = any(keyword in question_lower for keyword in macro_keywords)

if has_company and has_macro_keywords:
    if has_quarter:
        result['tasks'][0]['intent'] = 'complete_macro_context_quarterly'
    else:
        result['tasks'][0]['intent'] = 'complete_macro_context_annual'
```

---

## 🧪 Testing Plan

### **After Fix #1 (Parameter Conversion):**
Re-run these queries:
- "Who had the highest net margin Q2 2023?"
- "Show margins for all companies Q3 2023"
- "What is the average revenue across all companies Q2 2023?"

Expected: Should pass (no more syntax errors)

### **After Fix #2 (Database View):**
Re-run:
- "Who led on net income FY 2023?"

Expected: Should pass (view exists)

### **After Fix #3 (Macro Detection):**
Re-run all 9 macro queries:
- "Show Apple's revenue with CPI for Q2 2023"
- "Get Microsoft's performance with GDP context Q1 2023"
- etc.

Expected: Should display macro context in response

---

## 📊 Expected Results After Fixes

| Issue | Queries Affected | Expected Pass Rate After Fix |
|-------|------------------|------------------------------|
| SQL Syntax Error | 7 queries | +6.4% (99.1% total) |
| Missing View | 1 query | +0.9% (100% total) |
| Macro Display | 9 queries | 100% accuracy on display |

**Final Expected Pass Rate: 100% (110/110)**
**Final Expected Display Accuracy: 100%**

---

## 🎯 Priority Order

1. **Fix #3 (Macro Detection)** - Highest impact, affects user experience
2. **Fix #1 (Parameter Conversion)** - Fixes 6 queries
3. **Fix #2 (Database View)** - Fixes 1 query

---

## 📝 Next Steps

1. Investigate decomposer.py to understand current macro detection logic
2. Implement Fix #3 (macro detection)
3. Test macro queries
4. Implement Fix #1 (parameter conversion)
5. Test peer comparison queries
6. Implement Fix #2 (database view)
7. Run full test suite again
8. Validate 100% pass rate

---

**Let's start with Fix #3 (Macro Detection) as it has the highest impact!**
