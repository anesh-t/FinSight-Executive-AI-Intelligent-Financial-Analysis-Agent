# 📊 DATA SOURCE MAPPING FOR VISUALIZATION

**Critical Understanding:** When user asks "Apple revenue 2023", the agent queries a specific view/table. **THE SAME VIEW ALREADY HAS DATA FOR ALL YEARS AND ALL COMPANIES!** We just need to remove filters to get more data for charts.

---

## 🔍 COMPLETE DATA FLOW MAPPING

### **Example: "Apple revenue 2023"**

#### **Current Flow (Returns Single Point):**
```
1. User: "Apple revenue 2023"
2. Decomposer extracts: ticker=AAPL, fy=2023
3. Router selects: "annual_metrics" template
4. SQL Builder uses template SQL with parameters
5. Query executed:
   SELECT ... revenue_annual/1e9 as revenue_b
   FROM mv_financials_annual mv
   JOIN dim_company c USING (company_id)
   WHERE c.ticker = 'AAPL'           ← Filter to Apple only
     AND mv.fiscal_year = 2023       ← Filter to 2023 only
   LIMIT 1                            ← Only 1 row
   
6. Result: {revenue_b: 385.71, fiscal_year: 2023}
7. Formatter: "Apple reported revenue of $385.71B for FY2023"
```

#### **For Visualization (Need 5-Year Trend):**
```
Same source (mv_financials_annual) but modify filters:

SELECT fiscal_year, revenue_annual/1e9 as revenue_b
FROM mv_financials_annual mv
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL'               ← Keep company filter
  AND fiscal_year >= 2019              ← Get 5 years: 2019-2023
ORDER BY fiscal_year ASC               ← Chronological order
-- NO LIMIT!                           ← Get all 5 years

Result: [
  {fiscal_year: 2019, revenue_b: 260.17},
  {fiscal_year: 2020, revenue_b: 274.52},
  {fiscal_year: 2021, revenue_b: 365.82},
  {fiscal_year: 2022, revenue_b: 394.33},
  {fiscal_year: 2023, revenue_b: 385.71}
]
```

---

## 📋 TEMPLATE → VIEW → VISUALIZATION MAPPING

### **1. ANNUAL METRICS QUERIES**

**Template:** `annual_metrics`  
**Example Query:** "Apple revenue 2023", "Microsoft net income 2023"

| Component | Value |
|-----------|-------|
| **Intent** | `annual_metrics` |
| **Primary View** | `mv_financials_annual` |
| **Join Tables** | `mv_ratios_annual`, `dim_company`, `fact_financials` |
| **Current Query** | WHERE ticker=:ticker AND fiscal_year=:fy LIMIT 1 |
| **For Viz (5Y Trend)** | WHERE ticker=:ticker AND fiscal_year >= (:fy-4) |

**Visualization SQL:**
```sql
-- Get 5-year trend for charts
SELECT 
    fiscal_year,
    revenue_annual/1e9 as revenue_b,
    net_income_annual/1e9 as net_income_b,
    gross_margin_annual*100 as gross_margin_pct,
    operating_margin_annual*100 as operating_margin_pct,
    net_margin_annual*100 as net_margin_pct,
    roe_annual*100 as roe_pct,
    roa_annual*100 as roa_pct
FROM mv_financials_annual mv
JOIN mv_ratios_annual r USING (company_id, fiscal_year)
JOIN dim_company c USING (company_id)
WHERE c.ticker = :ticker
  AND mv.fiscal_year BETWEEN :start_year AND :end_year
ORDER BY fiscal_year ASC
```

**Available Metrics in View:**
- ✅ All financial metrics (revenue, income, expenses)
- ✅ All ratios (margins, ROE, ROA, debt ratios)
- ✅ Cash flows
- ✅ Balance sheet items

---

### **2. QUARTERLY METRICS QUERIES**

**Template:** `quarter_snapshot`  
**Example Query:** "Apple revenue Q2 2023", "Microsoft net margin Q2 2023"

