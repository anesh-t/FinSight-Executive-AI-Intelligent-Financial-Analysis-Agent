# COMPLETE VISUALIZATION MAPPING ANALYSIS

**Based on:** Complete verification output (93 queries tested)  
**Data Available:** 2019-2025 (Quarterly), 2019-2023 (Annual complete)

---

## 📊 DATA STRUCTURE UNDERSTANDING

### **What We Have:**

#### **QUARTERLY DATA** (fact_financials + views)
```
Time Range: Q1 2019 - Q2 2025
Granularity: Quarterly
Companies: 5 (AAPL, MSFT, GOOG, AMZN, META)

Available Fields:
├── Financials: revenue, net_income, operating_income, gross_profit,
│               r_and_d_expenses, sg_and_a_expenses, cogs,
│               cash_flow_ops, cash_flow_investing, cash_flow_financing,
│               capex, dividends, buybacks, eps
├── Ratios: gross_margin, operating_margin, net_margin,
│           roe, roa, debt_to_equity, debt_to_assets,
│           rd_intensity, sga_intensity
├── Stock: open_price, close_price, high_price, low_price, avg_price,
│          return_qoq, return_yoy, volatility_pct, dividend_yield
└── Macro: gdp, cpi, unemployment_rate, fed_funds_rate, sp500_index, vix
```

#### **ANNUAL DATA** (materialized views)
```
Time Range: 2019-2023 (complete), 2024-2025 (partial)
Granularity: Annual
Companies: 5

Available Fields:
├── Financials: revenue_annual, net_income_annual, operating_income_annual,
│               gross_profit_annual, r_and_d_expenses_annual,
│               cash flows, capex_annual
├── Ratios: gross_margin_annual, operating_margin_annual, net_margin_annual,
│           roe_annual, roa_annual, debt_to_equity_annual
├── Stock: avg_open_price_annual, avg_close_price_annual, close_price_eoy,
│          high_price_annual, low_price_annual, return_annual,
│          volatility_pct_annual
└── Macro: gdp_annual, cpi_annual, unemployment_rate_annual, etc.
```

---

## 🎨 VISUALIZATION MAPPING BY QUERY TYPE

### **CATEGORY 1: BASIC FINANCIALS - QUARTERLY** (10 queries, 100% pass)

#### **Sample Queries:**
```
✅ "Apple revenue Q2 2023"
✅ "Microsoft net income Q3 2023"
✅ "Google operating income Q2 2023"
✅ "Amazon gross profit Q2 2023"
```

#### **Current Output:**
```
Apple Inc. (AAPL) reported revenue of $81.80B for Q2 FY2023.
```

#### **VISUALIZATION STRATEGY:**

**Chart Type:** LINE CHART (8-Quarter Trend)

**Data Needed:**
```sql
SELECT fiscal_year, fiscal_quarter, revenue/1e9 as revenue_b
FROM fact_financials
WHERE company_id = (SELECT company_id FROM dim_company WHERE ticker = 'AAPL')
ORDER BY fiscal_year DESC, fiscal_quarter DESC
LIMIT 8
```

**Expected Output:**
```
┌─────────────────────────────────────────────────────┐
│ Apple Revenue Trend (Last 8 Quarters)               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  100B ┤                               ●             │
│       │                           ●       ●         │
│   80B ┤                       ●               ●     │
│       │                   ●                     ●   │
│   60B ┤               ●                             │
│       │           ●                                 │
│   40B ┤       ●                                     │
│       │   ●                                         │
│   20B ┤●                                            │
│       └─────────────────────────────────────────    │
│        Q1  Q2  Q3  Q4  Q1  Q2  Q3  Q4              │
│        2022         2023                            │
└─────────────────────────────────────────────────────┘

Current: $81.80B | Previous: $78.50B | Change: +4.2%
```

**Why This Works:**
- Shows context (trend) not just single point
- User can see if $81.80B is growth or decline
- Professional financial presentation

---

### **CATEGORY 2: BASIC FINANCIALS - ANNUAL** (7 queries, 100% pass)

#### **Sample Queries:**
```
✅ "Apple revenue 2023"
✅ "Microsoft net income 2023"
✅ "Google operating income 2023"
```

#### **VISUALIZATION STRATEGY:**

**Chart Type:** LINE CHART (5-Year Trend)

