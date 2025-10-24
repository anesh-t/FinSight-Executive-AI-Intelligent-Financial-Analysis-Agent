# 📊 CFO Intelligence Platform - Data Coverage

## Overview

The platform uses a **hybrid data model** combining quarterly financial reports with real-time market and economic data.

---

## 📅 Company Financials (Quarterly Updates)

### Coverage Period
- **Start:** Q1 2019
- **End:** Q2 2025 (as of October 2025)
- **Total Periods:** ~26 quarters per company

### Update Frequency
- ⏱️ **Quarterly** - Updated after each company's earnings release
- 📅 **Next Update:** When Q3 2025 earnings are released (typically November 2025)

### Data Source
- **Primary:** AlphaVantage API
- **Type:** as_reported financials (GAAP/IFRS compliant)
- **Quality:** Official SEC filings (10-Q, 10-K)

### Metrics Included (15+)
- Revenue, Net Income, Operating Income, Gross Profit
- R&D Expenses, SG&A Expenses, COGS
- Operating Cash Flow, Investing Cash Flow, Financing Cash Flow
- Capex, Dividends, Buybacks, EPS
- Total Assets, Total Liabilities, Equity

### Calculated Ratios (9)
- Gross Margin, Operating Margin, Net Margin
- ROE (Return on Equity), ROA (Return on Assets)
- Debt-to-Equity, Debt-to-Assets
- R&D Intensity, SG&A Intensity

---

## 📈 Stock Prices (Real-time)

### Coverage Period
- **Historical:** Full history available
- **Current:** Real-time / Latest market data
- **Frequency:** Daily updates

### Data Source
- **Primary:** YahooFinance API
- **Type:** Daily OHLCV (Open, High, Low, Close, Volume)
- **Quality:** Market-grade pricing data

### Metrics Included (5)
- Stock Price (Close)
- Stock Returns (Daily, QoQ, YoY)
- Volatility (Standard deviation of returns)
- Market Performance
- Price Trends

### Update Schedule
- 📊 **Intraday:** During market hours (9:30 AM - 4:00 PM ET)
- 🕐 **Daily Close:** Updated after market close (~4:15 PM ET)
- 📅 **Historical:** Available for backtesting

---

## 🌍 Macro Economic Indicators (Real-time)

### Coverage Period
- **Historical:** Multiple years of history
- **Current:** Latest published data
- **Frequency:** Varies by indicator

### Data Source
- **Primary:** FRED (Federal Reserve Economic Data)
- **Type:** Government-published economic statistics
- **Quality:** Official U.S. government data

### Indicators Included (5+)

#### GDP (Gross Domestic Product)
- **Update:** Quarterly (with revisions)
- **Latest:** Published ~1 month after quarter end
- **Units:** Billions of dollars

#### CPI (Consumer Price Index)
- **Update:** Monthly
- **Latest:** Published ~2 weeks after month end
- **Units:** Index (base year = 100)

#### Unemployment Rate
- **Update:** Monthly
- **Latest:** First Friday of each month
- **Units:** Percentage

#### Fed Funds Rate
- **Update:** As set by FOMC (8 meetings/year)
- **Latest:** Immediately after FOMC decisions
- **Units:** Percentage

#### S&P 500 Index
- **Update:** Real-time during market hours
- **Latest:** Current market data
- **Units:** Index points

### Update Schedule by Indicator

| Indicator | Update Frequency | Typical Release | Source Agency |
|-----------|------------------|-----------------|---------------|
| GDP | Quarterly | ~30 days after quarter | BEA |
| CPI | Monthly | ~15 days after month | BLS |
| Unemployment | Monthly | 1st Friday of month | BLS |
| Fed Funds Rate | 8x/year | FOMC meeting days | Federal Reserve |
| S&P 500 | Real-time | Market hours | S&P Dow Jones |

---

## 📉 Derived Metrics (Calculated)

### Macro Sensitivity Betas (8 betas)
- **Calculation:** Regression of company metrics vs. macro indicators
- **Update:** Recalculated quarterly when new financial data available
- **Coverage:** Same as company financials (2019-Q2 2025)

**Included:**
- Revenue Beta to CPI, GDP, Fed Rate, Unemployment, S&P 500
- Margin Beta to CPI, GDP, S&P 500

### Growth Metrics
- **QoQ (Quarter-over-Quarter):** Calculated from consecutive quarters
- **YoY (Year-over-Year):** Calculated from same quarter previous year
- **CAGR (3-year, 5-year):** Compound annual growth rate

**Update:** Recalculated each quarter with new data

---

## 🏢 Company-Specific Coverage

### Apple Inc. (AAPL)
- **Financials:** Q1 2019 - Q2 2025 (26+ quarters)
- **Stock Data:** Real-time
- **Fiscal Year:** Ends September 30

### Microsoft Corporation (MSFT)
- **Financials:** Q1 2019 - Q2 2025 (26+ quarters)
- **Stock Data:** Real-time
- **Fiscal Year:** Ends June 30

### Alphabet Inc. (GOOG)
- **Financials:** Q1 2019 - Q2 2025 (26+ quarters)
- **Stock Data:** Real-time
- **Fiscal Year:** Ends December 31

### Amazon.com Inc. (AMZN)
- **Financials:** Q1 2019 - Q2 2025 (26+ quarters)
- **Stock Data:** Real-time
- **Fiscal Year:** Ends December 31

