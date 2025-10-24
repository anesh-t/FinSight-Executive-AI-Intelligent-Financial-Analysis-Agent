# 📈 Stock Prices & Macro Indicators - Implementation Plan

## 🎯 Objective
Extend CFO Agent to support:
1. **Stock Prices** (daily, quarterly avg, annual avg)
2. **Macro Economic Indicators** (quarterly, annual)

Currently working: 9 ratios + 19 financial metrics ✅  
Adding: Stock prices + Macro indicators 🚀

---

## 📋 PHASE 1: Database Schema Discovery

### What We Know So Far:

#### Existing Views (from whitelist.py):
```python
✅ vw_company_quarter_macro     # Company data + macro indicators (quarterly)
✅ vw_macro_sensitivity_rolling  # Macro sensitivity analysis
✅ vw_stock_citations            # Stock data citations
✅ vw_macro_citations            # Macro data citations
```

#### Tables to Investigate:
```
❓ fact_stock_prices           # Stock price data (user confirmed)
❓ Other macro indicator tables # User has multiple tables/views
```

### Action Items:
- [x] Create explore_stock_macro_schema.py
- [ ] Run exploration script to find:
  - fact_stock_prices schema
  - All macro indicator tables/views
  - Available indicators (GDP, CPI, unemployment, etc.)
  - Date ranges available
  - Data granularity

---

## 📊 PHASE 2: Define User Queries

### Stock Price Queries:

#### Daily Prices:
```
"show Apple stock price on 2023-10-15"
"what was Microsoft closing price yesterday"
"show Google stock price range for October 2023"
```

#### Quarterly Average:
```
"show Apple average stock price Q2 2023"
"what was Amazon stock price in Q3 2023"
"show Meta quarterly stock price 2023"
```

#### Annual Average:
```
"show Apple average stock price 2023"
"what was Microsoft stock price for 2023"
```

#### Metrics Available:
- Open price
- Close price
- High/Low
- Volume
- Market cap
- Returns (daily, quarterly, annual)

---

### Macro Indicator Queries:

#### Common Indicators:
```
GDP Growth:
  "show GDP growth Q2 2023"
  "what was GDP for 2023"

Inflation (CPI):
  "show inflation rate Q3 2023"
  "what was CPI in 2023"

Unemployment:
  "show unemployment rate 2023"
  "what was unemployment in Q2 2023"

Interest Rates:
  "show Fed funds rate Q4 2023"
  "what was 10-year treasury yield 2023"

Other:
  "show consumer confidence Q2 2023"
  "what was S&P 500 level in 2023"
```

#### Combined Queries:
```
"show Apple revenue and GDP Q2 2023"
"compare Microsoft revenue to S&P 500 2023"
"show Amazon performance with inflation 2023"
```

---

## 🗄️ PHASE 3: Create Database Views

### A. Stock Price Views

#### 1. `vw_stock_prices_daily` (if not exists)
```sql
-- Already have fact_stock_prices (user confirmed)
-- May just need to whitelist it
```

#### 2. `vw_stock_prices_quarterly` (NEW)
```sql
CREATE VIEW vw_stock_prices_quarterly AS
SELECT 
    company_id,
    fiscal_year,
    fiscal_quarter,
    AVG(close_price) as avg_close,
    MIN(low_price) as quarter_low,
    MAX(high_price) as quarter_high,
    SUM(volume) as total_volume,
    -- First and last prices for quarterly return
    FIRST_VALUE(open_price) OVER w as quarter_open,
    LAST_VALUE(close_price) OVER w as quarter_close,
    -- Calculate return
    (LAST_VALUE(close_price) OVER w - FIRST_VALUE(open_price) OVER w) / 
        FIRST_VALUE(open_price) OVER w as quarterly_return
FROM fact_stock_prices
WINDOW w AS (PARTITION BY company_id, fiscal_year, fiscal_quarter 
             ORDER BY date
             ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
GROUP BY company_id, fiscal_year, fiscal_quarter;
```