**Data Needed:**
```sql
SELECT fiscal_year, revenue_annual/1e9 as revenue_b
FROM mv_financials_annual
WHERE company_id = (SELECT company_id FROM dim_company WHERE ticker = 'AAPL')
  AND fiscal_year >= 2019
ORDER BY fiscal_year ASC
```

**Expected Output:**
```
Apple Revenue Trend (2019-2023)

400B ┤                           ●
     │                       ●   
300B ┤                   ●       
     │               ●           
200B ┤           ●               
     │       ●                   
100B ┤   ●                       
     └───────────────────────────
      2019 2020 2021 2022 2023

5-Year CAGR: 10.3% | 2023: $385.71B
```

---

### **CATEGORY 3: FINANCIAL RATIOS - QUARTERLY** (8 queries, 100% pass)

#### **Sample Queries:**
```
✅ "Apple gross margin Q2 2023"
✅ "Microsoft net margin Q2 2023"
✅ "Google ROE Q2 2023"
```

#### **VISUALIZATION STRATEGY:**

**Chart Type:** LINE CHART with TARGET BAND

**Why:** Margins should be compared to historical range

**Data Needed:**
```sql
SELECT fiscal_year, fiscal_quarter, 
       gross_margin*100 as gross_margin_pct,
       AVG(gross_margin*100) OVER (ORDER BY fiscal_year, fiscal_quarter 
                                    ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) as rolling_avg
FROM vw_ratios_quarter
WHERE company_id = (SELECT company_id FROM dim_company WHERE ticker = 'AAPL')
ORDER BY fiscal_year DESC, fiscal_quarter DESC
LIMIT 8
```

**Expected Output:**
```
Apple Gross Margin Trend (Last 8 Quarters)

50% ┤ ━━━━━━━━━━━━━━━━━━━━━━━ Industry Avg (47%)
    │           ●───●───●───●
45% ┤       ●───●   │   │   │
    │   ●───●       │   │   │ Current: 44.5%
40% ┤───●           │   │   │ 8Q Avg: 44.8%
    │               │   │   │ Status: Stable ✓
35% ┤───────────────────────────
     Q1  Q2  Q3  Q4  Q1  Q2  Q3  Q4
     2022         2023
```

---

### **CATEGORY 4: STOCK PRICES - QUARTERLY** (11 queries, 100% pass!)

#### **Sample Queries:**
```
✅ "Apple opening stock price Q2 2023"
✅ "Apple closing stock price Q2 2023"
✅ "Apple high stock price Q2 2023"
✅ "Microsoft opening and closing price Q2 2023"
```

#### **VISUALIZATION STRATEGY:**

**Chart Type:** CANDLESTICK CHART or OHLC

**Data Needed:**
```sql
SELECT fiscal_year, fiscal_quarter,
       open_price, close_price, high_price, low_price
FROM vw_stock_prices_quarter
WHERE company_id = (SELECT company_id FROM dim_company WHERE ticker = 'AAPL')
ORDER BY fiscal_year DESC, fiscal_quarter DESC
LIMIT 8
```

**Expected Output:**
```
Apple Stock Price (Last 8 Quarters)

$200 ┤           ┃
     │           ┃     ╻
$180 ┤     ╻     ┃     ┃
     │     ┃     ┃     ┃
$160 ┤     ┃     ┃     ╹
     │     ┃     ╹
$140 ┤     ╹
     │ ╻
$120 ┤ ┃
     └──────────────────────
      Q1  Q2  Q3  Q4  Q1  Q2
      2022         2023

Q2 2023: Open $126.89 | Close $192.32 | High $194.76 | Low $124.76
Quarterly Return: +51.6% 🔥
```

**Alternative:** Simple line with HIGH/LOW band
```
$200 ┤               ●━━● High Range
     │           ●━━━│  │
$180 ┤       ●━━━│   │  │━━● Target Price
     │   ●━━━│   │   │  │
$160 ┤━━━│   │   │   │━━●
     └────────────────────────
```

---

### **CATEGORY 5: COMBINED QUERIES** (11 queries, 100% pass!)

#### **Sample Queries:**
```
✅ "Show Apple revenue and closing stock price for 2023"
✅ "Show Microsoft revenue, net margin, and closing price 2023"
✅ "Apple net income and opening price Q3 2023"
```

