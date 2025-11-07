# 🔬 GPT-4o SQL GENERATION - DATA ACCURACY TEST

**Generated:** 2025-11-02 00:14:24
**Total Queries:** 16
**Method:** GPT-4o with schema-aware prompt

---

## Test 1: Basic Revenue

### 💬 Query:
> Show Apple's revenue for Q2 2023

### ✅ Success - ✅ ACCURATE

**Generation Time:** 1.73s  
**Rows Returned:** 1

#### 📊 Results:

| ticker | fiscal_year | fiscal_quarter | revenue_b |
| --- | --- | --- | --- |
| AAPL | 2,023.00 | 2.00 | 81.7970000000000000 |

<details>
<summary>🔍 SQL Query</summary>

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

</details>

---

## Test 2: Basic Net Income

### 💬 Query:
> What is Microsoft's net income Q1 2023?

### ✅ Success - ✅ ACCURATE

**Generation Time:** 1.63s  
**Rows Returned:** 1

#### 📊 Results:

| ticker | fiscal_year | fiscal_quarter | net_income_b |
| --- | --- | --- | --- |
| MSFT | 2,023.00 | 1.00 | 18.2990000000000000 |

<details>
<summary>🔍 SQL Query</summary>

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

</details>

---

## Test 3: Basic Operating Income

### 💬 Query:
> Show Google's operating income Q3 2023

### ✅ Success - ⚠️ INACCURATE

**Generation Time:** 1.12s  
**Rows Returned:** 0

#### ⚠️ Data Accuracy Issues:
- No data returned

<details>
<summary>🔍 SQL Query</summary>

```sql
SELECT 
    c.ticker,
    cc.fiscal_year,
    cc.fiscal_quarter,
    cc.operating_income / 1e9 as operating_income_b
FROM vw_company_complete_quarter cc
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'GOOGL'
  AND cc.fiscal_year = 2023
  AND cc.fiscal_quarter = 3
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

</details>

---

## Test 4: Multi-Metric

### 💬 Query:
> Show Apple's revenue and net income for Q2 2023

### ✅ Success - ✅ ACCURATE

**Generation Time:** 1.27s  
**Rows Returned:** 1

#### 📊 Results:

| ticker | fiscal_year | fiscal_quarter | revenue_b | net_income_b |
| --- | --- | --- | --- | --- |
| AAPL | 2,023.00 | 2.00 | 81.7970000000000000 | 19.8810000000000000 |

<details>
<summary>🔍 SQL Query</summary>

```sql
SELECT 
    c.ticker,
    cc.fiscal_year,
    cc.fiscal_quarter,
    cc.revenue / 1e9 as revenue_b,
    cc.net_income / 1e9 as net_income_b
FROM vw_company_complete_quarter cc
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL'
  AND cc.fiscal_year = 2023
  AND cc.fiscal_quarter = 2
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

</details>

---

## Test 5: Multi-Metric 3

### 💬 Query:
> Get Microsoft's revenue, operating income, and gross profit Q1 2023

### ✅ Success - ✅ ACCURATE

**Generation Time:** 0.86s  
**Rows Returned:** 1

#### 📊 Results:

| ticker | fiscal_year | fiscal_quarter | revenue_b | operating_income_b | gross_profit_b |
| --- | --- | --- | --- | --- | --- |
| MSFT | 2,023.00 | 1.00 | 52.8570000000000000 | 22.3520000000000000 | 36.7290000000000000 |

<details>
<summary>🔍 SQL Query</summary>

```sql
SELECT 
    c.ticker,
    cc.fiscal_year,
    cc.fiscal_quarter,
    cc.revenue / 1e9 as revenue_b,
    cc.operating_income / 1e9 as operating_income_b,
    cc.gross_profit / 1e9 as gross_profit_b
FROM vw_company_complete_quarter cc
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'MSFT'
  AND cc.fiscal_year = 2023
  AND cc.fiscal_quarter = 1
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

</details>

---

## Test 6: Ratio - Gross Margin

### 💬 Query:
> What is Apple's gross margin for Q2 2023?

### ✅ Success - ⚠️ INACCURATE

**Generation Time:** 1.31s  
**Rows Returned:** 1

#### ⚠️ Data Accuracy Issues:
- gross_margin = 44.51630255388339425700 outside expected range [0.43, 0.46]

#### 📊 Results:

| ticker | fiscal_year | fiscal_quarter | gross_margin_pct |
| --- | --- | --- | --- |
| AAPL | 2,023.00 | 2.00 | 44.51630255388339425700 |

<details>
<summary>🔍 SQL Query</summary>

```sql
SELECT 
    c.ticker,
    cc.fiscal_year,
    cc.fiscal_quarter,
    cc.gross_margin * 100 as gross_margin_pct
