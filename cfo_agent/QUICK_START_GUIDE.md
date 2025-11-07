# 🚀 CFO Intelligence Platform - Quick Start Guide

## ✅ **System is Running!**

### **🌐 Access Points:**
- **Frontend (Streamlit):** http://localhost:8501
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

---

## 📊 **What You Can Do**

### **1. Standard SQL Queries** ⚡ Fast (1-2 seconds)

**Single Company:**
```
"What is Apple revenue for 2022?"
"Show Microsoft net income Q1 2023"
"Get Google ROE for 2023"
```

**Multi-Company (2-5 companies):**
```
"Show Apple, Microsoft, Google revenue Q1 2023"
"Compare Apple and Microsoft ROE for 2023"
"Show all 5 companies net income Q2 2023"
```

**Ratios:**
```
"Show Apple, Microsoft, Google ROE for 2023"
"Compare all companies ROA Q1 2023"
"Get Apple, Microsoft debt-to-equity ratio 2022"
```

**Growth:**
```
"What is Apple's revenue growth YoY Q2 2023?"
"Show Microsoft quarter-over-quarter growth Q1 2023"
```

### **2. Hybrid Queries** 🔄 (SQL + 10-K Context)

**Use `/ask/hybrid` endpoint or mention keywords:**
```
"Show Apple revenue 2022 and explain business drivers"
"What drove Apple's margin changes? Show numbers and 10-K context"
"How did supply chain risks affect margins? Show data and citations"
```

**Hybrid Keywords:**
- "10-K citations", "citations"
- "macro context", "business context"
- "show me the numbers"
- "what drove", "driven by"
- "numbers and context"

---

## 🎯 **How to Use Streamlit**

### **Step 1: Enter Your Question**
Type any financial question in the text box:
```
"Show Apple, Microsoft, Google revenue Q1 2023"
```

### **Step 2: Click "Ask CFO Agent"**
The system will:
1. Classify your query
2. Route to appropriate agent(s)
3. Execute SQL or RAG or both
4. Return formatted answer

### **Step 3: View Results**
- **Answer:** Professional CFO-level response
- **Session Analytics:** Query history and stats
- **Visualizations:** Charts (when applicable)

---

## 📈 **Example Queries to Try**

### **✅ Multi-Company Comparison:**
```
"Show Apple, Microsoft, Google revenue Q1 2023"
```
**Expected:** Table with all 3 companies and their revenue

### **✅ Multi-Company Ratios:**
```
"Show Apple, Microsoft ROE for 2023"
```
**Expected:** ROE percentages for both companies

### **✅ Growth Analysis:**
```
"What is Apple's revenue growth YoY Q2 2023?"
```
**Expected:** Year-over-year growth percentage

### **✅ Peer Comparison:**
```
"Compare all companies net income Q1 2023"
```
**Expected:** Ranked list of all 5 companies

---

## 🎨 **Streamlit Features**

### **Main Interface:**
- **Question Input:** Large text box for your query
- **Ask Button:** Submit your question
- **Response Area:** Formatted answer with markdown
- **Session Analytics:** Track your queries

### **Session Management:**
- Each session has a unique ID
- View query history
- Track performance metrics
- Clear session when needed

---

## 🛠️ **API Usage (Advanced)**

### **Standard Endpoint:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show Apple, Microsoft revenue Q1 2023",
    "session_id": "user123"
  }'
```

### **Hybrid Endpoint:**
```bash
curl -X POST http://localhost:8000/ask/hybrid \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show Apple revenue 2022 and explain business drivers",
    "session_id": "user123"
  }'
```

### **Health Check:**
```bash
curl http://localhost:8000/health
```

---

## 📊 **System Performance**

- **Success Rate:** 91.9% (409/445 queries)
- **SQL Queries:** 1-2 seconds
- **Multi-Company:** 1-2 seconds
- **Ratios:** 1-2 seconds
- **Hybrid Queries:** 5-10 seconds (with LLM synthesis)

---

## ✅ **Supported Features**

### **Companies (5 Total):**
1. Apple (AAPL)
2. Microsoft (MSFT)
3. Google/Alphabet (GOOGL)
4. Amazon (AMZN)
5. Meta/Facebook (META)

### **Financial Metrics:**
- Revenue, Net Income, Gross Profit
- Operating Income, EBITDA
- Total Assets, Total Equity
- Cash Flow (Operating, Investing, Financing)
- R&D Expenses, SG&A Expenses

### **Financial Ratios:**
- ROE (Return on Equity)
- ROA (Return on Assets)
- Gross Margin, Operating Margin, Net Margin
- Debt-to-Equity Ratio
- Current Ratio, Quick Ratio

### **Time Periods:**
- Quarterly: Q1, Q2, Q3, Q4
- Annual: Full year (FY)
- Years: 2020-2023

### **Growth Calculations:**
- Year-over-Year (YoY)
- Quarter-over-Quarter (QoQ)
- Percentage changes

---

## 🎉 **You're All Set!**

**The CFO Intelligence Platform is ready to use!**

Visit: **http://localhost:8501**

Try asking:
- "Show Apple, Microsoft, Google revenue Q1 2023"
- "Compare all companies ROE for 2023"
- "What is Apple's revenue growth YoY Q2 2023?"

**Happy Analyzing! 📊**
