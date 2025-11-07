# Fixes Needed for Remaining 41 Failed Queries

## Current Status
- **Working:** 404/445 queries (90.8%)
- **Need Fixes:** 41 queries
- **Out of Scope:** 5 queries (Tesla, Netflix, future dates, Q5)

---

## Issue 1: Growth/Trend Queries (19 queries) ❌

### Problem
Growth views exist (`vw_growth_quarter`) with data, but SQL generation doesn't use them.

### Views Available
- ✅ `vw_growth_quarter` - Has columns: `revenue_qoq`, `revenue_yoy`, `net_income_qoq`, `net_income_yoy`
- ❌ `vw_growth_annual` - Does NOT exist
- ✅ `vw_growth_ttm` - Exists but not tested

### Failing Queries
**QoQ (5 queries):**
- "What is Apple's revenue growth QoQ Q2 2023?"
- "Show Microsoft's quarter-over-quarter growth Q1 2023"
- "Get Google's QoQ net income growth Q3 2023"
- "What is Amazon's revenue QoQ Q4 2023?"
- "Show Meta's QoQ margin improvement Q2 2023"

**YoY (5 queries):**
- "What is Apple's revenue growth YoY Q2 2023?"
- "Show Microsoft's year-over-year growth Q1 2023"
- "Get Google's YoY net income growth Q3 2023"
- "What is Amazon's revenue YoY Q4 2023?"
- "Show Meta's YoY performance Q2 2023"

**CAGR (3 queries):**
- "What is Apple's revenue CAGR over last 3 years?"
- "Show Microsoft's 5-year revenue CAGR"
- "Get Google's net income CAGR 2020-2023"

**Multi-year Trends (6 queries):**
- "Get Microsoft's margin evolution over 2023"
- "What is Google's margin performance for last 3 years?"
- "What is Google's revenue trend over last 2 years?"
- "What is Google's margin trend 2020-2023?"
- "Show Amazon's revenue evolution 2019-2023"
- "Get Meta's profitability trend 2020-2023"

### Root Cause
1. Intent `growth_qoq_yoy` is detected correctly
2. But SQL generation doesn't know to use `vw_growth_quarter`
3. Formatter doesn't know how to display growth percentages

### Fix Required
1. Update `generative_sql.py` to recognize growth intents and use `vw_growth_quarter`
2. Update `formatter.py` to format growth percentages (e.g., "Revenue grew 15.3% YoY")
3. For CAGR: Need to calculate from multiple years of data
4. For trends: Need to return multiple quarters/years of data

---

## Issue 2: Peer Comparison Queries (13 queries) ❌

### Problem
Multi-company queries not working properly.

### Views Available
- ✅ `vw_peer_stats_quarter` - Exists
- ✅ `vw_peer_stats_annual` - Exists

### Failing Queries
**All Companies (5 queries):**
- "Show ROE for all companies Q1 2023"
- "What are the debt ratios for all companies Q3 2023?"
- "Show YoY growth for all companies Q2 2023"
- "Compare margin improvement across all companies 2020-2023"
- "Show growth trends with peer comparison for last 2 years"

**Rankings (5 queries):**
- "Show top performer by revenue for 2023"
- "Who led on net income FY2023?"
- "Rank companies by margins for 2023"
- "Who has the best ROE in 2023?"
- "Show stock performance rankings for 2023"

**Multi-company with Macro (3 queries):**
- "Compare tech giants with GDP and unemployment for 2023"
- "Show tech giants' financial evolution 2020-2023"
- "Compare tech giants' revenue with unemployment and Fed rate Q2 2023"

### Root Cause
1. Decomposer detects multi-company but doesn't set right intent
2. SQL generation doesn't know to use `vw_peer_stats_*` views
3. Formatter doesn't know how to display comparison tables

### Fix Required
1. Add intent detection for peer comparison queries
2. Update SQL generation to use `vw_peer_stats_quarter` or `vw_peer_stats_annual`
3. Update formatter to create comparison tables
4. Handle "all companies" to mean the 5 supported companies

---

## Issue 3: Multi-Year/Multi-Quarter Queries ❓

### Queries to Test
- "Show Apple and Microsoft ROA for 2022"
- "Show Google revenue for 2023 and 2024"
- "Get Apple's revenue for Q1, Q2, Q3 2023"
- "Compare Apple vs Microsoft revenue 2022 and 2023"

### Expected Behavior
Should return data for multiple time periods in a table format.

### Fix Required (if not working)
1. Detect multiple time periods in query
2. Generate SQL with OR conditions or UNION
3. Format as table with time periods as rows/columns

---

## Issue 4: Ambiguous Queries (4 queries) ❌

### Failing Queries
1. "What is the stock price for Q2 2023?" - No company specified
2. "Show margins" - No company or period specified
3. "Show Apple's revenue growth with actual values Q2 2023" - Unclear
4. "Get Microsoft's YoY growth and current revenue Q1 2023" - Growth not working

### Fix Required
1. Detect missing company → Ask user or default to first company
2. Detect missing period → Default to latest quarter
3. Better error messages for ambiguous queries

---

## Implementation Priority

### Phase 1: Growth Queries (High Impact - 19 queries)
1. Update SQL generation to use `vw_growth_quarter`
2. Add formatter support for growth percentages
3. Test QoQ and YoY queries

### Phase 2: Peer Comparisons (Medium Impact - 13 queries)
1. Add peer comparison intent detection
2. Update SQL generation for `vw_peer_stats_*`
3. Add comparison table formatting

### Phase 3: Multi-Period Queries (Unknown Impact)
1. Test current behavior
2. Fix if needed

### Phase 4: Ambiguous Queries (Low Impact - 4 queries)
1. Add better error handling
2. Add default company/period logic

---

## Expected Results After Fixes

- **Phase 1:** 404 + 19 = 423/445 (95.1%)
- **Phase 2:** 423 + 13 = 436/445 (98.0%)
- **Phase 3:** 436 + ? = ?/445
- **Phase 4:** ? + 4 = ?/445

**Target:** 440/445 (98.9%) - excluding 5 out-of-scope queries