#### **Current Output:**
```
Microsoft Corporation (MSFT) reported revenue of $227.58B, 
net margin of 36.3%, closing price of $376.04 for FY2023.
```

#### **VISUALIZATION STRATEGY:**

**Chart Type:** DUAL-AXIS CHART

**Why:** Show relationship between financials and stock price

**Data Needed:**
```sql
-- Annual
SELECT fiscal_year,
       revenue_annual/1e9 as revenue_b,
       net_margin_annual*100 as net_margin_pct,
       close_price_eoy as stock_price
FROM mv_company_complete_annual
WHERE ticker = 'MSFT'
  AND fiscal_year >= 2019
ORDER BY fiscal_year ASC

-- Quarterly
SELECT fiscal_year, fiscal_quarter,
       revenue/1e9 as revenue_b,
       net_margin*100 as net_margin_pct,
       close_price
FROM vw_company_complete_quarter
WHERE ticker = 'MSFT'
ORDER BY fiscal_year DESC, fiscal_quarter DESC
LIMIT 8
```

**Expected Output:**
```
Microsoft: Revenue, Margin & Stock (2019-2023)

Revenue ($B)              Stock Price ($)
$250B ┤           ●       $400
      │       ●   │       
$200B ┤   ●   │   │       $300
      │   │   │   │   ●━━━Stock
$150B ┤   ●━━━●━━━●       $200
      │   Revenue         
$100B ┤                   $100
      └────────────────────────
       2019 2020 2021 2022 2023

Correlation: 0.85 (Strong Positive)
As revenue grew 47%, stock price increased 82%
```

---

### **CATEGORY 6: MULTI-COMPANY COMPARISON** (6 queries, 100% pass)

#### **Sample Queries:**
```
✅ "Compare Apple and Google revenue Q2 2023"
✅ "Show Apple and Microsoft net margin 2023"
```

#### **Current Output:**
```
Here is the revenue for Q2 2023:
- **Apple Inc.**: $81.80B revenue
- **Alphabet Inc.**: $74.60B revenue
```

#### **VISUALIZATION STRATEGY:**

**Chart Type:** GROUPED BAR CHART

**Data Needed:**
```sql
SELECT c.ticker, c.name, f.fiscal_year, f.fiscal_quarter,
       f.revenue/1e9 as revenue_b
FROM fact_financials f
JOIN dim_company c USING (company_id)
WHERE c.ticker IN ('AAPL', 'GOOG')
  AND f.fiscal_year = 2023
  AND f.fiscal_quarter = 2
```

**Expected Output:**
```
Revenue Comparison (Q2 2023)

$100B ┤
      │ ████████
$ 80B ┤ ██ AAPL █   $81.80B
      │ ████████
$ 60B ┤ ████████   ████████
      │ ████████   ██ GOOG█   $74.60B
$ 40B ┤ ████████   ████████
      │ ████████   ████████
$ 20B ┤ ████████   ████████
      └───────────────────────
        Apple      Google

Gap: $7.2B (9.6%) | Leader: Apple 👑
```

**For Time Comparison:**
```
Revenue Trend: Apple vs Google (2019-2023)

$400B ┤                 ●━━━ Apple
      │             ●━━━│
$300B ┤         ●━━━│   │
      │     ●━━━│   │   ●━━━ Google
$200B ┤ ●━━━│   │   ●━━━│
      │     │   ●━━━│   │
$100B ┤     ●━━━│   │   │
      └─────────────────────
       2019 2020 2021 2022 2023
```

---

### **CATEGORY 7: MACRO INDICATORS** (5 queries, 40% pass)

#### **Sample Queries:**
```
✅ "Unemployment rate in 2023"
✅ "GDP in 2023"
⚠️ "CPI in 2023" (formatting issue)
```

#### **VISUALIZATION STRATEGY:**

**Chart Type:** LINE with EVENTS/ANNOTATIONS

**Data Needed:**
```sql
SELECT fiscal_year, unemployment_rate_annual
FROM mv_macro_annual
WHERE fiscal_year >= 2019
ORDER BY fiscal_year ASC
```

**Expected Output:**
```
US Unemployment Rate (2019-2023)

15% ┤     ●
    │     │   COVID Peak
12% ┤     │
    │     ●
 9% ┤     │
    │ ●───●───●
 6% ┤ │       │
    │ │       ●───●
 3% ┤ │           │  
    │ │           ●  Current: 3.63%
 0% ┤─────────────────
     2019 2020 2021 2022 2023

5-Year Change: -1.2pp | Status: Healthy ✓
```

