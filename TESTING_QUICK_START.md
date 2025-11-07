# 🚀 Testing Quick Start Guide

## Get Started Testing in 5 Minutes

---

## 📁 Files You Have

1. **TEST_QUERIES_STRUCTURED.md** - 110 structured data queries
2. **TEST_QUERIES_UNSTRUCTURED.md** - 125 unstructured data queries
3. **TEST_EXECUTION_TRACKER.md** - Track your progress
4. **This file** - Quick start guide

---

## ⚡ Quick Start (5 Steps)

### Step 1: Start the Services

```bash
# Terminal 1: Start API Server
cd /Users/aneshthangaraj/CascadeProjects/windsurf-project-2/cfo_agent
python app.py

# Terminal 2: Start Streamlit
cd /Users/aneshthangaraj/CascadeProjects/windsurf-project-2/cfo_agent
streamlit run streamlit_app.py --server.port 8501
```

**Wait for:** Both services to start (30 seconds)

---

### Step 2: Open Streamlit

Open browser: **http://localhost:8501**

---

### Step 3: Start with Simple Tests

Copy these queries one by one into the Streamlit chat:

**Test 1 (Basic):**
```
What is Apple's revenue in Q2 2023?
```

**Expected:** Revenue value with citation

---

**Test 2 (Growth):**
```
What is Apple's revenue YoY growth Q2 2023?
```

**Expected:** Revenue + YoY percentage

---

**Test 3 (Comparison):**
```
Compare Apple and Microsoft revenue Q2 2023
```

**Expected:** Both revenues displayed

---

**Test 4 (Macro):**
```
Show Apple's revenue with CPI for Q2 2023
```

**Expected:** Revenue + CPI + other macro indicators

---

**Test 5 (Unstructured):**
```
What are Apple's strategic priorities in 2023?
```

**Expected:** List of priorities with document citation

---

### Step 4: Check Results

For each query, verify:

✅ **SQL Executed** (for structured queries)
- Check terminal logs for SQL query
- Verify correct template selected

✅ **Data Displayed**
- Response shown in chat
- Numbers formatted correctly
- Company names correct

✅ **Makes Sense**
- Answer is logical
- Numbers are reasonable
- No errors or exceptions

✅ **Citations Present**
- Sources cited (ALPHAVANTAGE_FIN, FRED, YF)
- For unstructured: Document name + section

✅ **Fast Response**
- Structured: < 5 seconds
- Unstructured: < 10 seconds

---

### Step 5: Log Results

Open **TEST_EXECUTION_TRACKER.md** and update:

```markdown
**Issue #1**

**Query:** What is Apple's revenue in Q2 2023?

**Category:** Structured

**Result:** ✅ PASSED / ❌ FAILED

**Notes:** [Any observations]
```

---

## 🎯 Recommended Testing Order

### Day 1: Core Structured Queries (2 hours)

**Basic Metrics (20 queries):**
- Revenue queries (Q1.1 - Q1.5)
- Net income queries (Q1.6 - Q1.10)
- Multiple metrics (Q1.15 - Q1.17)

**Growth Analysis (15 queries):**
- QoQ growth (Q2.1 - Q2.5)
- YoY growth (Q2.6 - Q2.10)

**Peer Comparisons (10 queries):**
- Rankings (Q3.1 - Q3.5)
- Two-company comparisons (Q3.6 - Q3.10)

**Total:** 45 queries

---

### Day 2: Advanced Structured Queries (2 hours)

**Macro-Economic (15 queries):**
- Company + macro (Q4.1 - Q4.8)
- Macro sensitivity (Q4.9 - Q4.12)
- Pure macro (Q4.13 - Q4.15)

**Stock Market (10 queries):**
- Stock prices (Q5.1 - Q5.5)
- Stock returns (Q5.6 - Q5.7)
- Stock + financials (Q5.8 - Q5.10)

**Time Series (10 queries):**
- Last N quarters (Q6.1 - Q6.4)
- Last N years (Q6.5 - Q6.6)
- Date ranges (Q6.7 - Q6.10)

**Total:** 35 queries

---

### Day 3: Ratios & Edge Cases (1 hour)

**Ratios & Margins (15 queries):**
- Margins (Q7.1 - Q7.5)
- Return ratios (Q7.6 - Q7.9)
- Debt ratios (Q7.10 - Q7.12)
- Expense ratios (Q7.13 - Q7.15)

**Edge Cases (10 queries):**
- Ambiguous queries (Q8.1 - Q8.3)
- Invalid inputs (Q8.4 - Q8.7)
- Incomplete queries (Q8.8 - Q8.10)

**Total:** 25 queries

---

### Day 4: Core Unstructured Queries (2 hours)

**Strategic Priorities (15 queries):**
- Q1.1 - Q1.15

