# 🎯 CFO Agent - Complete Query Capabilities Reference

## Overview
Your CFO Agent can answer **200+ types of financial questions** across 5 companies (Apple, Microsoft, Google, Amazon, Meta) covering:
- **Time Periods:** Quarterly (Q1-Q4) and Annual (FY)
- **Data Categories:** Financials, Ratios, Stock Prices, Macro Indicators, Macro Sensitivity, Combined Views
- **Years Available:** 2017-2024

---

## 📊 **CATEGORY 1: FINANCIAL METRICS**

### **Quarterly Financial Queries**
**Surface:** `fact_financials` + `dim_company`

#### Revenue Queries
- "show Apple revenue Q2 2023"
- "what was Microsoft revenue in Q3 2023"
- "Apple Q2 2023 revenue"
- "latest quarter revenue for Google"

#### Income Queries
- "show Apple net income Q2 2023"
- "Microsoft operating income Q3 2023"
- "Google net income Q2 2023"
- "Amazon quarterly income Q3 2023"
- "what was Apple income Q2 2023" (defaults to net income)

#### Profit Queries
- "show Apple gross profit Q2 2023"
- "Microsoft gross profit Q3 2023"
- "operating income for Google Q2 2023"

#### Expense Queries (R&D, SG&A, COGS)
- "show Apple R&D expenses Q2 2023"
- "Microsoft SG&A expenses Q3 2023"
- "Google COGS Q2 2023"
- "Apple research and development Q2 2023"
- "Amazon selling general and administrative Q3 2023"

#### Cash Flow Queries
- "show Apple operating cash flow Q2 2023"
- "Microsoft cash flow from operations Q3 2023"
- "Google investing cash flow Q2 2023"
- "Amazon financing cash flow Q3 2023"
- "Apple capex Q2 2023"

#### Shareholder Distributions
- "show Apple dividends Q2 2023"
- "Microsoft buybacks Q3 2023"
- "Google share repurchases Q2 2023"

#### Balance Sheet Queries
- "show Apple total assets Q2 2023"
- "Microsoft total liabilities Q3 2023"
- "Google equity Q2 2023"

#### EPS Queries
- "show Apple EPS Q2 2023"
- "Microsoft earnings per share Q3 2023"

---

### **Annual Financial Queries**
**Surface:** `mv_financials_annual`

#### Revenue & Income (Annual)
- "show Apple revenue 2023"
- "Microsoft annual revenue 2023"
- "Google net income for fiscal year 2023"
- "Amazon total revenue 2023"
- "Meta full year revenue 2023"

#### Expenses (Annual)
- "show Apple R&D expenses 2023"
- "Microsoft annual SG&A 2023"
- "Google COGS for 2023"
- "Amazon total R&D spending 2023"

#### Cash Flow (Annual)
- "show Apple annual operating cash flow 2023"
- "Microsoft total capex 2023"
- "Google annual cash flow from operations 2023"

#### Annual Aggregates
- "show Apple 2023 financials"
- "Microsoft annual metrics 2023"
- "Google full year 2023"

---

## 📈 **CATEGORY 2: FINANCIAL RATIOS**

### **Quarterly Ratio Queries**
**Surface:** `vw_ratios_quarter`

#### Margin Ratios
- "show Apple gross margin Q2 2023"
- "Microsoft operating margin Q3 2023"
- "Google net margin Q2 2023"
- "Amazon profit margins Q3 2023"

#### Return Ratios
- "show Apple ROE Q2 2023"
- "Microsoft ROA Q3 2023"
- "Google return on equity Q2 2023"
- "Amazon return on assets Q3 2023"

#### Debt Ratios
- "show Apple debt to equity Q2 2023"
- "Microsoft debt to assets Q3 2023"
- "Google leverage ratio Q2 2023"
- "Amazon debt ratios Q3 2023"

#### Intensity Ratios
- "show Apple R&D intensity Q2 2023"
- "Microsoft SG&A intensity Q3 2023"
- "Google R&D to revenue Q2 2023"
- "Amazon SG&A ratio Q3 2023"

---

