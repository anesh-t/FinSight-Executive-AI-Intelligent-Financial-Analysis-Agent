# 🧪 VISUALIZATION FEATURE - TESTING GUIDE

**Date:** October 21, 2025  
**Status:** Ready for Testing

---

## ✅ **PRE-FLIGHT CHECKLIST:**

### **1. Backend Status:** ✅
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status":"healthy",...}`  
**Status:** ✅ Running

### **2. Streamlit Status:** ✅
```bash
curl http://localhost:8501 > /dev/null && echo "Running"
```
**Status:** ✅ Running

### **3. Dependencies:**
Plotly needs to be installed for chart rendering.

**Check if installed:**
```bash
python -c "import plotly; print('Plotly installed')" 2>/dev/null || echo "Plotly NOT installed"
```

**If not installed, run:**
```bash
pip install plotly
```

**Then restart Streamlit:**
```bash
# In Streamlit UI, press 'R' or click "Always rerun"
```

---

## 🧪 **TEST SCENARIOS:**

### **Test 1: Simple Annual Query** ⭐ START HERE

**Query:** "Apple revenue 2023"

**Expected Behavior:**
1. Text response: "Apple Inc. (AAPL) reported revenue of $385.71B for FY2023."
2. Button appears: [📊 View Trend Chart]
3. Hint: "💡 Recommended: View 5-year trend for context"
4. Click button → Chart displays with 5 years (2019-2023)
5. Metrics shown: Period Change, 5Y CAGR, Trend

**Chart Should Show:**
- Line chart with 5 data points
- Trend line (dashed)
- Years on x-axis: 2019, 2020, 2021, 2022, 2023
- Revenue values on y-axis
- Interactive hover tooltips

---

### **Test 2: Quarterly Query**

**Query:** "Apple revenue Q2 2023"

**Expected Behavior:**
1. Text response with Q2 2023 data
2. Button appears
3. Click → Chart shows 8 quarters
4. Most recent on right side

---

### **Test 3: Stock Price Query**

**Query:** "Apple closing stock price Q2 2023"

**Expected Behavior:**
1. Text response with closing price
2. Button: "View stock price movement"
3. Click → OHLC/Candlestick chart
4. Green/red candles
5. Trading range metrics

---

### **Test 4: Combined Query**

**Query:** "Show Apple revenue and net margin 2023"

**Expected Behavior:**
1. Text shows both metrics
2. Button appears
3. Click → Dual-axis chart
4. Bars for revenue, line for margin

---

### **Test 5: Ratio Query**

**Query:** "Apple gross margin 2023"

**Expected Behavior:**
1. Text shows margin percentage
2. Button appears
3. Click → Line chart with % values
4. Shows margin trend over 5 years

---

### **Test 6: Growth Query**

**Query:** "Apple revenue growth Q2 2023"

**Expected Behavior:**
1. Text shows growth rate
2. Button appears
3. Click → Bar chart with YoY growth
4. Green/red bars for positive/negative

---

### **Test 7: Query Without Visualization**

**Query:** "Who is the CEO of Apple"

**Expected Behavior:**
1. Text response (narrative)
2. NO button appears (not applicable)
3. Works normally

---

## 🐛 **TROUBLESHOOTING:**

### **Issue 1: Button Not Appearing**

**Possible Causes:**
- Query type not supported for viz
- Backend not returning viz_metadata

**Check:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Apple revenue 2023","session_id":"test"}' | \
  python -m json.tool | grep -A 5 "viz_metadata"
```

**Expected:** Should see viz_metadata with "available": true

---

### **Issue 2: Import Error - plotly**

**Error:** `ModuleNotFoundError: No module named 'plotly'`

**Fix:**
```bash
pip install plotly
```

**Then refresh Streamlit** (press 'R' in browser or click menu → "Rerun")

---

### **Issue 3: Import Error - numpy**

**Error:** `ModuleNotFoundError: No module named 'numpy'`

**Fix:**
```bash
pip install numpy
```

**Then refresh Streamlit**

---

### **Issue 4: Chart Not Loading**

**Possible Causes:**
- Backend endpoint failing
- Network timeout

**Check Backend Logs:**
```bash
tail -20 /tmp/cfo_backend_viz4.log
```

**Check for errors** like "VIZ" or "ERROR"

**Test Endpoint Directly:**
```bash
curl -X POST http://localhost:8000/api/visualize \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test",
    "intent": "annual_metrics",
    "params": {"ticker": "AAPL", "fy": 2023}
  }' | python -m json.tool | head -50
```

**Expected:** Returns chart_data and chart_config

---

### **Issue 5: Chart Displays But Looks Wrong**

**Check:**
1. Data values - are they correct?
2. Labels - are years/quarters showing?
3. Styling - dark theme applied?

**View Raw Data:**
```bash
# Use the curl command from Issue 4 to see raw data
```

---

## 📊 **VERIFICATION CHECKLIST:**

After testing, verify:

- [ ] Text responses still work (existing functionality)
- [ ] Button appears for applicable queries
- [ ] Button doesn't appear for non-applicable queries
- [ ] Chart loads when button clicked
- [ ] Chart shows correct data (5 years or 8 quarters)
- [ ] Chart is interactive (hover works)
- [ ] Insights metrics shown (CAGR, etc.)
- [ ] Multiple queries in same session work
- [ ] Error handling works (try invalid query)

---

## 🎯 **SUCCESS CRITERIA:**

✅ **PASS if:**
- Text responses work
- Button appears for supported queries
- Chart renders correctly
- Data matches text response
- No errors in console

❌ **FAIL if:**
- Text responses broken
- Button never appears
- Charts don't load
- Errors displayed
- Data incorrect

---

## 📝 **SAMPLE TEST SESSION:**

```
Session Start → http://localhost:8501

Query 1: "Apple revenue 2023"
✅ Text: $385.71B
✅ Button: Appears
✅ Chart: 5 years, trend line, metrics

Query 2: "Microsoft net margin Q2 2023"
✅ Text: 36.7%
✅ Button: Appears
✅ Chart: 8 quarters, margin %

Query 3: "Apple closing stock price 2023"
✅ Text: $194.71
✅ Button: Appears
✅ Chart: OHLC, 5 years

Query 4: "Show Apple revenue and net margin 2023"
✅ Text: Both metrics
✅ Button: Appears
✅ Chart: Dual-axis, bars + line

All tests passed! ✅
```

---

## 🚀 **READY TO TEST!**

**Steps:**
1. Open: http://localhost:8501
2. Try Test 1: "Apple revenue 2023"
3. Click the "📊 View Trend Chart" button
4. Verify chart displays correctly

**If chart displays → Implementation successful!** 🎉

**If issues → Check troubleshooting section above**

---

**Good luck testing!** 🚀
