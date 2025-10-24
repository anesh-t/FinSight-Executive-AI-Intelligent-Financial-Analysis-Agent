# 📊 EPS Data Flow - How the System Sources EPS Data

## 🔍 When You Ask: "Show Microsoft EPS for 2023"

### **Step-by-Step Flow:**

```
User Query: "show microsoft eps for 2023"
     ↓
[1] DECOMPOSER (decomposer.py)
     ↓
   Analyzes query and selects template: "annual_metrics"
     ↓
[2] TEMPLATE (templates.json)
     ↓
   Selected: "annual_metrics" template
     ↓
[3] SQL QUERY EXECUTION
     ↓
   Executes SQL against Supabase database
     ↓
[4] DATABASE TABLES
     ↓
   Sources: fact_financials + mv_financials_annual
     ↓
[5] FORMATTER (formatter.py)
     ↓
   Formats result and displays EPS value
     ↓
[6] USER RESPONSE
   "Microsoft reported EPS of $2.76 for FY2023"
```

---

## 📝 **Detailed Breakdown:**

### **1. DECOMPOSER (decomposer.py)**
- Receives: `"show microsoft eps for 2023"`
- Identifies:
  - Company: Microsoft (MSFT)
  - Metric: EPS
  - Time period: Annual 2023
- Selects template: **`annual_metrics`**
- Extracts parameters: `ticker=MSFT`, `fy=2023`

---

### **2. TEMPLATE (templates.json - Line 11-18)**

**Template: `annual_metrics`**

```json
{
  "intent": "annual_metrics",
  "surface": "fact_financials, mv_financials_annual, mv_ratios_annual",
  "description": "Get annual financial metrics...",
  "sql": "SELECT ... AVG(f.eps) as eps FROM mv_financials_annual mv ... 
          LEFT JOIN fact_financials f ON f.company_id = mv.company_id 
          AND f.fiscal_year = mv.fiscal_year ...",
  "params": ["ticker", "fy", "limit"]
}
```

**Key SQL snippet for EPS:**
```sql
AVG(f.eps) as eps
FROM mv_financials_annual mv
LEFT JOIN fact_financials f 
  ON f.company_id = mv.company_id 
  AND f.fiscal_year = mv.fiscal_year
WHERE c.ticker = 'MSFT' 
  AND mv.fiscal_year = 2023
GROUP BY ...
```

---

### **3. DATABASE SOURCE:**

#### **For Annual EPS (2023):**
```sql
-- Sources from fact_financials, calculates average
SELECT AVG(f.eps) as eps
FROM fact_financials f
WHERE fiscal_year = 2023
AND company_id = (SELECT company_id FROM dim_company WHERE ticker = 'MSFT')

-- This averages all 4 quarters:
-- Q1 2023: $2.45
-- Q2 2023: $2.69
-- Q3 2023: $2.99
-- Q4 2023: $2.93
-- Average: $2.76
```

#### **Database Table Structure:**
```
fact_financials
├── company_id
├── fiscal_year
├── fiscal_quarter
├── eps              ← EPS SOURCE
├── revenue
├── net_income
└── ... (other metrics)
```

---

### **4. FORMATTER (formatter.py)**

**Code that displays EPS (lines 398-403):**
```python
# Per-share metrics
if (show_all or 'eps' in requested_metrics):
    if 'eps' in row and row['eps'] is not None:
        parts.append(f"EPS of ${row['eps']:.2f}")
    elif 'earnings_per_share' in row and row['earnings_per_share'] is not None:
        parts.append(f"EPS of ${row['earnings_per_share']:.2f}")
```

---

## 🔄 **Comparison: Quarterly vs Annual EPS**

### **Quarterly EPS Query:**
**User asks:** `"show microsoft eps for Q2 2023"`

**Template used:** `quarter_snapshot`

**SQL:**
```sql
SELECT f.eps
FROM fact_financials f
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'MSFT'
  AND f.fiscal_year = 2023
  AND f.fiscal_quarter = 2
```