---

### **CATEGORY 8: GROWTH METRICS** (3 queries, 100% pass)

#### **Sample Queries:**
```
✅ "Apple revenue growth Q2 2023"
✅ "Microsoft YoY growth Q2 2023"
✅ "Google 3-year CAGR 2023"
```

#### **VISUALIZATION STRATEGY:**

**Chart Type:** WATERFALL CHART or BAR with GROWTH %

**Data Needed:**
```sql
SELECT fiscal_year,
       revenue_annual/1e9 as revenue_b,
       LAG(revenue_annual/1e9) OVER (ORDER BY fiscal_year) as prev_revenue,
       (revenue_annual/NULLIF(LAG(revenue_annual) OVER (ORDER BY fiscal_year), 0) - 1) * 100 as growth_pct
FROM mv_financials_annual
WHERE company_id = (SELECT company_id FROM dim_company WHERE ticker = 'AAPL')
  AND fiscal_year >= 2019
ORDER BY fiscal_year ASC
```

**Expected Output:**
```
Apple Revenue Growth (YoY % Change)

+15% ┤       ████
     │       ████  +11.4%
+10% ┤   ████████
     │   ████████  +5.9%
 +5% ┤   ████████
     │ ████████████
  0% ┼─────────────────────────
     │             ████
 -5% ┤             ████  -2.2%
     └─────────────────────────
      2020 2021 2022 2023

3-Year CAGR: +10.3%
Total Growth: +48.2% ($260B → $386B)
```

---

### **CATEGORY 9: COMPLETE ANALYSIS** (3 queries, 100% pass)

#### **Sample Queries:**
```
✅ "Show Apple complete picture Q2 2023"
✅ "Show Microsoft full analysis 2023"
✅ "Everything about Google Q2 2023"
```

#### **Current Output:**
```
Microsoft Corporation (MSFT) reported revenue of $227.58B, net income of $82.54B, 
operating income of $100.53B, gross profit of $158.74B, R&D expenses of $27.52B, 
SG&A expenses of $7.29B, COGS of $68.85B, gross margin of 69.7%, operating margin 
of 44.2%, net margin of 36.3%, ROE of 38.4%, ROA of 19.3%, debt-to-equity ratio 
of 0.97, debt-to-assets ratio of 0.49, R&D intensity of 12.1%, SG&A intensity of 
3.2%, total assets of $470.56B, total liabilities of $232.29B, equity of $238.27B, 
operating cash flow of $102.65B, investing cash flow of $-97.37B, financing cash 
flow of $-17.09B, capex of $35.20B, dividends of $20.74B, buybacks of $0.00B, 
EPS of $11.06 for FY2023.
```

#### **VISUALIZATION STRATEGY:**

**Chart Type:** MINI DASHBOARD (Multiple Charts)

1. **Revenue & Profitability Waterfall**
2. **Margin Trend (3 types)**
3. **Cash Flow Sankey Diagram**
4. **Key Metrics Cards**

**Data Needed:** Full annual/quarterly record + 5-year trend