| Component | Value |
|-----------|-------|
| **Intent** | `quarter_snapshot` |
| **Primary View** | `fact_financials` |
| **Join Tables** | `vw_ratios_quarter`, `dim_company` |
| **Current Query** | WHERE ticker=:ticker AND fiscal_year=:fy AND fiscal_quarter=:fq LIMIT 1 |
| **For Viz (8Q Trend)** | WHERE ticker=:ticker ORDER BY fy DESC, fq DESC LIMIT 8 |

**Visualization SQL:**
```sql
-- Get 8-quarter trend for charts
SELECT 
    f.fiscal_year,
    f.fiscal_quarter,
    f.revenue/1e9 as revenue_b,
    f.net_income/1e9 as net_income_b,
    f.operating_income/1e9 as op_income_b,
    r.gross_margin*100 as gross_margin_pct,
    r.operating_margin*100 as operating_margin_pct,
    r.net_margin*100 as net_margin_pct,
    r.roe*100 as roe_pct,
    r.roa*100 as roa_pct
FROM fact_financials f
JOIN dim_company c USING (company_id)
LEFT JOIN vw_ratios_quarter r 
    ON r.company_id = f.company_id 
    AND r.fiscal_year = f.fiscal_year 
    AND r.fiscal_quarter = f.fiscal_quarter
WHERE c.ticker = :ticker
  AND f.fiscal_quarter IS NOT NULL
ORDER BY f.fiscal_year DESC, f.fiscal_quarter DESC
LIMIT 8
```

---

### **3. STOCK PRICE QUERIES - QUARTERLY**

**Template:** `stock_price_quarterly`  
**Example Query:** "Apple opening stock price Q2 2023"

| Component | Value |
|-----------|-------|
| **Intent** | `stock_price_quarterly` |
| **Primary View** | `vw_stock_prices_quarter` |
| **Join Tables** | `dim_company` |
| **Current Query** | WHERE ticker=:ticker AND fiscal_year=:fy AND fiscal_quarter=:fq LIMIT 1 |
| **For Viz (8Q Candlestick)** | WHERE ticker=:ticker ORDER BY fy DESC, fq DESC LIMIT 8 |

**Visualization SQL:**
```sql
-- Get 8-quarter stock data for OHLC/Candlestick chart
SELECT 
    sq.fiscal_year,
    sq.fiscal_quarter,
    sq.open_price,
    sq.close_price,
    sq.high_price,
    sq.low_price,
    sq.avg_price,
    sq.return_qoq*100 as return_qoq_pct,
    sq.return_yoy*100 as return_yoy_pct,
    sq.volatility_pct,
    sq.volume_total
FROM vw_stock_prices_quarter sq
JOIN dim_company c USING (company_id)
WHERE c.ticker = :ticker
ORDER BY sq.fiscal_year DESC, sq.fiscal_quarter DESC
LIMIT 8
```

---

### **4. STOCK PRICE QUERIES - ANNUAL**

**Template:** `stock_price_annual`  
**Example Query:** "Apple closing stock price 2023"

| Component | Value |
|-----------|-------|
| **Intent** | `stock_price_annual` |
| **Primary View** | `mv_stock_prices_annual` |
| **Join Tables** | `dim_company` |
| **Current Query** | WHERE ticker=:ticker AND fiscal_year=:fy LIMIT 1 |
| **For Viz (5Y Trend)** | WHERE ticker=:ticker AND fiscal_year >= (:fy-4) |

**Visualization SQL:**
```sql
-- Get 5-year stock trend
SELECT 
    sa.fiscal_year,
    sa.avg_open_price_annual,
    sa.avg_close_price_annual,
    sa.close_price_eoy,
    sa.high_price_annual,
    sa.low_price_annual,
    sa.avg_price_annual,
    sa.return_annual*100 as return_annual_pct,
    sa.volatility_pct_annual
FROM mv_stock_prices_annual sa
JOIN dim_company c USING (company_id)
WHERE c.ticker = :ticker
  AND sa.fiscal_year BETWEEN :start_year AND :end_year
ORDER BY sa.fiscal_year ASC
```

---

### **5. COMBINED QUERIES (Financials + Stock)**

