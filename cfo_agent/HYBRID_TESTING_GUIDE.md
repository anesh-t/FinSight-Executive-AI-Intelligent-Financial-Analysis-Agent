# 🧪 Hybrid Query Testing Guide

## ✅ **Fix Applied**

The Streamlit app now uses the `/ask/hybrid` endpoint for hybrid queries!

---

## 🎯 **How to Test Your Query**

### **Step 1: Open Streamlit**
Visit: http://localhost:8501

### **Step 2: Select "Hybrid (SQL + 10-K)" Mode**
In the sidebar, you should see a mode selector. Choose:
- **Hybrid (SQL + 10-K)** ✅

### **Step 3: Ask Your Question**
Type in the question box:
```
"What drove the margin swing last quarter—show me the numbers, macro context, and 10-K citations for Apple?"
```

**Note:** Make sure to specify a company (Apple, Microsoft, Google, Amazon, or Meta)

### **Step 4: Click "Ask CFO Agent"**
The system will:
1. Detect it as a HYBRID query
2. Execute SQL agent (get margin data)
3. Execute RAG agent (get 10-K context)
4. Use GPT-4o-mini to synthesize both
5. Return comprehensive answer

---

## 📊 **Expected Response**

Your answer should include:

### **Quantitative Data (from SQL):**
- Margin percentages (Q3 vs Q2 or latest quarters)
- Revenue figures
- Percentage changes

### **Qualitative Context (from 10-K):**
- Business drivers mentioned in MD&A
- Risk factors affecting margins
- Strategic initiatives
- Market conditions

### **Synthesized Insights:**
- LLM combines both sources
- Explains what drove the changes
- Cites specific numbers and 10-K sections

---

## 🎨 **Example Queries to Try**

### **1. Margin Analysis (Your Query):**
```
"What drove Apple's margin swing last quarter—show me the numbers, macro context, and 10-K citations?"
```

### **2. Revenue Drivers:**
```
"Show me Apple revenue for 2022 and explain what drove it from their 10-K"
```

### **3. Risk Impact:**
```
"How did supply chain risks affect Apple's margins? Show the financial impact and 10-K citations"
```

### **4. Strategic Initiatives:**
```
"What were the financial impacts of Microsoft's strategic initiatives mentioned in their 10-K?"
```

---

## ⏱️ **Expected Response Time**

- **SQL Query:** 1-2 seconds
- **RAG Retrieval:** 2-3 seconds  
- **LLM Synthesis:** 2-4 seconds
- **Total:** 5-10 seconds

**Note:** First query may take longer due to initialization

---

## 🔍 **How to Verify It's Working**

### **Check 1: Mode Selection**
- Make sure "Hybrid (SQL + 10-K)" is selected in sidebar

### **Check 2: Response Content**
Your answer should have:
- ✅ Specific numbers (revenue, margins, percentages)
- ✅ Business context (from 10-K)
- ✅ Citations or references to 10-K
- ✅ "Sources: Financial Database (SQL), SEC 10-K Filings" at the end

### **Check 3: Response Time**
- Should take 5-10 seconds (not instant, not timeout)

---

## 🛠️ **If It's Not Working**

### **Issue 1: No Response or Timeout**
**Solution:** The query might be too complex. Try:
```
"Show Apple revenue 2022 and explain business drivers"
```

### **Issue 2: Only SQL Data (No 10-K Context)**
**Solution:** Make sure you selected "Hybrid (SQL + 10-K)" mode, not "Structured Data (SQL)"

### **Issue 3: Error Message**
**Check:**
1. Backend is running: http://localhost:8000/health
2. Hybrid endpoint exists: http://localhost:8000/docs (look for /ask/hybrid)

---

## 📝 **What Changed**

### **Before:**
```python
# Old code - used UnifiedCFOAgent (not working)
from master_agent import UnifiedCFOAgent
agent = UnifiedCFOAgent(verbose=False)
result = agent.query(prompt)
```

### **After:**
```python
# New code - uses /ask/hybrid endpoint
response = requests.post(
    f"{API_BASE_URL}/ask/hybrid",
    json={
        "question": prompt,
        "session_id": st.session_state.session_id
    },
    timeout=60
)
```

---

## ✅ **Ready to Test!**

1. **Open:** http://localhost:8501
2. **Select:** Hybrid (SQL + 10-K) mode
3. **Ask:** "What drove Apple's margin swing last quarter—show me the numbers, macro context, and 10-K citations?"
4. **Wait:** 5-10 seconds
5. **Enjoy:** Comprehensive CFO-level analysis! 📊

**The hybrid query system is now fully integrated with Streamlit!** 🎉