**Business Model (15 queries):**
- Q2.1 - Q2.15

**Risk Factors (15 queries):**
- Q3.1 - Q3.15

**Total:** 45 queries

---

### Day 5: Advanced Unstructured Queries (2 hours)

**Competitive Positioning (15 queries):**
- Q4.1 - Q4.15

**Management Discussion (15 queries):**
- Q5.1 - Q5.15

**Products & Services (10 queries):**
- Q6.1 - Q6.10

**Total:** 40 queries

---

### Day 6: Specialized Unstructured Queries (2 hours)

**Financial Strategy (10 queries):**
- Q7.1 - Q7.10

**Regulatory & Legal (10 queries):**
- Q8.1 - Q8.10

**ESG & Sustainability (10 queries):**
- Q9.1 - Q9.10

**Future Outlook (10 queries):**
- Q10.1 - Q10.10

**Total:** 40 queries

---

## 🐛 Common Issues & Solutions

### Issue: "Cannot connect to CFO Agent API"

**Solution:**
```bash
# Check if API is running
curl http://localhost:8000/docs

# If not, restart API
cd cfo_agent
python app.py
```

---

### Issue: "No data found"

**Possible Causes:**
1. Company not in database (only AAPL, MSFT, AMZN, GOOG, META)
2. Period not available (only 2019-2025)
3. Quarter invalid (Q1-Q4 only)

**Solution:** Use valid company/period

---

### Issue: "SQL execution failed"

**Check:**
1. Database connection (check .env file)
2. Terminal logs for SQL error
3. Template exists for query type

---

### Issue: "Response is empty"

**Check:**
1. Data exists in database for that period
2. SQL query returned results (check logs)
3. Formatter is working (check terminal)

---

### Issue: "Unstructured query returns nothing"

**Check:**
1. 10-K documents are loaded
2. Vector database is populated
3. Embeddings are generated

---

## 📊 Success Metrics

### Structured Queries

**Target Pass Rate:** 95% (105/110)

**Critical Queries (Must Pass):**
- All revenue queries
- All net income queries
- All growth calculations
- All peer comparisons
- All macro context queries

**Acceptable Failures:**
- Some edge cases (invalid inputs)
- Some complex time series

---

### Unstructured Queries

**Target Pass Rate:** 90% (113/125)

**Critical Queries (Must Pass):**
- Strategic priorities
- Business model
- Risk factors
- Competitive positioning

**Acceptable Failures:**
- Queries requiring missing documents
- Highly specific cross-company queries
- Some specialized queries (ESG, regulatory)

---

## 📝 Quick Testing Template

Copy this for each query:

```
Query: [Paste query here]
Category: Structured / Unstructured
Result: ✅ PASS / ❌ FAIL
Time: [X seconds]
Notes: [Any observations]

Expected:
[What should happen]

Actual:
[What happened]

Issues:
[Any problems]
```

---

## 🎯 Testing Checklist

Before you start:
- [ ] API server running (http://localhost:8000)
- [ ] Streamlit running (http://localhost:8501)
- [ ] Browser open to Streamlit
- [ ] TEST_QUERIES files open
- [ ] TEST_EXECUTION_TRACKER open
- [ ] Terminal visible for logs

During testing:
- [ ] Copy query exactly as written
- [ ] Wait for complete response
- [ ] Check all validation criteria
- [ ] Log results immediately
- [ ] Note any issues

After testing:
- [ ] Update tracker with results
- [ ] Document all issues found
- [ ] Calculate pass rates
- [ ] Identify patterns in failures
- [ ] Create summary report

---

## 🚀 Pro Tips

1. **Test in batches** - Do 10-15 queries at a time, then take a break

2. **Watch terminal logs** - They show SQL queries and errors

3. **Clear cache** - If results seem cached, clear Streamlit cache

4. **Test variations** - If a query fails, try rephrasing it

5. **Document patterns** - If multiple similar queries fail, note the pattern

6. **Take screenshots** - For interesting results or errors

7. **Compare with database** - Verify numbers match actual data

8. **Test edge cases last** - Focus on core functionality first

---

## 📞 Need Help?

**Check these first:**
1. Terminal logs (errors will show here)
2. Browser console (F12 for dev tools)
3. Database connection (test_connection.py)
4. API health (http://localhost:8000/docs)

**Common fixes:**
- Restart services
- Clear Python cache
- Clear browser cache
- Check .env file
- Verify database access

---

## ✅ You're Ready!

You now have:
- ✅ 235 test queries ready to use
- ✅ Validation criteria for each query
- ✅ Progress tracker
- ✅ Quick start guide
- ✅ Testing schedule

**Start with the 5 simple tests above, then work through the recommended order!**

**Good luck! 🎉**