**Expected Output:**
```
┌─────────────────────────────────────────────────────────────┐
│ MICROSOFT CORPORATION (MSFT) - FY2023 COMPLETE ANALYSIS     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📊 REVENUE BREAKDOWN (Waterfall)                            │
│ Revenue      Operating      Net                            │
│ $227.6B  ▸   Income     ▸   Income                         │
│              $100.5B        $82.5B                          │
│ │████████│   │████│         │███│                           │
│ └────┬───┘   └─┬──┘         └─┬─┘                          │
│      │         │              │                             │
│   -$127.1B  -$18.0B                                        │
│    COGS+    Taxes                                          │
│   OpEx                                                      │
│                                                             │
│ 📈 MARGIN TRENDS (5-Year)                                   │
│ 75% ┤ ●━━●━━●━━●━━● Gross (69.7%)                          │
│ 50% ┤ ●━━●━━●━━●━━● Operating (44.2%)                      │
│ 25% ┤ ●━━●━━●━━●━━● Net (36.3%)                            │
│     └───────────────────                                    │
│     2019 2020 2021 2022 2023                                │
│                                                             │
│ 💰 CASH FLOW (FY2023)                                       │
│ Operating: $102.7B ▸ Investing: -$97.4B ▸ Free Cash: $67.5B│
│                                                             │
│ 🎯 KEY METRICS                                              │
│ ROE: 38.4% | ROA: 19.3% | D/E: 0.97 | R&D: 12.1%           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 VISUALIZATION SUMMARY TABLE

| Query Category | Query Count | Best Chart Type | Data Points Needed | Priority |
|----------------|-------------|-----------------|-------------------|----------|
| Basic Financials (Q) | 10 | Line (8Q trend) | 8 quarters | HIGH |
| Basic Financials (A) | 7 | Line (5Y trend) | 5 years | HIGH |
| Ratios (Q) | 8 | Line + Band | 8Q + avg | HIGH |
| Ratios (A) | 6 | Line + Band | 5Y + avg | MEDIUM |
| Stock (Q) | 11 | Candlestick/OHLC | 8 quarters | HIGH |
| Stock (A) | 9 | Line + Band | 5 years | MEDIUM |
| Combined (A/Q) | 11 | Dual-Axis | 5Y or 8Q | HIGH |
| Multi-Company | 6 | Grouped Bar + Line | Per company | HIGH |
| Macro Indicators | 5 | Line + Events | 5-10 years | MEDIUM |
| Growth Metrics | 3 | Waterfall/Bar | 5 years | MEDIUM |
| Complete Analysis | 3 | Dashboard | Full data | LOW |

---

## 🎯 IMPLEMENTATION PRIORITY

### **PHASE 1: HIGH PRIORITY** (70% of queries)
1. **Single metric time series** (Financials, Ratios)
   - Line charts with 5Y/8Q trends
   - Simple, fast, high value
   
2. **Stock price visualizations**
   - OHLC/Candlestick for quarterly
   - Line with bands for annual
   
3. **Combined queries**
   - Dual-axis charts
   - Most requested by users

4. **Multi-company comparisons**
   - Grouped bars
   - Side-by-side trends

### **PHASE 2: MEDIUM PRIORITY** (25% of queries)
1. Growth analysis charts
2. Macro indicator trends
3. Ratio analysis with benchmarks

### **PHASE 3: LOW PRIORITY** (5% of queries)
1. Complete analysis dashboards
2. Advanced correlation plots

---

## 🔧 TECHNICAL REQUIREMENTS

### **Data Fetching Strategy:**

```python
def get_viz_data(query_result, intent, params):
    """
    Fetch extended data for visualization based on intent
    """
    ticker = params.get('ticker')
    fy = params.get('fy')
    fq = params.get('fq')
    
    if 'annual' in intent:
        # Get 5-year trend
        sql = f"""
        SELECT fiscal_year, 
               revenue_annual/1e9 as revenue_b,
               net_margin_annual*100 as margin_pct,
               close_price_eoy as stock_price
        FROM mv_company_complete_annual
        WHERE ticker = '{ticker}'
          AND fiscal_year BETWEEN {fy-4} AND {fy}
        ORDER BY fiscal_year ASC
        """
        return {"type": "line", "period": "annual", "data": execute(sql)}
    
    elif 'quarter' in intent:
        # Get 8-quarter trend
        sql = f"""
        SELECT fiscal_year, fiscal_quarter,
               revenue/1e9 as revenue_b,
               net_margin*100 as margin_pct,
               close_price
        FROM vw_company_complete_quarter
        WHERE ticker = '{ticker}'
        ORDER BY fiscal_year DESC, fiscal_quarter DESC
        LIMIT 8
        """
        return {"type": "line", "period": "quarterly", "data": execute(sql)}
```

### **Chart Library: Plotly**

```python
import plotly.graph_objects as go

def render_line_chart(data, title, y_label):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['x'],
        y=data['y'],
        mode='lines+markers',
        name=title,
        line=dict(color='#4a9eff', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Period",
        yaxis_title=y_label,
        template="plotly_dark",
        hovermode='x unified',
        height=400
    )
    
    return fig
```

---

## ✅ NEXT STEPS

1. **Implement hybrid visualization endpoint**
2. **Create chart rendering functions** (Plotly)
3. **Add "View Chart" button** in Streamlit
4. **Test with sample queries**
5. **Iterate based on user feedback**

**Ready to proceed with implementation?**