**Template:** `complete_annual` or `complete_quarterly`  
**Example Query:** "Show Apple revenue, net margin, and closing stock price for 2023"

| Component | Value |
|-----------|-------|
| **Intent** | `complete_annual` / `complete_quarterly` |
| **Primary View** | `mv_company_complete_annual` / `vw_company_complete_quarter` |
| **Contains** | ALL data: financials + ratios + stock prices |
| **For Viz** | Same view, just remove LIMIT and year filter |

**Visualization SQL (Annual):**
```sql
-- PERFECT! This view has EVERYTHING we need
SELECT 
    fiscal_year,
    -- Financials
    revenue_annual/1e9 as revenue_b,
    net_income_annual/1e9 as net_income_b,
    operating_income_annual/1e9 as op_income_b,
    -- Ratios
    gross_margin_annual*100 as gross_margin_pct,
    operating_margin_annual*100 as operating_margin_pct,
    net_margin_annual*100 as net_margin_pct,
    roe_annual*100 as roe_pct,
    -- Stock
    close_price_eoy as stock_price,
    avg_price_annual,
    return_annual*100 as return_pct
FROM mv_company_complete_annual
WHERE ticker = :ticker
  AND fiscal_year BETWEEN :start_year AND :end_year
ORDER BY fiscal_year ASC
```

**Visualization SQL (Quarterly):**
```sql
-- For quarterly combined queries
SELECT 
    fiscal_year,
    fiscal_quarter,
    -- Financials
    revenue/1e9 as revenue_b,
    net_income/1e9 as net_income_b,
    -- Ratios
    gross_margin*100 as gross_margin_pct,
    net_margin*100 as net_margin_pct,
    -- Stock
    open_price,
    close_price,
    high_price,
    low_price,
    avg_price
FROM vw_company_complete_quarter
WHERE ticker = :ticker
ORDER BY fiscal_year DESC, fiscal_quarter DESC
LIMIT 8
```

---

### **6. MULTI-COMPANY COMPARISON**

**Example Query:** "Compare Apple and Google revenue Q2 2023"

**Current Approach:** Agent executes separate queries for each company, then combines

**For Visualization:**
```sql
-- Get multi-company comparison data
-- Annual
SELECT 
    c.ticker,
    c.name,
    mv.fiscal_year,
    mv.revenue_annual/1e9 as revenue_b,
    r.net_margin_annual*100 as net_margin_pct,
    r.roe_annual*100 as roe_pct
FROM mv_financials_annual mv
JOIN mv_ratios_annual r USING (company_id, fiscal_year)
JOIN dim_company c USING (company_id)
WHERE c.ticker IN (:ticker1, :ticker2, :ticker3, ...)
  AND mv.fiscal_year BETWEEN :start_year AND :end_year
ORDER BY c.ticker, mv.fiscal_year ASC

-- Quarterly
SELECT 
    c.ticker,
    c.name,
    f.fiscal_year,
    f.fiscal_quarter,
    f.revenue/1e9 as revenue_b,
    r.net_margin*100 as net_margin_pct
FROM fact_financials f
JOIN vw_ratios_quarter r 
    ON f.company_id = r.company_id 
    AND f.fiscal_year = r.fiscal_year 
    AND f.fiscal_quarter = r.fiscal_quarter
JOIN dim_company c USING (company_id)
WHERE c.ticker IN (:ticker1, :ticker2)
  AND f.fiscal_year = :fy
  AND f.fiscal_quarter = :fq
ORDER BY c.ticker
```

---

### **7. MACRO INDICATORS**

**Template:** `macro_indicator_quarterly` / `macro_indicator_annual`  
**Example Query:** "Unemployment rate in 2023"

| Component | Value |
|-----------|-------|
| **Intent** | `macro_indicator_annual` |
| **Primary View** | `mv_macro_annual` / `vw_macro_quarter` |
| **For Viz** | Get 5-10 years of macro trend |

