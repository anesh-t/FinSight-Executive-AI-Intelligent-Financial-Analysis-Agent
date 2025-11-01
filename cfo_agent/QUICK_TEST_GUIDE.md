# ⚡ Quick Test Guide - Top 3 Questions Per Mode

**Fast reference for testing Streamlit**

---

## 📊 MODE 1: STRUCTURED DATA (SQL)
**Speed: 3-5 seconds**

### **Top 3 Questions:**
```
1. What was Apple's revenue in 2022?

2. Compare Apple and Microsoft revenue in 2022

3. Show me Apple's revenue trend from 2019 to 2022
```

---

## 📚 MODE 2: UNSTRUCTURED DATA (10-K)
**Speed: 5-7 seconds (Quick Mode)**

### **Top 3 Questions:**
```
1. Summarize Apple's major risk factors in 2022

2. What are Apple's ESG commitments in 2022?

3. What was Apple's cash flow in 2022?
   (Fastest: 3-5s!)
```

---

## 🔄 MODE 3: HYBRID (SQL + RAG)
**Speed: 10-15 seconds**

### **Top 3 Questions:**
```
1. How did supply chain risks affect Apple's margins in 2022?

2. Give me a complete overview of Apple in 2022

3. Summarize Apple's strategic priorities and financial results
```

---

## 🎯 QUICK START

**Start Streamlit:**
```bash
streamlit run streamlit_app.py
```

**Test One From Each Mode:**
1. **Structured:** "What was Apple's revenue in 2022?"
2. **Unstructured:** "Summarize Apple's risks in 2022"
3. **Hybrid:** "How did risks affect Apple's margins?"

---

## ⚡ FASTEST QUERIES (< 5s)

Want to see speed? Try these:

**Structured:**
- "What was Apple's revenue in 2022?"
- "Show me Microsoft's net income"

**Unstructured (Financial Extraction):**
- "What was Apple's cash flow in 2022?"
- "Show me Apple's revenue in 2022"

---

## 📈 EXPECTED PERFORMANCE

| Mode | Time | Example |
|------|------|---------|
| **Structured** | 3-5s | Revenue queries |
| **Unstructured** | 5-7s | Risk summaries |
| **Hybrid** | 10-15s | Combined analysis |

---

## ✅ SUCCESS INDICATORS

**You'll know it's working when you see:**

✅ **Structured:** Clean tables with financial metrics  
✅ **Unstructured:** Quick summary with follow-up questions  
✅ **Hybrid:** Comprehensive analysis with both data sources  

---

**🚀 Ready to test! Pick a mode and try a question! 🚀**

**Full question list:** See `STREAMLIT_TEST_QUERIES.md`
