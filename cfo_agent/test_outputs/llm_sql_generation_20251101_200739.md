# 🤖 LLM-BASED SQL GENERATION TEST RESULTS

**Generated:** 2025-11-01 20:07:39
**Method:** GPT-4o with 549-line prompt
**Setting:** use_generative = True

---

## Test 1: Basic

### 💬 User Question:
> Show Apple's revenue for Q2 2023

### ✅ Success

**Generation Time:** 2.06s

### 🤖 GPT-4o Generated SQL:

```sql
SELECT 
    c.ticker,
    cc.fiscal_year,
    cc.fiscal_quarter,
    cc.revenue / 1e9 as revenue_b
FROM vw_company_complete_quarter cc
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL'
  AND cc.fiscal_year = 2023
  AND cc.fiscal_quarter = 2
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

### 📊 Results (1 rows):

| ticker | fiscal_year | fiscal_quarter | revenue_b |
| --- | --- | --- | --- |
| AAPL | 2,023.00 | 2.00 | 81.7970000000000000 |

---

## Test 2: Basic

### 💬 User Question:
> What is Microsoft's net income in Q1 2023?

### ✅ Success

**Generation Time:** 2.23s

### 🤖 GPT-4o Generated SQL:

```sql
SELECT 
    c.ticker,
    cc.fiscal_year,
    cc.fiscal_quarter,
    cc.net_income / 1e9 as net_income_b
FROM vw_company_complete_quarter cc
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'MSFT'
  AND cc.fiscal_year = 2023
  AND cc.fiscal_quarter = 1
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

### 📊 Results (1 rows):

| ticker | fiscal_year | fiscal_quarter | net_income_b |
| --- | --- | --- | --- |
| MSFT | 2,023.00 | 1.00 | 18.2990000000000000 |

---

## Test 3: Multiple Metrics

### 💬 User Question:
> Show Apple's revenue, net income, and gross margin for Q2 2023

### ✅ Success

**Generation Time:** 1.69s

### 🤖 GPT-4o Generated SQL:

```sql
SELECT 
    c.ticker,
    cc.fiscal_year,
    cc.fiscal_quarter,
    cc.revenue / 1e9 as revenue_b,
    cc.net_income / 1e9 as net_income_b,
    cc.gross_margin * 100 as gross_margin_pct
FROM vw_company_complete_quarter cc
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL'
  AND cc.fiscal_year = 2023
  AND cc.fiscal_quarter = 2
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

### 📊 Results (1 rows):

| ticker | fiscal_year | fiscal_quarter | revenue_b | net_income_b | gross_margin_pct |
| --- | --- | --- | --- | --- | --- |
| AAPL | 2,023.00 | 2.00 | 81.7970000000000000 | 19.8810000000000000 | 44.51630255388339425700 |

---

## Test 4: Complex

### 💬 User Question:
> Show me Apple's revenue, operating income, R&D expenses, stock price, and volatility for Q2 2023

### ✅ Success

**Generation Time:** 2.24s

### 🤖 GPT-4o Generated SQL:

```sql
SELECT 
    c.ticker,
    cc.fiscal_year,
    cc.fiscal_quarter,
    cc.revenue / 1e9 as revenue_b,
    cc.operating_income / 1e9 as operating_income_b,
    cc.r_and_d_expenses / 1e9 as rnd_expenses_b,
    cc.close_price,
    cc.volatility_pct * 100 as volatility_pct
FROM vw_company_complete_quarter cc
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL'
  AND cc.fiscal_year = 2023
  AND cc.fiscal_quarter = 2
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

### 📊 Results (1 rows):

| ticker | fiscal_year | fiscal_quarter | revenue_b | operating_income_b | rnd_expenses_b | close_price | volatility_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | 2,023.00 | 2.00 | 81.7970000000000000 | 22.9980000000000000 | 7.4420000000000000 | 192.320007 | 43.81571961519516413900 |

---

## Test 5: Time Series

### 💬 User Question:
> Show Apple's revenue for the last 4 quarters

### ✅ Success

**Generation Time:** 1.71s

### 🤖 GPT-4o Generated SQL:

```sql
SELECT 
    c.ticker,
    cc.fiscal_year,
    cc.fiscal_quarter,
    cc.revenue / 1e9 as revenue_b
FROM vw_company_complete_quarter cc
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL'
ORDER BY cc.fiscal_year DESC, cc.fiscal_quarter DESC
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

### 📊 Results (10 rows):

| ticker | fiscal_year | fiscal_quarter | revenue_b |
| --- | --- | --- | --- |
| AAPL | 2,025.00 | 2.00 | 94.0360000000000000 |
| AAPL | 2,025.00 | 1.00 | 95.3590000000000000 |
| AAPL | 2,024.00 | 4.00 | 124.3000000000000000 |
| AAPL | 2,024.00 | 3.00 | 94.9300000000000000 |
| AAPL | 2,024.00 | 2.00 | 85.7770000000000000 |

*... and 5 more rows*

---

## Test 6: Macro Context

### 💬 User Question:
> Show Apple's revenue with GDP and CPI for Q2 2023

### ✅ Success

**Generation Time:** 1.86s

### 🤖 GPT-4o Generated SQL:

```sql
SELECT 
    c.ticker,
    cmc.fiscal_year,
    cmc.fiscal_quarter,
    cmc.revenue / 1e9 as revenue_b,
    cmc.gdp / 1e12 as gdp_t,
    cmc.cpi
FROM vw_company_macro_context_quarter cmc
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL'
  AND cmc.fiscal_year = 2023
  AND cmc.fiscal_quarter = 2
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

### 📊 Results (1 rows):

| ticker | fiscal_year | fiscal_quarter | revenue_b | gdp_t | cpi |
| --- | --- | --- | --- | --- | --- |
| AAPL | 2,023.00 | 2.00 | 81.7970000000000000 | 2.2539418000000000E-8 | 303.4243333333333 |

---

## Test 7: Growth

### 💬 User Question:
> Show Apple's revenue growth YoY for Q2 2023

### ❌ Error:
```
Query execution failed: column g.revenue_yoy_growth does not exist
```

---

## Test 8: Comparison

### 💬 User Question:
> Compare Apple and Microsoft revenue for Q2 2023

### ❌ Error:
```
Query execution failed: column ps.metric_value does not exist
```

---

## Test 9: Annual

### 💬 User Question:
> Show Apple's annual revenue for 2023

### ✅ Success

**Generation Time:** 1.31s

### 🤖 GPT-4o Generated SQL:

```sql
SELECT 
    c.ticker,
    ca.fiscal_year,
    ca.revenue_annual / 1e9 as revenue_annual_b
FROM mv_company_complete_annual ca
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL'
  AND ca.fiscal_year = 2023
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

### 📊 Results (1 rows):

| ticker | fiscal_year | revenue_annual_b |
| --- | --- | --- |
| AAPL | 2,023.00 | 385.7060000000000000 |

---

## Test 10: Latest

### 💬 User Question:
> Show Apple's latest quarter results

### ❌ Error:
```
Query execution failed: column lq.latest_fy does not exist
```

---


## 📊 Summary

- **Total Tests:** 10
- **Successful:** 7 (70.0%)
- **Failed:** 3

- **Average Generation Time:** 1.87s
