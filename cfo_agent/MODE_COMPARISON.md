# 🔄 Mode Comparison - What You Get

## 📊 **Your Query:** "Show me Apple's gross margin breakdown from their 10-K"

---

## ❌ **What You Got (Structured Data Mode)**

**Mode Used:** Structured Data (SQL)

**Response:**
```
Apple Inc. (AAPL) reported gross margin of 46.8% for FY2025.
Sources: Financial Database
```

**Why This Happened:**
- You were in "Structured Data (SQL)" mode
- This mode queries the PostgreSQL database
- Database has only summary metrics (one number: 46.8%)
- No detailed table breakdown
- No Products vs Services split

---

## ✅ **What You Should Get (Unstructured Data Mode)**

**Mode to Use:** Unstructured Data (10-K)

**Expected Response:**
```
Apple Inc. Gross Margin Breakdown (from 2019 Form 10-K)

Gross Margin ($ in millions)
┌──────────┬──────────┬──────────┬──────────┐
│ Category │   2019   │   2018   │   2017   │
├──────────┼──────────┼──────────┼──────────┤
│ Products │ $68,887  │ $77,683  │ $70,197  │
│ Services │ $29,505  │ $24,156  │ $17,989  │
│ Total    │ $98,392  │ $101,839 │ $88,186  │
└──────────┴──────────┴──────────┴──────────┘

Gross Margin Percentage
┌──────────┬───────┬───────┬───────┐
│ Category │ 2019  │ 2018  │ 2017  │
├──────────┼───────┼───────┼───────┤
│ Products │ 32.2% │ 34.4% │ 35.7% │
│ Services │ 63.7% │ 60.8% │ 55.0% │
│ Total    │ 37.8% │ 38.3% │ 38.5% │
└──────────┴───────┴───────┴───────┘

Key Insights:
- Products gross margin decreased from $77.7B (2018) to $68.9B (2019)
- Services gross margin increased from $24.2B (2018) to $29.5B (2019)
- Services have significantly higher margins (63.7%) vs Products (32.2%)
- Total gross margin percentage declined from 38.3% to 37.8%

Drivers:
- Products: Lower iPhone unit sales, currency headwinds
- Services: Higher net sales, favorable mix

Source: Apple Inc. 2019 Form 10-K
```

---

## 🔍 **Side-by-Side Comparison**

| Aspect | Structured Data (SQL) | Unstructured Data (10-K) |
|--------|----------------------|--------------------------|
| **What You Got** | 46.8% (one number) | Full table with breakdown |
| **Detail Level** | Summary only | Products vs Services |
| **Time Period** | Single year | Multi-year (2017-2019) |
| **Context** | None | Business drivers, insights |
| **Source** | Database | 10-K filing |
| **Response Time** | 5 seconds | 3-5 seconds |
| **Table Format** | No table | Formatted markdown table |

---

## 🎯 **How to Get the Table**

### **Step-by-Step:**

1. **In Streamlit Sidebar:**
   - Look for the mode selector
   - Currently shows: "📊 Mode: Structured Data (SQL)"
   - **Click to change it**

2. **Select:**
   - ✅ **"Unstructured Data (10-K)"** ← Choose this!
   - Not "Structured Data (SQL)"
   - Not "Hybrid (SQL + 10-K)" (unless you want both)

3. **Ask the Same Question:**
   ```
   "Show me Apple's gross margin breakdown from their 10-K"
   ```

4. **Get the Table:**
   - Full breakdown: Products vs Services
   - Multi-year comparison
   - Percentages and dollar amounts
   - Business context and insights

---

## 📊 **Visual Guide**

### **Current Mode (What You Used):**
```
┌─────────────────────────────────────┐
│ 📊 Mode: Structured Data (SQL)     │ ← You are here
├─────────────────────────────────────┤
│                                     │
│ Queries: PostgreSQL Database       │
│ Returns: Summary metrics only      │
│ Example: "46.8% gross margin"      │
│                                     │
└─────────────────────────────────────┘
```

### **Mode You Need (For Tables):**
```
┌─────────────────────────────────────┐
│ 📖 Mode: Unstructured Data (10-K)  │ ← Switch to this!
├─────────────────────────────────────┤
│                                     │
│ Queries: Vector Database (10-K)    │
│ Returns: Detailed tables           │
│ Example: Full margin breakdown     │
│                                     │
└─────────────────────────────────────┘
```

---

## 🎨 **What Each Mode Does**

### **1. Structured Data (SQL)** 📊
**What it queries:**
- PostgreSQL database
- Structured financial metrics
- Summary data only

**Best for:**
- Quick metrics: "What is Apple revenue?"
- Multi-company: "Compare Apple and Microsoft"
- Ratios: "Show ROE for all companies"

**Example Response:**
```
Apple Inc. (AAPL) reported gross margin of 46.8% for FY2025.
```

---

### **2. Unstructured Data (10-K)** 📖
**What it queries:**
- Vector database with 10-K filings
- Detailed tables and narratives
- Business context

**Best for:**
- Tables: "Show gross margin breakdown"
- Context: "Explain business drivers"
- Details: "Show revenue by segment"

**Example Response:**
```
[Full table with Products vs Services breakdown]
[Multi-year comparison]
[Business insights and drivers]
```

---

### **3. Hybrid (SQL + 10-K)** 🔄
**What it queries:**
- Both SQL database AND 10-K filings
- Synthesizes both sources

**Best for:**
- Comprehensive analysis
- "Show numbers and explain drivers"
- "What drove the change with citations"

**Example Response:**
```
[SQL metrics: 46.8% gross margin]
[10-K table: Products vs Services breakdown]
[LLM synthesis: Combined insights]
```

---

## ✅ **Quick Fix for Your Query**

### **What to Do Now:**

1. **Look at Streamlit sidebar** (left side of screen)

2. **Find the mode selector** - it should say:
   ```
   📊 Mode: Structured Data (SQL)
   ```

3. **Click on it and change to:**
   ```
   📖 Unstructured Data (10-K)
   ```

4. **Ask again:**
   ```
   "Show me Apple's gross margin breakdown from their 10-K"
   ```

5. **You'll get:**
   - ✅ Full table with Products vs Services
   - ✅ Multi-year comparison (2017-2019)
   - ✅ Both dollar amounts and percentages
   - ✅ Business insights and context

---

## 🎯 **Summary**

### **Problem:**
You asked for a 10-K table but were in SQL mode, so you got only a summary number.

### **Solution:**
Switch to "Unstructured Data (10-K)" mode in the sidebar.

### **Result:**
You'll get the full detailed table from the 10-K filing with:
- Products vs Services breakdown
- Multi-year comparison
- Dollar amounts and percentages
- Business context

---

## 🚀 **Try It Now!**

**Steps:**
1. Switch mode to "Unstructured Data (10-K)"
2. Ask: "Show me Apple's gross margin breakdown from their 10-K"
3. See the full table! 📊

**Your agent has the table data - you just need to use the right mode!** ✅