### **Annual Ratio Queries**
**Surface:** `mv_ratios_annual`

#### Annual Margins
- "show Apple gross margin 2023"
- "Microsoft operating margin 2023"
- "Google net margin 2023"

#### Annual Returns
- "show Apple ROE 2023"
- "Microsoft ROA 2023"
- "Google return on equity 2023"

#### Annual Debt Ratios
- "show Apple debt to equity 2023"
- "Microsoft debt to assets 2023"

#### Annual Intensity Ratios
- "show Apple R&D intensity 2023"
- "Microsoft SG&A intensity 2023"

---

## 📊 **CATEGORY 3: STOCK PRICES & RETURNS**

### **Quarterly Stock Queries**
**Surface:** `vw_stock_prices_quarter`

#### Stock Price Queries
- "show Apple stock price Q2 2023"
- "Microsoft average stock price Q3 2023"
- "Google stock price in Q2 2023"
- "what was Amazon stock price Q3 2023"

#### Return Queries
- "show Apple stock return Q2 2023"
- "Microsoft QoQ return Q3 2023"
- "Google YoY return Q2 2023"
- "Amazon quarterly stock performance Q3 2023"

#### Volatility Queries
- "show Apple volatility Q2 2023"
- "Microsoft stock volatility Q3 2023"
- "Google price volatility Q2 2023"

#### Dividend Yield Queries
- "show Apple dividend yield Q2 2023"
- "Microsoft dividend yield Q3 2023"

---

### **Annual Stock Queries**
**Surface:** `mv_stock_prices_annual`

#### Annual Stock Prices
- "show Apple stock price 2023"
- "Microsoft annual average stock price 2023"
- "Google stock price for 2023"

#### Annual Returns
- "show Apple annual return 2023"
- "Microsoft yearly stock return 2023"
- "Google annual stock performance 2023"

#### Annual Volatility
- "show Apple volatility 2023"
- "Microsoft annual volatility 2023"

#### Annual Dividend Yield
- "show Apple dividend yield 2023"
- "Microsoft annual dividend yield 2023"

---

## 🌍 **CATEGORY 4: MACRO INDICATORS**

### **Quarterly Macro Queries**
**Surface:** `vw_macro_quarter`

#### GDP Queries
- "show GDP Q2 2023"
- "what was real GDP Q3 2023"
- "quarterly GDP Q2 2023"

#### Inflation/CPI Queries
- "show CPI Q2 2023"
- "inflation rate Q3 2023"
- "consumer price index Q2 2023"
- "what was inflation Q3 2023"

#### Unemployment Queries
- "show unemployment rate Q2 2023"
- "unemployment Q3 2023"
- "jobless rate Q2 2023"

#### Fed Rate Queries
- "show Fed rate Q2 2023"
- "Federal Funds rate Q3 2023"
- "interest rate Q2 2023"
- "what was Fed rate Q3 2023"

#### S&P 500 Queries
- "show S&P 500 Q2 2023"
- "SPX index Q3 2023"
- "market index Q2 2023"

---

### **Annual Macro Queries**
**Surface:** `mv_macro_annual`

#### Annual GDP
- "show GDP 2023"
- "annual GDP 2023"
- "real GDP for 2023"

#### Annual Inflation
- "show CPI 2023"
- "inflation rate 2023"
- "annual inflation 2023"

#### Annual Unemployment
- "show unemployment rate 2023"
- "annual unemployment 2023"

#### Annual Fed Rate
- "show Fed rate 2023"
- "Federal Funds rate 2023"

#### Annual S&P 500
- "show S&P 500 2023"
- "annual market index 2023"

---

## 📉 **CATEGORY 5: MACRO SENSITIVITY (BETAS)**

### **Quarterly Macro Sensitivity**
**Surface:** `vw_macro_sensitivity_rolling`

#### Margin Sensitivity to CPI
- "show Apple margin sensitivity to CPI Q2 2023"
- "Microsoft beta to inflation Q3 2023"
- "Google CPI sensitivity Q2 2023"

