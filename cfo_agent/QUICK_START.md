# 🚀 QUICK START GUIDE - CFO Intelligence Platform

**Get started in 3 minutes!**

---

## ⚡ INSTANT START

### **1. Start the System (2 commands)**

```bash
# Terminal 1: Start SQL backend
cd /Users/aneshthangaraj/CascadeProjects/windsurf-project-2/cfo_agent
python main.py
```

```bash
# Terminal 2: Start Streamlit UI
cd /Users/aneshthangaraj/CascadeProjects/windsurf-project-2/cfo_agent
streamlit run streamlit_app.py
```

### **2. Open Browser**

Go to: **http://localhost:8501**

### **3. Start Querying!**

You're ready! Choose a mode and ask questions.

---

## 🎯 3 QUERY MODES

### **💾 MODE 1: Structured Data (SQL)**

**Use for:** Financial metrics, multi-company comparisons, time-series

**Example Queries:**
```
show Apple revenue Q2 2023
compare Apple and Google gross margin 2023
show Microsoft revenue, net income Q2 2023
```

**Features:**
- ✅ Real-time stock data
- ✅ Company financials (2019-2025)
- ✅ Macro economic indicators
- ✅ Interactive charts
- ✅ < 2s response time

---

### **📚 MODE 2: Unstructured Data (10-K)**

**Use for:** Risk analysis, strategic insights, qualitative analysis

**Example Queries:**
```
What were Apple's supply chain risks in 2022?
What cybersecurity threats did Microsoft face in 2022?
What innovation strategies did Apple discuss in 2022?
```

**Features:**
- ✅ SEC 10-K narrative analysis
- ✅ Risk factor extraction
- ✅ Strategic priorities
- ✅ CFO-level insights
- ✅ Source citations

---

### **🔄 MODE 3: Hybrid (SQL + 10-K)**

**Use for:** Complete CFO intelligence, risk-performance correlation

**Example Queries:**
```
How did Apple's supply chain risks affect their gross margin in 2022?
What cybersecurity risks did Microsoft face and what was their R&D spending in 2022?
How did Apple's innovation strategies align with revenue growth in 2022?
```

**Features:**
- ✅ Combined analysis
- ✅ Qualitative + Quantitative
- ✅ Strategic context
- ✅ Professional formatting
- ✅ Master CFO-level quality

---

## 📋 SAMPLE QUERIES BY MODE

### **SQL Mode Examples:**

```
✅ show Apple revenue Q2 2023
✅ compare Apple and Google revenue Q2 2023
✅ show Microsoft revenue, net income, gross margin Q2 2023
✅ show Apple complete picture Q2 2023
✅ show Apple with macro context Q2 2023
```

### **RAG Mode Examples:**

```
✅ What were Apple's supply chain risks in 2022?
✅ What cybersecurity threats did Microsoft face in 2022?
✅ What regulatory challenges did Apple face in 2022?
✅ What strategic priorities did Microsoft discuss in 2022?
✅ What climate commitments did Apple make in 2022?
```

### **Hybrid Mode Examples:**

```
✅ How did Apple's supply chain risks affect their gross margin in 2022?
✅ What cybersecurity risks did Microsoft face and what was their R&D spending in 2022?
✅ How did Apple's innovation strategies align with revenue growth in 2022?
✅ What regulatory challenges did Apple face and what was their operating margin in 2022?
```

---

## 🏢 SUPPORTED COMPANIES

- **Apple (AAPL)**
- **Microsoft (MSFT)**
- **Google (GOOGL)**
- **Amazon (AMZN)**
- **Meta (META)**

---

## 📅 DATA COVERAGE

| Data Type | Coverage | Update Frequency |
|-----------|----------|------------------|
| **Company Financials** | 2019 - Q2 2025 | Quarterly |
| **Stock Prices** | Real-time | Daily |
| **Macro Indicators** | Real-time | Daily |
| **10-K Filings** | 2019 - 2022 | Annual |

---

## 💡 TIPS FOR BEST RESULTS

### **SQL Mode:**
- ✅ Be specific with time periods (Q2 2023, 2023, TTM)
- ✅ Use company names or tickers (Apple or AAPL)
- ✅ Can query 2-4 companies at once
- ✅ Can request 2-4 metrics simultaneously

