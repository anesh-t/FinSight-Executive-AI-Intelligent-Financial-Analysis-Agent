# 📊 Table Query Guide - 10-K Vector Database

## 🎯 **Quick Answer**

### **Which Mode to Use?**

| Goal | Mode | Why |
|------|------|-----|
| **Just extract tables from 10-K** | **Unstructured (10-K)** | Faster (3-5s), pure RAG retrieval |
| **Tables + SQL data + synthesis** | **Hybrid (SQL + 10-K)** | Complete analysis (6-10s) |
| **Just financial metrics** | **Structured (SQL)** | Fastest (1-2s), database only |

### **Recommendation for Table Queries:**
✅ **Use "Unstructured Data (10-K)" mode** for pure table extraction from 10-K filings
- Faster response (3-5 seconds)
- Direct access to 10-K content
- LLM formats tables nicely

---

## 📋 **Sample Table Queries from 10-K**

### **1. Gross Margin Tables** 📊

#### **Query:**
```
"Show me Apple's gross margin breakdown for products and services from their 10-K"
```

#### **What You'll Get:**
- Gross margin dollars (Products vs Services)
- Gross margin percentages
- Multi-year comparison (2019, 2018, 2017)
- Insights on trends

#### **Expected Table:**
```
Gross Margin ($ in millions)
| Category | 2019 | 2018 | 2017 |
|----------|------|------|------|
| Products | $68,887 | $77,683 | $70,197 |
| Services | $29,505 | $24,156 | $17,989 |
| Total    | $98,392 | $101,839 | $88,186 |

Gross Margin Percentage
| Category | 2019 | 2018 | 2017 |
|----------|------|------|------|
| Products | 32.2% | 34.4% | 35.7% |
| Services | 63.7% | 60.8% | 55.0% |
| Total    | 37.8% | 38.3% | 38.5% |
```

---

### **2. Revenue by Geographic Segment** 🌍

#### **Query:**
```
"Display Apple's revenue by geographic region from their 10-K"
```

#### **What You'll Get:**
- Americas revenue
- Europe revenue
- Greater China revenue
- Japan revenue
- Rest of Asia Pacific revenue
- Year-over-year comparisons

#### **Expected Table:**
```
Net Sales by Geographic Segment ($ in millions)
| Region | 2019 | 2018 | 2017 |
|--------|------|------|------|
| Americas | $116,914 | $112,093 | $96,600 |
| Europe | $60,288 | $62,420 | $54,938 |
| Greater China | $43,678 | $51,942 | $44,764 |
| Japan | $21,506 | $21,733 | $17,733 |
| Rest of Asia Pacific | $17,788 | $17,407 | $14,854 |
```

---

### **3. Operating Expenses Breakdown** 💰

#### **Query:**
```
"Show me Apple's operating expenses breakdown from their 10-K"
```

#### **What You'll Get:**
- Research & Development (R&D)
- Selling, General & Administrative (SG&A)
- Total operating expenses
- Percentage of revenue

#### **Expected Table:**
```
Operating Expenses ($ in millions)
| Category | 2019 | 2018 | 2017 |
|----------|------|------|------|
| R&D | $16,217 | $14,236 | $11,581 |
| SG&A | $18,245 | $16,705 | $15,261 |
| Total | $34,462 | $30,941 | $26,842 |
```

---

### **4. Product Revenue Breakdown** 📱

#### **Query:**
```
"Display Apple's revenue by product category from their 10-K"
```

#### **What You'll Get:**
- iPhone revenue
- Mac revenue
- iPad revenue
- Wearables, Home and Accessories
- Services revenue

#### **Expected Table:**
```
Net Sales by Product Category ($ in millions)
| Product | 2019 | 2018 | 2017 |
|---------|------|------|------|
| iPhone | $142,381 | $164,888 | $141,319 |
| Mac | $25,740 | $25,484 | $25,850 |
| iPad | $21,280 | $18,380 | $19,222 |
| Wearables, Home & Accessories | $24,482 | $17,381 | $12,863 |
| Services | $46,291 | $39,748 | $29,980 |
```