#### Margin Sensitivity to Fed Rate
- "show Apple sensitivity to Fed rate Q2 2023"
- "Microsoft beta to interest rate Q3 2023"
- "Google Fed rate sensitivity Q2 2023"

#### Margin Sensitivity to S&P 500
- "show Apple beta to S&P 500 Q2 2023"
- "Microsoft market sensitivity Q3 2023"
- "Google SPX beta Q2 2023"

#### Margin Sensitivity to Unemployment
- "show Apple unemployment sensitivity Q2 2023"
- "Microsoft jobless rate beta Q3 2023"

#### General Sensitivity
- "show Apple macro sensitivity Q2 2023"
- "Microsoft economic sensitivity Q3 2023"
- "Google betas Q2 2023"

---

### **Annual Macro Sensitivity**
**Surface:** `mv_macro_sensitivity_annual`

#### Annual Sensitivity to CPI
- "show Apple margin sensitivity to CPI 2023"
- "Microsoft beta to inflation 2023"

#### Annual Sensitivity to Fed Rate
- "show Apple sensitivity to Fed rate 2023"
- "Microsoft beta to interest rate 2023"

#### Annual Sensitivity to S&P 500
- "show Apple beta to S&P 500 2023"
- "Microsoft market sensitivity 2023"

#### Annual Sensitivity to Unemployment
- "show Apple unemployment sensitivity 2023"
- "Microsoft jobless rate beta 2023"

#### General Annual Sensitivity
- "show Apple macro sensitivity 2023"
- "Microsoft economic sensitivity 2023"
- "Google annual betas 2023"

---

## 🎯 **CATEGORY 6: COMBINED VIEWS (NEW!)**

### **Layer 1: Core Company Data (Financials + Ratios + Stock)**

#### Quarterly Core Complete
**Surface:** `vw_company_complete_quarter`

- "show Apple complete picture Q2 2023"
- "everything about Microsoft Q3 2023"
- "comprehensive view of Google Q2 2023"
- "Amazon complete data Q3 2023"
- "Meta full snapshot Q2 2023"
- "show me all metrics for Apple Q2 2023"

**Returns:** Revenue, income, expenses, margins, ROE, ROA, debt ratios, stock price, returns, volatility

#### Annual Core Complete
**Surface:** `mv_company_complete_annual`

- "show Apple complete picture 2023"
- "everything about Microsoft 2023"
- "comprehensive annual view of Google 2023"
- "Amazon complete view 2023"
- "Meta full snapshot 2023"
- "show me all annual metrics for Apple 2023"

**Returns:** Annual revenue, income, expenses, margins, ROE, ROA, debt ratios, stock price, returns, volatility

---

### **Layer 2: With Macro Context (Company + Economic Data)**

#### Quarterly with Macro Context
**Surface:** `vw_company_macro_context_quarter`

- "show Apple with macro context Q2 2023"
- "Microsoft with economic context Q3 2023"
- "Google complete picture with inflation Q2 2023"
- "Amazon with GDP context Q3 2023"
- "Meta with unemployment rate Q2 2023"
- "Apple and economic indicators Q2 2023"
- "Microsoft plus macro Q3 2023"

**Returns:** All Layer 1 data PLUS GDP, CPI, unemployment, Fed rate, S&P 500

#### Annual with Macro Context
**Surface:** `mv_company_macro_context_annual`

- "show Apple with macro 2023"
- "Microsoft with economic context 2023"
- "Google annual with inflation 2023"
- "Amazon complete view with GDP 2023"
- "Meta with macro indicators 2023"
- "Apple and economic data 2023"

**Returns:** All Layer 1 annual data PLUS annual GDP, CPI, unemployment, Fed rate, S&P 500

---

### **Layer 3: Full Picture (Company + Macro + Sensitivity)**

#### Quarterly Full Analysis
**Surface:** `vw_company_full_quarter`

- "show Apple full analysis Q2 2023"
- "everything including betas for Microsoft Q3 2023"
- "complete picture with sensitivity for Google Q2 2023"
- "Amazon full analysis with betas Q3 2023"
- "Meta comprehensive with sensitivity Q2 2023"
- "Apple full view with macro sensitivity Q2 2023"