**Visualization SQL:**
```sql
-- Get macro indicator trend
SELECT 
    fiscal_year,
    gdp_annual/1e3 as gdp_t,
    cpi_annual,
    unemployment_rate_annual,
    fed_funds_rate_annual,
    sp500_index_annual
FROM mv_macro_annual
WHERE fiscal_year BETWEEN :start_year AND :end_year
ORDER BY fiscal_year ASC
```

---

## 🎯 KEY INSIGHTS FOR IMPLEMENTATION

### **1. Views Are Already Perfect!**
```
✅ mv_company_complete_annual - Has EVERYTHING for annual queries
✅ vw_company_complete_quarter - Has EVERYTHING for quarterly queries
✅ Both include: financials + ratios + stock prices
✅ No need to join multiple tables for viz!
```

### **2. Simple Modification Pattern:**
```python
# Current query (returns 1 row)
WHERE ticker = :ticker AND fiscal_year = :fy LIMIT 1

# For visualization (returns 5 rows)
WHERE ticker = :ticker 
  AND fiscal_year BETWEEN :fy-4 AND :fy
ORDER BY fiscal_year ASC
# NO LIMIT!
```

### **3. Parameter Extraction:**
```python
def get_viz_params(original_params, intent):
    """Extract parameters from original query"""
    ticker = original_params.get('ticker')
    fy = original_params.get('fy')
    fq = original_params.get('fq')
    
    if 'annual' in intent:
        return {
            'ticker': ticker,
            'start_year': fy - 4 if fy else 2019,
            'end_year': fy if fy else 2023
        }
    elif 'quarter' in intent:
        return {
            'ticker': ticker,
            'limit': 8  # Last 8 quarters
        }
```

---

## 📊 VISUALIZATION DATA REQUIREMENTS SUMMARY

| Query Type | Source View | Data Needed | SQL Modification |
|------------|-------------|-------------|------------------|
| Annual Financial | `mv_financials_annual` | 5 years | Remove year filter, add range |
| Annual Ratios | `mv_ratios_annual` | 5 years | Same as above |
| Annual Stock | `mv_stock_prices_annual` | 5 years | Same as above |
| Annual Combined | `mv_company_complete_annual` | 5 years | **BEST - has everything!** |
| Quarterly Financial | `fact_financials` | 8 quarters | Change LIMIT to 8, remove year filter |
| Quarterly Ratios | `vw_ratios_quarter` | 8 quarters | Same as above |
| Quarterly Stock | `vw_stock_prices_quarter` | 8 quarters | Same as above |
| Quarterly Combined | `vw_company_complete_quarter` | 8 quarters | **BEST - has everything!** |
| Multi-Company | Same as single | Per company | Add ticker IN (...) |
| Macro Indicators | `mv_macro_annual` | 5-10 years | Remove year filter |

---

## ✅ IMPLEMENTATION STRATEGY

### **Step 1: Identify Data Source from Template**
```python
# When user asks "Apple revenue 2023"
# Agent uses template: "annual_metrics"
# Template uses view: "mv_financials_annual"
# For viz: USE THE SAME VIEW!
```

### **Step 2: Modify Query for Historical Data**
```python
# Instead of:
WHERE ticker = 'AAPL' AND fiscal_year = 2023 LIMIT 1

# Use:
WHERE ticker = 'AAPL' AND fiscal_year >= 2019
ORDER BY fiscal_year ASC
```

### **Step 3: Return Same Structure + Historical Data**
```python
{
    "current": {fiscal_year: 2023, revenue_b: 385.71},
    "historical": [
        {fiscal_year: 2019, revenue_b: 260.17},
        {fiscal_year: 2020, revenue_b: 274.52},
        {fiscal_year: 2021, revenue_b: 365.82},
        {fiscal_year: 2022, revenue_b: 394.33},
        {fiscal_year: 2023, revenue_b: 385.71}
    ]
}
```

---

## 🚀 READY TO IMPLEMENT

**With this mapping, I can now:**
1. ✅ Know exactly which view to query for each intent
2. ✅ Reuse existing views (no new queries needed!)
3. ✅ Simply modify WHERE clause and LIMIT
4. ✅ Get all necessary data for charts from same source

**Next: Build VizDataFetcher that maps intent → view → modified SQL!**