**Result:** Returns single value: `$2.69`

**Data source:** `fact_financials.eps` (direct, no calculation)

---

### **Annual EPS Query:**
**User asks:** `"show microsoft eps for 2023"`

**Template used:** `annual_metrics`

**SQL:**
```sql
SELECT AVG(f.eps) as eps
FROM fact_financials f
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'MSFT'
  AND f.fiscal_year = 2023
GROUP BY f.fiscal_year
```

**Result:** Returns average: `$2.76`

**Data source:** `AVG(fact_financials.eps)` across all quarters

---

## 📊 **Example with Real Data:**

### **Query:** "show microsoft eps for 2023"

#### **Backend Process:**

1. **Database Query Executed:**
```sql
SELECT 
  c.ticker, 
  c.name, 
  mv.fiscal_year, 
  AVG(f.eps) as eps
FROM mv_financials_annual mv
JOIN dim_company c USING (company_id)
LEFT JOIN fact_financials f 
  ON f.company_id = mv.company_id 
  AND f.fiscal_year = mv.fiscal_year
WHERE c.ticker = 'MSFT' 
  AND mv.fiscal_year = 2023
GROUP BY c.ticker, c.name, mv.fiscal_year
```

2. **Data Retrieved from fact_financials:**
| fiscal_year | fiscal_quarter | eps |
|-------------|----------------|-----|
| 2023 | 1 | $2.45 |
| 2023 | 2 | $2.69 |
| 2023 | 3 | $2.99 |
| 2023 | 4 | $2.93 |

3. **Calculation:**
```
AVG(eps) = (2.45 + 2.69 + 2.99 + 2.93) / 4 = 11.06 / 4 = 2.76
```

4. **Response Formatted:**
```
"Microsoft Corporation (MSFT) reported EPS of $2.76 for FY2023."
```

---

## 🎯 **Key Insights:**

### **EPS Data Sources:**

| Query Type | Template | Database Table | Calculation |
|------------|----------|----------------|-------------|
| **Quarterly** | `quarter_snapshot` | `fact_financials.eps` | Direct value (no calc) |
| **Annual** | `annual_metrics` | `fact_financials.eps` | AVG of 4 quarters |
| **TTM** | `ttm_snapshot` | `mv_financials_ttm` | Not currently included |

### **Why AVG instead of SUM for annual EPS?**
- EPS is a **per-share** metric
- Summing would incorrectly multiply the value by 4
- Averaging gives the **typical EPS per quarter** for the year
- This represents the **annual earning power per share**

### **Data Quality:**
- ✅ Source: `fact_financials` table (single source of truth)
- ✅ Quarterly data: Direct from database
- ✅ Annual data: Calculated average (consistent methodology)
- ✅ All 5 companies have complete data (2019-2025)

---

## 🔧 **Technical Details:**

### **Database Connection:**
- Pool: `db_pool` (db/pool.py)
- Database: Supabase PostgreSQL
- Connection: Read-only async connection pool

### **Query Executor:**
- File: `catalog/executor.py`
- Function: `execute_query()`
- Returns: DataFrame with query results

### **Response Formatter:**
- File: `formatter.py`
- Function: `_generate_simple_summary()`
- Logic: Checks for `'eps' in requested_metrics` to show/hide EPS

---

## 📌 **Summary:**

**When you ask "show microsoft eps for 2023":**

1. ✅ Decomposer picks `annual_metrics` template
2. ✅ SQL queries `fact_financials` table
3. ✅ Calculates `AVG(eps)` across Q1-Q4 2023
4. ✅ Returns: `$2.76` (average of $2.45, $2.69, $2.99, $2.93)
5. ✅ Formatter displays: "Microsoft reported EPS of $2.76 for FY2023"

**Data Flow:**
```
fact_financials (quarterly data) 
    → AVG calculation 
    → annual EPS 
    → formatted response
```