---

### **5. Cash Flow Statement** 💵

#### **Query:**
```
"Show me Apple's cash flow statement from their 10-K"
```

#### **What You'll Get:**
- Operating cash flow
- Investing cash flow
- Financing cash flow
- Net change in cash

#### **Expected Table:**
```
Cash Flow ($ in millions)
| Category | 2019 | 2018 | 2017 |
|----------|------|------|------|
| Operating Activities | $69,391 | $77,434 | $63,598 |
| Investing Activities | $45,896 | $16,066 | ($46,446) |
| Financing Activities | ($90,976) | ($87,876) | ($17,347) |
| Net Change | $24,311 | $5,624 | ($195) |
```

---

### **6. Balance Sheet Items** 📈

#### **Query:**
```
"Display Apple's assets and liabilities breakdown from their 10-K"
```

#### **What You'll Get:**
- Current assets
- Non-current assets
- Current liabilities
- Non-current liabilities
- Shareholders' equity

---

### **7. Segment Operating Income** 📊

#### **Query:**
```
"Show me Apple's operating income by segment from their 10-K"
```

#### **What You'll Get:**
- Operating income by product line
- Operating margins by segment
- Year-over-year changes

---

### **8. R&D Expenses Detail** 🔬

#### **Query:**
```
"Display Apple's R&D expenses breakdown from their 10-K"
```

#### **What You'll Get:**
- R&D spending by year
- R&D as percentage of revenue
- Year-over-year growth

---

## 🎯 **How to Ask for Best Results**

### **✅ Good Query Patterns:**

1. **"Show me [metric] from [company]'s 10-K"**
   - Example: "Show me Apple's gross margin from their 10-K"

2. **"Display [table name] from [company]'s 10-K"**
   - Example: "Display revenue by segment from Apple's 10-K"

3. **"What is [company]'s [metric] breakdown in their 10-K?"**
   - Example: "What is Apple's operating expenses breakdown in their 10-K?"

4. **"Extract [table] from [company]'s [year] 10-K"**
   - Example: "Extract gross margin table from Apple's 2019 10-K"