FROM vw_company_complete_quarter cc
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL'
  AND cc.fiscal_year = 2023
  AND cc.fiscal_quarter = 2
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

</details>

---

## Test 7: Ratio - ROE

### 💬 Query:
> Show Microsoft's ROE Q1 2023

### ✅ Success - ⚠️ INACCURATE

**Generation Time:** 1.41s  
**Rows Returned:** 1

#### ⚠️ Data Accuracy Issues:
- roe = 9.39938258605014305300 outside expected range [0.35, 0.45]

#### 📊 Results:

| ticker | fiscal_year | fiscal_quarter | roe_pct |
| --- | --- | --- | --- |
| MSFT | 2,023.00 | 1.00 | 9.39938258605014305300 |

<details>
<summary>🔍 SQL Query</summary>

```sql
SELECT 
    c.ticker,
    cc.fiscal_year,
    cc.fiscal_quarter,
    cc.roe * 100 as roe_pct
FROM vw_company_complete_quarter cc
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'MSFT'
  AND cc.fiscal_year = 2023
  AND cc.fiscal_quarter = 1
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

</details>

---

## Test 8: Growth YoY

### 💬 Query:
> Show Apple's revenue growth YoY for Q2 2023

### ✅ Success - ⚠️ INACCURATE

**Generation Time:** 0.98s  
**Rows Returned:** 1

#### ⚠️ Data Accuracy Issues:
- revenue_yoy = -1.40069190805096493400 outside expected range [-0.05, 0.1]

#### 📊 Results:

| ticker | fiscal_year | fiscal_quarter | revenue_yoy_growth_pct |
| --- | --- | --- | --- |
| AAPL | 2,023.00 | 2.00 | -1.40069190805096493400 |

<details>
<summary>🔍 SQL Query</summary>

```sql
SELECT 
    c.ticker,
    g.fiscal_year,
    g.fiscal_quarter,
    g.revenue_yoy * 100 as revenue_yoy_growth_pct
FROM vw_growth_quarter g
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL'
  AND g.fiscal_year = 2023
  AND g.fiscal_quarter = 2
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

</details>

---

## Test 9: Stock Price

### 💬 Query:
> What is Apple's stock price for Q2 2023?

### ✅ Success - ✅ ACCURATE

**Generation Time:** 1.24s  
**Rows Returned:** 1

#### 📊 Results:

| ticker | fiscal_year | fiscal_quarter | close_price |
| --- | --- | --- | --- |
| AAPL | 2,023.00 | 2.00 | 192.320007 |

<details>
<summary>🔍 SQL Query</summary>

```sql
SELECT 
    c.ticker,
    cc.fiscal_year,
    cc.fiscal_quarter,
    cc.close_price
FROM vw_company_complete_quarter cc
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL'
  AND cc.fiscal_year = 2023
  AND cc.fiscal_quarter = 2
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

</details>

---

## Test 10: Time Series

### 💬 Query:
> Show Apple's revenue for the last 4 quarters

### ✅ Success - ✅ ACCURATE

**Generation Time:** 1.44s  
**Rows Returned:** 10

#### 📊 Results:

| ticker | fiscal_year | fiscal_quarter | revenue_b |
| --- | --- | --- | --- |
| AAPL | 2,025.00 | 2.00 | 94.0360000000000000 |
| AAPL | 2,025.00 | 1.00 | 95.3590000000000000 |
| AAPL | 2,024.00 | 4.00 | 124.3000000000000000 |
| AAPL | 2,024.00 | 3.00 | 94.9300000000000000 |
| AAPL | 2,024.00 | 2.00 | 85.7770000000000000 |

*... and 5 more rows*

<details>
<summary>🔍 SQL Query</summary>

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

</details>

---

## Test 11: Annual

### 💬 Query:
> Show Apple's annual revenue for 2023

### ✅ Success - ✅ ACCURATE

**Generation Time:** 1.41s  
**Rows Returned:** 1

#### 📊 Results:

| ticker | fiscal_year | revenue_annual_b |
| --- | --- | --- |
| AAPL | 2,023.00 | 385.7060000000000000 |

<details>
<summary>🔍 SQL Query</summary>

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

</details>

---

## Test 12: Latest

### 💬 Query:
> Show Apple's latest quarter results

### ✅ Success - ✅ ACCURATE

**Generation Time:** 1.38s  
**Rows Returned:** 1

#### 📊 Results:

| ticker | fiscal_year | fiscal_quarter | revenue_b | gross_margin_pct | net_income_b | eps | close_price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | 2,025.00 | 2.00 | 94.0360000000000000 | 46.49070568718363180100 | 23.4340000000000000 | 1.5676825919732431 | None |

<details>
<summary>🔍 SQL Query</summary>

```sql
SELECT 
    c.ticker,
    cc.fiscal_year,
    cc.fiscal_quarter,
    cc.revenue / 1e9 as revenue_b,
    cc.gross_margin * 100 as gross_margin_pct,
    cc.net_income / 1e9 as net_income_b,
    cc.eps,
    cc.close_price
