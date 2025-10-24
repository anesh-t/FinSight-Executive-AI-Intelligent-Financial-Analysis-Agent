# End-to-End Evaluation Checklist

## Manual E2E Testing

### Setup
- [ ] Database connection established
- [ ] Schema cache loaded
- [ ] Ticker cache loaded
- [ ] FastAPI server running on port 8000

### Test 1: Quarter Snapshot
**Query:** "Show AAPL latest quarter revenue, gross margin, and ROE with GP source."

**Expected:**
- [ ] Intent: `quarter_snapshot`
- [ ] Surface: `vw_cfo_answers`
- [ ] Results: Non-empty table with revenue, gross_margin, roe, gross_profit_source
- [ ] Insights: 2-3 bullet points mentioning growth/rank/GP status
- [ ] Sources: Citation line with ALPHAVANTAGE_FIN

**Command:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Show AAPL latest quarter revenue, gross margin, and ROE with GP source."}'
```

---

### Test 2: Annual Metrics
**Query:** "What were Microsoft revenue and net income in FY 2023?"

**Expected:**
- [ ] Intent: `annual_metrics`
- [ ] Surface: `mv_financials_annual`
- [ ] Results: Revenue and net income for FY 2023
- [ ] Insights: Mention annual performance
- [ ] Sources: Citation line

---

### Test 3: Growth Analysis
**Query:** "Latest quarter revenue QoQ and YoY for AAPL."

**Expected:**
- [ ] Intent: `growth_qoq_yoy`
- [ ] Surface: `vw_growth_quarter`
- [ ] Results: QoQ and YoY percentages
- [ ] Insights: Mention growth trends
- [ ] Sources: Citation line

---

### Test 4: Peer Comparison
**Query:** "Who led on net margin last quarter? show ranks/percentiles."

**Expected:**
- [ ] Intent: `peer_leaderboard_quarter`
- [ ] Surface: `vw_peer_stats_quarter`
- [ ] Results: All companies with ranks and percentiles
- [ ] Insights: Identify leader and mention percentiles
- [ ] Sources: Citation line

---

### Test 5: Multi-Task Query
**Query:** "hey hi, tell me Apple revenue in 2022, compare its ROE with Google and tell which is better."

**Expected:**
- [ ] Greeting: "Hi!" or similar
- [ ] Task 1: Annual revenue for AAPL FY 2022
- [ ] Task 2: ROE comparison AAPL vs GOOG FY 2022
- [ ] Results: Two separate sections
- [ ] Insights: Identify which company has better ROE
- [ ] Sources: Citation lines for both tasks

---

### Test 6: Macro Sensitivity
**Query:** "Over the last 12 quarters, AAPL beta of net margin vs CPI?"

**Expected:**
- [ ] Intent: `macro_betas_rolling`
- [ ] Surface: `vw_macro_sensitivity_rolling`
- [ ] Results: Beta coefficient for net margin vs CPI
- [ ] Insights: Interpret sensitivity (positive/negative/neutral)
- [ ] Sources: Citation line

---

### Test 7: Health Check
**Query:** "Is AMZN balance sheet in balance last quarter? gap?"

**Expected:**
- [ ] Intent: `health_flags`
- [ ] Surface: `vw_financial_health_quarter`
- [ ] Results: balance_status, balance_gap_abs, balance_gap_pct
- [ ] Insights: Interpret balance status
- [ ] Sources: Citation line

---

### Test 8: Outlier Detection
**Query:** "Flag any 3σ outliers in net margin for META since 2021."

**Expected:**
- [ ] Intent: `outliers`
- [ ] Surface: `vw_outliers_quarter`
- [ ] Results: Quarters with outlier_net_margin_3sigma = 1
- [ ] Insights: Identify outlier periods
- [ ] Sources: Citation line

---

## Performance Benchmarks

### Latency (p95)
- [ ] Quarter snapshot: < 2.5s
- [ ] Annual metrics: < 2.0s
- [ ] Growth analysis: < 2.5s
- [ ] Peer comparison: < 3.0s
- [ ] Multi-task: < 4.0s

### Accuracy
- [ ] Router accuracy: > 90%
- [ ] Entity resolution: > 95%
- [ ] SQL validation: 100% (all queries pass validation)
- [ ] Results non-empty: > 95%

---

## Safety Checks

### SQL Validation
- [ ] All queries are SELECT-only
- [ ] No SELECT * in generated SQL
- [ ] All queries have LIMIT clause
- [ ] LIMIT ≤ 200 enforced
- [ ] Only whitelisted surfaces used
- [ ] Only whitelisted parameters used

### HITL (when enabled)
- [ ] Generative SQL triggers approval request
- [ ] Template SQL auto-approved
- [ ] Approval context includes SQL and params

---

## Session Memory

### Test Session Persistence
1. Query 1: "Show AAPL latest quarter revenue"
2. Query 2: "What about Microsoft?"
3. Check session context: `GET /session/test123/context`

**Expected:**
- [ ] last_tickers: ["AAPL", "MSFT"]
- [ ] query_count: 2
- [ ] last_period: latest quarter info

---

## Error Handling

### Invalid Ticker
**Query:** "Show INVALID_TICKER revenue"

**Expected:**
- [ ] Graceful error message
- [ ] No SQL execution
- [ ] Helpful suggestion

### Missing Data
**Query:** "Show AAPL revenue in FY 1990"

**Expected:**
- [ ] Empty results message
- [ ] Explanation of missing data
- [ ] Fallback suggestion

---

## Acceptance Criteria

**All tests must pass:**
- [ ] Correct intent/surface routing (100%)
- [ ] Non-empty results (> 95%)
- [ ] SQL validation (100%)
- [ ] Response format (table + insights + sources)
- [ ] Latency within bounds
- [ ] Safety checks pass
- [ ] Session memory works
- [ ] Error handling graceful

**Sign-off:** _______________  
**Date:** _______________