**Returns:** All Layer 2 data PLUS margin sensitivity betas (CPI, Fed rate, S&P 500, unemployment)

#### Annual Full Analysis
**Surface:** `mv_company_full_annual`

- "show Apple full analysis 2023"
- "everything including betas for Microsoft 2023"
- "complete picture with sensitivity for Amazon 2023"
- "Meta full view with betas 2023"
- "Google comprehensive with sensitivity 2023"
- "Apple full analysis with macro sensitivity 2023"

**Returns:** All Layer 2 annual data PLUS annual margin sensitivity betas

---

## 📊 **CATEGORY 7: GROWTH METRICS**

### **Quarterly Growth**
**Surface:** `vw_growth_quarter`

- "show Apple revenue growth Q2 2023"
- "Microsoft QoQ growth Q3 2023"
- "Google YoY growth Q2 2023"
- "Amazon quarterly growth rates Q3 2023"

### **Annual Growth & CAGR**
**Surface:** `vw_growth_annual`

- "show Apple annual growth 2023"
- "Microsoft 3-year CAGR 2023"
- "Google 5-year CAGR 2023"
- "Amazon revenue CAGR 2023"

---

## 🏆 **CATEGORY 8: PEER COMPARISONS**

### **Quarterly Peer Rankings**
**Surface:** `vw_peer_stats_quarter`

- "who led in revenue Q2 2023"
- "rank companies by net margin Q3 2023"
- "peer comparison Q2 2023"
- "leaderboard Q3 2023"

### **Annual Peer Rankings**
**Surface:** `vw_peer_stats_annual`

- "who led in revenue 2023"
- "rank companies by operating margin 2023"
- "annual peer comparison 2023"
- "leaderboard 2023"

---

## 🔍 **CATEGORY 9: TTM (TRAILING 12 MONTHS)**

### **TTM Financials**
**Surface:** `mv_financials_ttm`

- "show Apple TTM revenue"
- "Microsoft trailing 12 months revenue"
- "Google last 12 months net income"

### **TTM Ratios**
**Surface:** `mv_ratios_ttm`

- "show Apple TTM gross margin"
- "Microsoft trailing 12 months ROE"
- "Google last 12 months net margin"

### **TTM Growth**
**Surface:** `vw_growth_ttm`

- "show Apple TTM growth"
- "Microsoft trailing 12 months growth rate"

---

## 💬 **CATEGORY 10: SPECIAL QUERIES**

### **Latest Quarter Queries**
- "show Apple latest quarter revenue"
- "Microsoft most recent quarter"
- "Google latest financials"
- "Amazon current quarter metrics"

### **Multi-Metric Queries**
- "show Apple revenue and net income Q2 2023"
- "Microsoft margins and ROE Q3 2023"
- "Google financials and ratios Q2 2023"

### **Multi-Company Queries**
- "show revenue for all companies Q2 2023"
- "compare net margin across companies 2023"
- "who had highest ROE Q3 2023"

### **Financial Health**
**Surface:** `vw_financial_health_quarter`
- "show Apple financial health Q2 2023"
- "Microsoft financial strength Q3 2023"

### **Outlier Detection**
**Surface:** `vw_outliers_quarter`
- "show outliers Q2 2023"
- "anomalies in Q3 2023"

---

## 🎨 **QUERY VARIATIONS SUPPORTED**

### **Time Period Variations**
- "Q2 2023", "2023 Q2", "second quarter 2023", "FY2023 Q2"
- "2023", "FY2023", "fiscal year 2023", "annual 2023"
- "latest quarter", "most recent", "current quarter"

### **Company Name Variations**
- "Apple" / "AAPL" / "Apple Inc"
- "Microsoft" / "MSFT" / "Microsoft Corp"
- "Google" / "GOOGL" / "Alphabet"
- "Amazon" / "AMZN" / "Amazon.com"
- "Meta" / "META" / "Facebook"