FROM vw_company_complete_quarter cc
JOIN dim_company c USING (company_id)
JOIN vw_latest_company_quarter lq 
    ON cc.company_id = lq.company_id
    AND cc.fiscal_year = lq.fiscal_year
    AND cc.fiscal_quarter = lq.fiscal_quarter
WHERE c.ticker = 'AAPL'
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

</details>

---

## Test 13: Comparison

### 💬 Query:
> Compare Apple and Microsoft revenue Q2 2023

### ✅ Success - ✅ ACCURATE

**Generation Time:** 1.43s  
**Rows Returned:** 2

#### 📊 Results:

| ticker | fiscal_year | fiscal_quarter | revenue_b | rank_revenue | pct_revenue |
| --- | --- | --- | --- | --- | --- |
| MSFT | 2,023.00 | 2.00 | 56.1890000000000000 | 4.00 | 0.4000 |
| AAPL | 2,023.00 | 2.00 | 81.7970000000000000 | 2.00 | 0.8000 |

<details>
<summary>🔍 SQL Query</summary>

```sql
SELECT 
    c.ticker,
    ps.fiscal_year,
    ps.fiscal_quarter,
    ps.revenue / 1e9 as revenue_b,
    ps.rank_revenue,
    ps.pct_revenue
FROM vw_peer_stats_quarter ps
JOIN dim_company c USING (company_id)
WHERE c.ticker IN ('AAPL', 'MSFT')
  AND ps.fiscal_year = 2023
  AND ps.fiscal_quarter = 2
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

</details>

---

## Test 14: Complex 5-Metric

### 💬 Query:
> Show Apple's revenue, operating income, R&D, stock price, and volatility Q2 2023

### ✅ Success - ✅ ACCURATE

**Generation Time:** 1.23s  
**Rows Returned:** 1

#### 📊 Results:

| ticker | fiscal_year | fiscal_quarter | revenue_b | operating_income_b | rnd_expenses_b | close_price | volatility_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | 2,023.00 | 2.00 | 81.7970000000000000 | 22.9980000000000000 | 7.4420000000000000 | 192.320007 | 43.81571961519516413900 |

<details>
<summary>🔍 SQL Query</summary>

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

</details>

---

## Test 15: Period Q1 2024

### 💬 Query:
> Show Apple's revenue for Q1 2024

### ✅ Success - ✅ ACCURATE

**Generation Time:** 0.92s  
**Rows Returned:** 1

#### 📊 Results:

| ticker | fiscal_year | fiscal_quarter | revenue_b |
| --- | --- | --- | --- |
| AAPL | 2,024.00 | 1.00 | 90.7530000000000000 |

<details>
<summary>🔍 SQL Query</summary>

```sql
SELECT 
    c.ticker,
    cc.fiscal_year,
    cc.fiscal_quarter,
    cc.revenue / 1e9 as revenue_b
FROM vw_company_complete_quarter cc
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL'
  AND cc.fiscal_year = 2024
  AND cc.fiscal_quarter = 1
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

</details>

---

## Test 16: Period Q3 2024

### 💬 Query:
> Show Apple's revenue for Q3 2024

### ✅ Success - ✅ ACCURATE

**Generation Time:** 0.76s  
**Rows Returned:** 1

#### 📊 Results:

| ticker | fiscal_year | fiscal_quarter | revenue_b |
| --- | --- | --- | --- |
| AAPL | 2,024.00 | 3.00 | 94.9300000000000000 |

<details>
<summary>🔍 SQL Query</summary>

```sql
SELECT 
    c.ticker,
    cc.fiscal_year,
    cc.fiscal_quarter,
    cc.revenue / 1e9 as revenue_b
FROM vw_company_complete_quarter cc
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL'
  AND cc.fiscal_year = 2024
  AND cc.fiscal_quarter = 3
LIMIT :limit;
```

**Parameters:** `{'limit': 10}`

</details>

---


## 📊 Summary

- **Total Tests:** 16
- **Successful:** 16 (100.0%)
- **Data Accurate:** 12 (75.0%)
- **Failed:** 0

- **Average Generation Time:** 1.26s