### **❌ Avoid:**
- Too vague: "Show me data"
- No source: "Show margins" (doesn't specify 10-K)
- No company: "Show revenue breakdown" (which company?)

---

## 🎨 **Complete List of Sample Queries**

### **Financial Performance Tables:**
```
1. "Show me Apple's gross margin for products and services from their 10-K"
2. "Display Apple's net sales by product category from their 10-K"
3. "Show me Apple's operating expenses breakdown from their 10-K"
4. "What is Apple's revenue by geographic segment in their 10-K?"
5. "Display Apple's quarterly revenue trends from their 10-K"
```

### **Profitability Tables:**
```
6. "Show me Apple's gross profit margin table from their 10-K"
7. "Display Apple's operating margin by segment from their 10-K"
8. "What is Apple's net income breakdown in their 10-K?"
9. "Show me Apple's earnings per share table from their 10-K"
```

### **Cash Flow Tables:**
```
10. "Display Apple's cash flow statement from their 10-K"
11. "Show me Apple's operating cash flow breakdown from their 10-K"
12. "What is Apple's free cash flow calculation in their 10-K?"
```

### **Balance Sheet Tables:**
```
13. "Show me Apple's assets breakdown from their 10-K"
14. "Display Apple's liabilities and equity from their 10-K"
15. "What is Apple's current assets composition in their 10-K?"
```

### **Segment Analysis Tables:**
```
16. "Show me Apple's revenue by geographic region from their 10-K"
17. "Display Apple's operating income by segment from their 10-K"
18. "What is Apple's product mix revenue in their 10-K?"
```

### **Expense Tables:**
```
19. "Show me Apple's R&D expenses over time from their 10-K"
20. "Display Apple's SG&A expenses breakdown from their 10-K"
21. "What is Apple's cost of revenue by category in their 10-K?"
```

---

## 🔧 **Which Mode to Use - Detailed**

### **Mode 1: Unstructured Data (10-K)** ⚡ RECOMMENDED FOR TABLES
**Use When:**
- You want pure 10-K table extraction
- You need narrative context from filings
- You want faster responses (3-5s)

**Example:**
```
Mode: Unstructured Data (10-K)
Query: "Show me Apple's gross margin table from their 10-K"
Result: Clean table from 10-K with context
Time: 3-5 seconds
```

**Pros:**
- ✅ Faster (3-5 seconds)
- ✅ Direct 10-K access
- ✅ Gets exact table data
- ✅ Includes narrative context

**Cons:**
- ❌ No SQL database data
- ❌ No cross-source synthesis

---

### **Mode 2: Hybrid (SQL + 10-K)** 🔄 FOR COMPREHENSIVE ANALYSIS
**Use When:**
- You want both SQL data AND 10-K tables
- You need synthesis of multiple sources
- You want business context + numbers

**Example:**
```
Mode: Hybrid (SQL + 10-K)
Query: "Show Apple's gross margin and explain what drove the changes with 10-K citations"
Result: SQL data + 10-K table + LLM synthesis
Time: 6-10 seconds
```

**Pros:**
- ✅ Complete analysis
- ✅ SQL data + 10-K insights
- ✅ LLM synthesis
- ✅ Business context

**Cons:**
- ⏱️ Slower (6-10 seconds)
- ⚠️ Needs hybrid keywords

---

### **Mode 3: Structured Data (SQL)** ⚡⚡ FASTEST
**Use When:**
- You want database metrics only
- You need fastest response
- You don't need 10-K narrative

**Example:**
```
Mode: Structured Data (SQL)
Query: "Show Apple gross margin for 2023"
Result: Database metrics only
Time: 1-2 seconds
```

**Pros:**
- ✅ Fastest (1-2 seconds)
- ✅ Reliable
- ✅ Multi-company support

**Cons:**
- ❌ No 10-K tables
- ❌ No narrative context

---

## 🎯 **Recommendation Summary**

### **For Table Extraction from 10-K:**
✅ **Use "Unstructured Data (10-K)" Mode**

### **Sample Workflow:**

1. **Open Streamlit:** http://localhost:8501
2. **Select Mode:** "Unstructured Data (10-K)"
3. **Ask:** "Show me Apple's gross margin breakdown from their 10-K"
4. **Wait:** 3-5 seconds
5. **Get:** Beautifully formatted table with context

### **Top 5 Table Queries to Try:**

1. **Gross Margin:**
   ```
   "Show me Apple's gross margin for products and services from their 10-K"
   ```

2. **Revenue by Segment:**
   ```
   "Display Apple's revenue by geographic region from their 10-K"
   ```

3. **Operating Expenses:**
   ```
   "Show me Apple's operating expenses breakdown from their 10-K"
   ```

4. **Product Revenue:**
   ```
   "Display Apple's revenue by product category from their 10-K"
   ```

5. **Cash Flow:**
   ```
   "Show me Apple's cash flow statement from their 10-K"
   ```

---

## ✅ **Ready to Test!**

**System Status:**
- ✅ Backend: http://localhost:8000
- ✅ Streamlit: http://localhost:8501
- ✅ Vector DB: Loaded with 10-K tables
- ✅ RAG Agent: Ready to extract tables

**Start with:**
1. Open Streamlit
2. Select "Unstructured Data (10-K)"
3. Try: "Show me Apple's gross margin breakdown from their 10-K"
4. See the magic! 🎉

**Your agent is ready to extract and format tables from 10-K filings!** 📊