#### 3. `vw_stock_prices_annual` (NEW)
```sql
CREATE VIEW vw_stock_prices_annual AS
SELECT 
    company_id,
    fiscal_year,
    AVG(close_price) as avg_close,
    MIN(low_price) as year_low,
    MAX(high_price) as year_high,
    SUM(volume) as total_volume,
    -- Annual return
    (LAST_VALUE(close_price) OVER w - FIRST_VALUE(open_price) OVER w) / 
        FIRST_VALUE(open_price) OVER w as annual_return
FROM fact_stock_prices
WINDOW w AS (PARTITION BY company_id, fiscal_year 
             ORDER BY date
             ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
GROUP BY company_id, fiscal_year;
```

---

### B. Macro Indicator Views

**Need to explore first to see what exists!**

Likely structure:
```sql
-- Option 1: If there's a fact_macro_indicators table
vw_macro_indicators_quarterly (NEW)
vw_macro_indicators_annual (NEW)

-- Option 2: If already exists
Use existing: vw_company_quarter_macro (already whitelisted)
```

---

## 🔧 PHASE 4: Update Agent Components

### 1. Update Whitelist (`db/whitelist.py`)

```python
ALLOWED_SURFACES = {
    # ... existing surfaces ...
    
    # Stock Prices (ADD THESE)
    'fact_stock_prices',           # Daily stock prices
    'vw_stock_prices_quarterly',   # Quarterly aggregates
    'vw_stock_prices_annual',      # Annual aggregates
    
    # Macro Indicators (ADD IF NEEDED)
    'vw_macro_indicators_quarterly',  # Quarterly macro
    'vw_macro_indicators_annual',     # Annual macro
    # vw_company_quarter_macro already exists
}
```

---

### 2. Add SQL Templates (`catalog/templates.json`)

#### Stock Price Templates:

```json
{
  "stock_price_daily": {
    "surface": "fact_stock_prices",
    "description": "Daily stock prices",
    "sql": "SELECT c.ticker, c.name, s.date, s.open_price, s.close_price, s.high_price, s.low_price, s.volume FROM fact_stock_prices s JOIN dim_company c USING (company_id) WHERE c.ticker = :ticker AND s.date BETWEEN :start_date AND :end_date ORDER BY s.date LIMIT :limit"
  },
  
  "stock_price_quarterly": {
    "surface": "vw_stock_prices_quarterly",
    "description": "Quarterly average stock prices",
    "sql": "SELECT c.ticker, c.name, s.fiscal_year, s.fiscal_quarter, s.avg_close, s.quarter_low, s.quarter_high, s.quarterly_return FROM vw_stock_prices_quarterly s JOIN dim_company c USING (company_id) WHERE c.ticker = :ticker AND s.fiscal_year = :fy AND s.fiscal_quarter = :fq LIMIT :limit"
  },
  
  "stock_price_annual": {
    "surface": "vw_stock_prices_annual",
    "description": "Annual average stock prices",
    "sql": "SELECT c.ticker, c.name, s.fiscal_year, s.avg_close, s.year_low, s.year_high, s.annual_return FROM vw_stock_prices_annual s JOIN dim_company c USING (company_id) WHERE c.ticker = :ticker AND s.fiscal_year = :fy LIMIT :limit"
  }
}
```

#### Macro Indicator Templates:

```json
{
  "macro_indicator_quarterly": {
    "surface": "vw_macro_indicators_quarterly",
    "description": "Quarterly macro indicators",
    "sql": "SELECT indicator_code, indicator_name, fiscal_year, fiscal_quarter, value, unit FROM vw_macro_indicators_quarterly WHERE indicator_code = :indicator AND fiscal_year = :fy AND fiscal_quarter = :fq LIMIT :limit"
  },
  
  "macro_indicator_annual": {
    "surface": "vw_macro_indicators_annual",
    "description": "Annual macro indicators",
    "sql": "SELECT indicator_code, indicator_name, fiscal_year, AVG(value) as annual_avg, unit FROM vw_macro_indicators_annual WHERE indicator_code = :indicator AND fiscal_year = :fy LIMIT :limit"
  }
}
```

---

### 3. Update Router (`router.py`)

Add routing logic for stock and macro queries:

```python
def route_query(parsed_query):
    metric = parsed_query["metric"]
    period = parsed_query["period_type"]
    
    # Existing logic for financials and ratios
    # ...
    
    # NEW: Stock price routing
    if metric in ['stock_price', 'price', 'closing_price', 'stock']:
        if period == 'daily':
            return 'fact_stock_prices'
        elif period == 'quarterly':
            return 'vw_stock_prices_quarterly'
        elif period == 'annual':
            return 'vw_stock_prices_annual'
    
    # NEW: Macro indicator routing
    if metric in MACRO_INDICATORS:  # List of macro codes
        if period == 'quarterly':
            return 'vw_macro_indicators_quarterly'
        elif period == 'annual':
            return 'vw_macro_indicators_annual'
```

---

### 4. Update Formatter (`formatter.py`)

Add formatting for stock prices and macro indicators:

```python
# Stock price formatting
if 'close_price' in row:
    parts.append(f"closing price of ${row['close_price']:.2f}")

if 'avg_close' in row:
    parts.append(f"average price of ${row['avg_close']:.2f}")

if 'quarterly_return' in row:
    parts.append(f"quarterly return of {row['quarterly_return']*100:.1f}%")

# Macro indicator formatting
if 'indicator_name' in row and 'value' in row:
    unit = row.get('unit', '')
    if unit == '%':
        parts.append(f"{row['indicator_name']} of {row['value']:.2f}%")
    else:
        parts.append(f"{row['indicator_name']} of {row['value']:.2f} {unit}")
```

---

### 5. Update Decomposer (`decomposer.py`)

Add support for parsing stock and macro queries:

```python
# Add to metric extraction logic
if "stock price" in question or "closing price" in question:
    metric = "stock_price"

if any(macro in question for macro in ["GDP", "inflation", "CPI", "unemployment"]):
    metric = extract_macro_indicator(question)  # New function
```

---

## 🧪 PHASE 5: Testing

### Test Files to Create:

1. `test_stock_prices_daily.py` - Test daily stock queries
2. `test_stock_prices_quarterly.py` - Test quarterly averages
3. `test_stock_prices_annual.py` - Test annual averages
4. `test_macro_indicators.py` - Test macro queries
5. `test_combined_queries.py` - Test finance + stock + macro

---

## 📅 Implementation Order

1. ✅ **Create exploration script** (DONE)
2. ⏳ **Run exploration** to understand data structure
3. ⏳ **Create necessary views** (quarterly/annual aggregates)
4. ⏳ **Update whitelist** (add new surfaces)
5. ⏳ **Add templates** (stock & macro SQL templates)
6. ⏳ **Update router** (routing logic for stock/macro)
7. ⏳ **Update formatter** (display stock/macro data)
8. ⏳ **Update decomposer** (parse stock/macro questions)
9. ⏳ **Test thoroughly** (all query types)
10. ⏳ **Document** (update README with new capabilities)

---

## 🎯 Expected Outcome

After implementation, users can ask:

### Stock Price Queries:
- "show Apple stock price Q2 2023" → "Apple averaged $175.23 in Q2 FY2023"
- "what was Microsoft stock price 2023" → "Microsoft averaged $325.50 in FY2023"

### Macro Indicator Queries:
- "show GDP growth Q2 2023" → "GDP growth was 2.4% in Q2 2023"
- "what was inflation in 2023" → "CPI inflation averaged 4.1% in 2023"

### Combined Queries:
- "show Apple revenue and stock price Q2 2023" → Returns both metrics
- "compare Microsoft performance to GDP 2023" → Returns revenue + GDP

---

## 📊 Metrics Coverage After Implementation

| Category | Metrics | Status |
|----------|---------|--------|
| **Financial Ratios** | 9 ratios | ✅ Working (100%) |
| **Financial Metrics** | 19 metrics | ✅ Working |
| **Stock Prices** | 6 metrics | ⏳ To Implement |
| **Macro Indicators** | ~10-20 indicators | ⏳ To Implement |

**Total:** ~40-50 financial metrics accessible via natural language! 🚀

---

**NEXT STEP:** Run `python explore_stock_macro_schema.py` to see what data we have!