### Meta Platforms Inc. (META)
- **Financials:** Q1 2019 - Q2 2025 (26+ quarters)
- **Stock Data:** Real-time
- **Fiscal Year:** Ends December 31

---

## 🔄 Data Update Workflow

### Quarterly Financial Updates

**When New Earnings Released:**
1. Company reports earnings (typically 3-4 weeks after quarter end)
2. AlphaVantage updates their database (~1-2 days after earnings)
3. Manual or automated data pipeline runs
4. New data ingested into PostgreSQL/Supabase
5. Materialized views refreshed
6. Platform immediately reflects new data

**Typical Timeline:**
- Quarter ends (e.g., June 30 for Q2)
- Earnings release (e.g., July 20-30)
- Data available in platform (e.g., July 22 - August 1)

### Real-time Updates

**Stock Prices:**
- YahooFinance API queried on-demand
- Cache: Short-lived (15 minutes during market hours)
- After hours: Last closing price

**Macro Indicators:**
- FRED API queried on-demand
- Cache: 24 hours (data doesn't change intraday)
- Updated when government publishes new releases

---

## 📊 Data Quality & Validation

### Company Financials
- ✅ Source: Official SEC filings
- ✅ Type: As-reported (not adjusted)
- ✅ Validation: Cross-checked with company investor relations
- ✅ Completeness: All required fields present
- ✅ Consistency: Balance sheet equation verified

### Stock Prices
- ✅ Source: Market-grade data (YahooFinance)
- ✅ Validation: Spot-checked against major exchanges
- ✅ Completeness: Daily OHLCV available
- ✅ Corporate Actions: Adjusted for splits/dividends

### Macro Indicators
- ✅ Source: Official government agencies
- ✅ Validation: FRED is authoritative source
- ✅ Revisions: Historical data may be revised by agencies
- ✅ Seasonality: Some indicators seasonally adjusted

---

## 🎯 Data Limitations & Known Gaps

### Company Financials

**What's Available:**
- ✅ Quarterly income statements (2019-Q2 2025)
- ✅ Quarterly balance sheets (2019-Q2 2025)
- ✅ Quarterly cash flow statements (2019-Q2 2025)
- ✅ Calculated financial ratios

**What's NOT Available:**
- ❌ Pre-2019 historical data
- ❌ Q3 2025 and future quarters (not yet reported)
- ❌ Segment-level breakdowns
- ❌ Geographic revenue splits
- ❌ Product-line specific data

### Stock Data

**What's Available:**
- ✅ Daily closing prices (real-time)
- ✅ Historical price data (full history)
- ✅ Basic returns and volatility

**What's NOT Available:**
- ❌ Intraday tick data
- ❌ Order book data
- ❌ Options data
- ❌ Short interest

### Macro Data

**What's Available:**
- ✅ Key U.S. economic indicators
- ✅ Historical time series
- ✅ Latest published values

**What's NOT Available:**
- ❌ Global economic indicators (non-U.S.)
- ❌ State/regional breakdowns
- ❌ Real-time economic forecasts
- ❌ Proprietary economic indices

---

## 💡 How to Query Different Data Types

### For Company Financials (Quarterly)
```
"show Apple revenue Q2 2023"
"show Microsoft net income Q3 2024"
"show Google gross margin Q1 2025"
```
**Data Source:** AlphaVantage (2019-Q2 2025)

### For Stock Prices (Real-time)
```
"show Apple stock price Q2 2023"
"show Microsoft stock return 2024"
"show Google volatility Q1 2025"
```
**Data Source:** YahooFinance (real-time/historical)

### For Macro Indicators (Real-time)
```
"show GDP Q2 2023"
"show CPI 2024"
"show unemployment rate Q1 2025"
```
**Data Source:** FRED (real-time)

### For Combined Analysis
```
"show Apple with macro context Q2 2023"
"show Microsoft full analysis Q3 2024"
```
**Combines:** Company financials + Stock prices + Macro indicators

---

## 📅 Expected Update Schedule (Future)

### Q3 2025 (July-September 2025)
- **Earnings:** Expected October-November 2025
- **Data Availability:** November 2025

### Q4 2025 (October-December 2025)
- **Earnings:** Expected January-February 2026
- **Data Availability:** February 2026

### 2026 and Beyond
- Quarterly updates will continue as companies report earnings
- Stock and macro data remain real-time

---

## ✅ Summary

### Data Freshness by Type

| Data Type | Coverage | Update Frequency | Latency |
|-----------|----------|------------------|---------|
| **Company Financials** | 2019-Q2 2025 | Quarterly | 1-4 weeks after quarter |
| **Stock Prices** | Real-time | Daily/Intraday | < 15 minutes |
| **Macro Indicators** | Real-time | Varies (Monthly/Quarterly) | Same day as release |
| **Calculated Ratios** | 2019-Q2 2025 | Quarterly | Same as financials |
| **Sensitivity Betas** | 2019-Q2 2025 | Quarterly | Same as financials |

### Key Points
- ✅ **Financials:** Quarterly snapshots from official SEC filings
- ✅ **Stock/Macro:** Real-time market and economic data
- ✅ **Hybrid Model:** Best of both worlds - fundamental + market data
- ✅ **Quality:** Enterprise-grade data from authoritative sources
- ✅ **Updates:** Automatic for real-time; quarterly ingestion for financials

---

**For Questions About Data Coverage:**
- Check the "About This Platform" section in the UI
- Review the Technical Details expandable section
- Refer to this document for detailed specifications

**Last Updated:** October 20, 2025  
**Document Version:** 1.0