### **RAG Mode:**
- ✅ Ask about specific years (2022, 2021)
- ✅ Focus on qualitative aspects (risks, strategies)
- ✅ Use question format ("What...", "How...")
- ✅ Reference 10-K sections when relevant

### **Hybrid Mode:**
- ✅ Combine qualitative + quantitative requests
- ✅ Use "and" to link risk + metric queries
- ✅ Ask about impact/correlation
- ✅ Best for comprehensive CFO analysis

---

## 🎨 INTERFACE FEATURES

### **Sidebar:**
- **Mode Selector** - Switch between 3 modes
- **Session Analytics** - Track your queries
- **Quick Examples** - Mode-specific samples
- **Clear Options** - Chat only or all cache

### **Main Chat:**
- **Message History** - Persistent conversation
- **Progress Indicators** - Real-time status
- **Chart Buttons** - View trends (SQL mode)
- **Mode-Aware Welcome** - Different per mode

### **Footer:**
- **Test Stats** - System health metrics
- **Data Coverage** - What's available
- **Platform Info** - Technical details

---

## ⚙️ COMMON TASKS

### **Switch Modes:**
1. Go to sidebar
2. Select mode from radio buttons
3. Chat updates automatically

### **View Charts (SQL Mode):**
1. Ask a financial query
2. Click "📊 View Trend Chart" button
3. Interactive chart appears

### **Clear Chat:**
1. Sidebar → "💬 Clear Chat Only"
2. Keeps session context

### **Clear Everything:**
1. Sidebar → "🧹 Clear All Cache"
2. Fresh start (clears charts too)

---

## 🐛 TROUBLESHOOTING

### **"Cannot connect to API"**
```bash
# Make sure backend is running
python main.py

# Should see: "Application startup complete"
```

### **"Streamlit not starting"**
```bash
# Install streamlit
pip install streamlit

# Run again
streamlit run streamlit_app.py
```

### **"No data returned"**
- Check if company name is correct (Apple, Microsoft, etc.)
- Verify time period is valid (2019-2025 for financials)
- For 10-K mode, use years 2019-2022

### **"Slow responses"**
- First query may be slower (model loading)
- Hybrid mode takes 4-6s (normal)
- SQL mode should be < 2s
- Charts add 1-2s loading time

---

## 📊 EXPECTED RESPONSE TIMES

| Mode | Average | Range |
|------|---------|-------|
| **SQL** | < 2s | 1-3s |
| **RAG** | 3-5s | 2-7s |
| **Hybrid** | 4-6s | 3-10s |

---

## 🎓 LEARNING PATH

### **Day 1: Basics**
1. Start with SQL mode
2. Try simple queries (revenue, margins)
3. Explore quick examples

### **Day 2: Advanced**
1. Try multi-company comparisons
2. Request multiple metrics
3. Add macro context

### **Day 3: Intelligence**
1. Switch to RAG mode
2. Explore risk analysis
3. Read strategic insights

### **Day 4: Master Level**
1. Use Hybrid mode
2. Correlate risks with performance
3. Get CFO-level analysis

---

## 📚 HELPFUL RESOURCES

### **Documentation:**
- `PROJECT_COMPLETE.md` - Full system overview
- `MASTER_CFO_SYSTEM_COMPLETE.md` - Hybrid system details
- `PRODUCTION_READY_SUMMARY.md` - Deployment guide

### **Test Files:**
- `test_bulletproof_final.py` - 15 validated queries
- `test_master_cfo_level.py` - 10 expert queries
- Run to see examples: `python test_bulletproof_final.py`

---

## 🎯 SUCCESS METRICS

**You're using it correctly if:**

✅ Getting responses in < 10s  
✅ Answers are detailed and formatted  
✅ Sources are cited (SQL mode or RAG mode)  
✅ Charts show data (SQL mode)  
✅ No error messages  

---

## 🚀 READY TO START!

1. **Open 2 terminals**
2. **Run the 2 commands** (main.py + streamlit)
3. **Open browser** (http://localhost:8501)
4. **Choose mode** (start with SQL)
5. **Ask a question** (try examples)
6. **Explore!** 🎉

---

**Need help?** Check the full documentation in `PROJECT_COMPLETE.md`

**🎊 Happy Querying! 🎊**