### **Metric Name Variations**
- "revenue" / "sales" / "top line"
- "net income" / "income" / "profit" / "earnings" / "bottom line"
- "operating income" / "operating profit" / "EBIT"
- "R&D" / "research and development" / "R&D expenses"
- "SG&A" / "selling general and administrative"
- "ROE" / "return on equity"
- "ROA" / "return on assets"

---

## 📈 **TOTAL QUERY CAPABILITIES**

| Category | Quarterly | Annual | TTM | Combined | Total |
|----------|-----------|--------|-----|----------|-------|
| **Financials** | 15 metrics | 15 metrics | 15 metrics | ✓ | 45+ |
| **Ratios** | 9 ratios | 9 ratios | 9 ratios | ✓ | 27+ |
| **Stock** | 5 metrics | 5 metrics | - | ✓ | 10+ |
| **Macro** | 5 indicators | 5 indicators | - | ✓ | 10+ |
| **Sensitivity** | 8 betas | 8 betas | - | ✓ | 16+ |
| **Growth** | ✓ | ✓ | ✓ | - | 6+ |
| **Peer** | ✓ | ✓ | - | - | 2+ |
| **Combined** | 3 layers | 3 layers | - | - | 6+ |

**Total Unique Query Types:** 200+

**Total Possible Questions:** 1000+ (with variations)

---

## 🎯 **EXAMPLE QUERIES BY USE CASE**

### **Executive Summary**
- "show Apple complete picture 2023"
- "Microsoft full analysis 2023"

### **Quarterly Business Review**
- "show Apple complete picture Q2 2023"
- "Apple Q2 2023 revenue and margins"

### **Economic Context**
- "show Apple with macro context Q2 2023"
- "Microsoft with economic environment 2023"

### **Risk Analysis**
- "show Apple full analysis with betas 2023"
- "Apple macro sensitivity Q2 2023"

### **Competitive Analysis**
- "who led in revenue 2023"
- "compare net margin across companies Q2 2023"

### **Trend Analysis**
- "show Apple 3-year CAGR 2023"
- "Apple YoY growth Q2 2023"

### **Financial Health Check**
- "show Apple debt ratios Q2 2023"
- "Microsoft financial health Q3 2023"

---

## 🚀 **QUICK REFERENCE: TOP 20 MOST USEFUL QUERIES**

1. "show [company] complete picture Q2 2023" - Core company snapshot
2. "show [company] complete picture 2023" - Annual snapshot
3. "show [company] with macro context Q2 2023" - With economic data
4. "show [company] full analysis 2023" - Complete view with betas
5. "show [company] revenue Q2 2023" - Revenue
6. "show [company] net income Q2 2023" - Profitability
7. "show [company] gross margin Q2 2023" - Efficiency
8. "show [company] ROE Q2 2023" - Returns
9. "show [company] debt to equity Q2 2023" - Leverage
10. "show [company] stock price Q2 2023" - Stock performance
11. "show [company] R&D expenses Q2 2023" - Innovation spending
12. "show [company] cash flow Q2 2023" - Liquidity
13. "show [company] operating margin 2023" - Profitability
14. "show [company] annual growth 2023" - Growth rates
15. "who led in revenue 2023" - Peer comparison
16. "show [company] macro sensitivity 2023" - Risk analysis
17. "show GDP Q2 2023" - Economic context
18. "show [company] latest quarter revenue" - Most recent data
19. "show [company] TTM revenue" - Trailing 12 months
20. "show [company] beta to inflation Q2 2023" - Specific sensitivity

---

## 📝 **NOTES**

- All queries support **5 companies**: Apple (AAPL), Microsoft (MSFT), Google (GOOGL), Amazon (AMZN), Meta (META)
- **Time range**: 2017-2024 (varies by company and metric)
- **Quarterly data**: Q1, Q2, Q3, Q4 for each fiscal year
- **Annual data**: Full fiscal year aggregates
- **TTM data**: Rolling 12-month calculations
- **Natural language**: Agent understands many variations and synonyms
- **Limit**: All queries limited to 200 records for safety

---

**Last Updated:** October 19, 2025
**Version:** 2.0 (Combined Views Integration)
