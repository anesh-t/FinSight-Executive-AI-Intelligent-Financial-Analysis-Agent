# 📊 Structured Data Test Queries

## Comprehensive Test Suite for SQL-Based Agent

---

## ✅ Validation Criteria

For each query, check:
1. **SQL Execution:** Query successfully retrieves data from database
2. **Data Display:** Results are shown in the chat interface
3. **Answer Quality:** Response makes sense and is accurate
4. **Citations:** Sources are properly cited (ALPHAVANTAGE_FIN, FRED, YF)
5. **Response Time:** Query completes in < 5 seconds

---

## 📋 Test Categories

1. Basic Financial Metrics (20 queries)
2. Growth Analysis (15 queries)
3. Peer Comparisons (15 queries)
4. Macro-Economic Queries (15 queries)
5. Stock Market Queries (10 queries)
6. Time Series Queries (10 queries)
7. Ratio & Margin Queries (15 queries)
8. Edge Cases & Error Handling (10 queries)

**Total: 110 Structured Queries**

---

## 1️⃣ BASIC FINANCIAL METRICS (20 Queries)

### Revenue Queries

**Q1.1:** What is Apple's revenue in Q2 2023?

**Q1.2:** Show Microsoft's revenue for Q1 2023

**Q1.3:** Get Google's revenue last quarter

**Q1.4:** What was Amazon's revenue in FY 2023?

**Q1.5:** Show Meta's revenue Q3 2023

### Net Income Queries

**Q1.6:** What is Apple's net income Q2 2023?

**Q1.7:** Show Microsoft's profit for Q1 2023

**Q1.8:** Get Google's net income FY 2023

**Q1.9:** What was Amazon's earnings Q2 2023?

**Q1.10:** Show Meta's net income last quarter

### Operating Income Queries

**Q1.11:** What is Apple's operating income Q2 2023?

**Q1.12:** Show Microsoft's EBIT Q1 2023

### Gross Profit Queries

**Q1.13:** What is Apple's gross profit Q2 2023?

**Q1.14:** Show Google's gross profit FY 2023

### Multiple Metrics

**Q1.15:** Show Apple's revenue and net income Q2 2023

**Q1.16:** Get Microsoft's revenue, net income, and operating income Q1 2023

**Q1.17:** What are Google's key financials Q3 2023?

### Balance Sheet Items

**Q1.18:** What is Apple's total assets Q2 2023?

**Q1.19:** Show Microsoft's total debt Q1 2023

**Q1.20:** Get Google's equity Q3 2023

---

## 2️⃣ GROWTH ANALYSIS (15 Queries)

### Quarter-over-Quarter (QoQ)

**Q2.1:** What is Apple's revenue QoQ growth Q2 2023?

**Q2.2:** Show Microsoft's net income QoQ change Q1 2023

**Q2.3:** Get Google's revenue quarter over quarter growth Q3 2023

**Q2.4:** What is Amazon's margin QoQ improvement Q2 2023?

**Q2.5:** Show Meta's revenue sequential growth Q1 2023

### Year-over-Year (YoY)

**Q2.6:** What is Apple's revenue YoY growth Q2 2023?

**Q2.7:** Show Microsoft's net income year over year change Q1 2023

**Q2.8:** Get Google's revenue YoY Q3 2023

**Q2.9:** What is Amazon's annual revenue growth FY 2023?

**Q2.10:** Show Meta's net income year-on-year growth Q2 2023

### CAGR

**Q2.11:** What is Apple's 3-year revenue CAGR ending 2023?

**Q2.12:** Calculate Microsoft's 5-year revenue CAGR ending FY 2023

**Q2.13:** Show Google's revenue CAGR from 2020 to 2023

### Growth with Values

**Q2.14:** Show Apple's revenue and YoY growth Q2 2023

**Q2.15:** Get Microsoft's net income with QoQ and YoY growth Q1 2023

---

## 3️⃣ PEER COMPARISONS (15 Queries)

### Simple Rankings

**Q3.1:** Who led on revenue last quarter?

**Q3.2:** Who had the highest net margin Q2 2023?

**Q3.3:** Rank companies by operating margin Q3 2023

**Q3.4:** Who led on net income FY 2023?

**Q3.5:** Show revenue leaders Q2 2023

### Two-Company Comparisons

**Q3.6:** Compare Apple and Microsoft revenue Q2 2023

**Q3.7:** Compare Google and Meta net margin Q3 2023

**Q3.8:** Show Apple vs Amazon revenue Q2 2023

**Q3.9:** Compare Microsoft and Google operating margin Q1 2023

**Q3.10:** Apple vs Microsoft: who has better ROE Q2 2023?

### Multi-Company Comparisons

**Q3.11:** Compare Apple, Microsoft, and Google revenue Q2 2023

**Q3.12:** Show margins for all companies Q3 2023

**Q3.13:** Compare revenue for AAPL, MSFT, AMZN, GOOG Q2 2023

### Statistics

**Q3.14:** Show Apple's revenue percentile Q2 2023

**Q3.15:** What is the average revenue across all companies Q2 2023?

---

## 4️⃣ MACRO-ECONOMIC QUERIES (15 Queries)

### Company + Single Macro

**Q4.1:** Show Apple's revenue with CPI for Q2 2023

**Q4.2:** Get Microsoft's performance with GDP context Q1 2023

**Q4.3:** Show Google's revenue with unemployment rate Q3 2023

**Q4.4:** What is Amazon's revenue with Fed rate Q2 2023?

**Q4.5:** Show Meta's margins with CPI Q1 2023

### Company + Multiple Macro

**Q4.6:** Show Apple's revenue with GDP and CPI Q2 2023

**Q4.7:** Get Microsoft's performance with CPI, unemployment, and Fed rate Q1 2023

**Q4.8:** Show Google's financials with macro context Q3 2023

### Macro Sensitivity

**Q4.9:** What is Apple's net margin beta to CPI?

**Q4.10:** Show Microsoft's margin sensitivity to inflation

**Q4.11:** Get Google's operating margin beta to Fed rate

**Q4.12:** What is Amazon's sensitivity to unemployment?

### Pure Macro

**Q4.13:** What was GDP in Q2 2023?

**Q4.14:** Show CPI and unemployment for Q3 2023

**Q4.15:** What was the Fed rate in Q1 2023?

---

## 5️⃣ STOCK MARKET QUERIES (10 Queries)

### Stock Prices

**Q5.1:** What is Apple's stock price Q2 2023?

**Q5.2:** Show Microsoft's closing price Q1 2023

**Q5.3:** Get Google's opening price Q3 2023

**Q5.4:** What was Amazon's high price Q2 2023?

**Q5.5:** Show Meta's low price Q1 2023

### Stock Returns

**Q5.6:** What is Apple's stock return Q2 2023?

**Q5.7:** Show Microsoft's price change Q1 2023

### Stock + Financials

**Q5.8:** Show Apple's revenue and stock price Q2 2023

**Q5.9:** Get Microsoft's net income and stock return Q1 2023

**Q5.10:** Compare Google's revenue growth and stock performance Q3 2023

---

## 6️⃣ TIME SERIES QUERIES (10 Queries)

### Last N Quarters

**Q6.1:** Show Apple's revenue for the last 4 quarters

**Q6.2:** Get Microsoft's net income over the last 6 quarters

**Q6.3:** Show Google's margins for the last 8 quarters

**Q6.4:** What is Amazon's revenue trend last 4 quarters?

### Last N Years

**Q6.5:** Show Apple's annual revenue for the last 3 years

**Q6.6:** Get Microsoft's net income over the last 2 years

### Specific Date Ranges

**Q6.7:** Show Apple's revenue from Q1 2022 to Q4 2023

**Q6.8:** Get Microsoft's margins for all of 2023

**Q6.9:** Show Google's quarterly revenue for 2023

**Q6.10:** What was Amazon's revenue each quarter in 2023?

---

## 7️⃣ RATIO & MARGIN QUERIES (15 Queries)

### Margin Queries

**Q7.1:** What is Apple's gross margin Q2 2023?

**Q7.2:** Show Microsoft's operating margin Q1 2023

**Q7.3:** Get Google's net margin Q3 2023

**Q7.4:** Show Amazon's profit margin Q2 2023

**Q7.5:** What are Meta's margins Q1 2023?

### Return Ratios

**Q7.6:** What is Apple's ROE Q2 2023?

**Q7.7:** Show Microsoft's return on equity Q1 2023

**Q7.8:** Get Google's ROA Q3 2023

**Q7.9:** What is Amazon's return on assets Q2 2023?

### Debt Ratios

**Q7.10:** What is Apple's debt-to-equity ratio Q2 2023?

**Q7.11:** Show Microsoft's debt to equity Q1 2023

**Q7.12:** Get Google's debt-to-assets ratio Q3 2023

### Expense Ratios

**Q7.13:** What is Apple's R&D intensity Q2 2023?

**Q7.14:** Show Microsoft's R&D to revenue ratio Q1 2023

**Q7.15:** Get Google's SG&A intensity Q3 2023?

---

## 8️⃣ EDGE CASES & ERROR HANDLING (10 Queries)

### Ambiguous Queries

**Q8.1:** Show Apple's performance Q2 2023

**Q8.2:** Get Microsoft's metrics Q1 2023

**Q8.3:** What is Google doing?

### Invalid Periods

**Q8.4:** Show Apple's revenue Q5 2023

**Q8.5:** Get Microsoft's data for Q1 2030

### Invalid Companies

**Q8.6:** What is Tesla's revenue Q2 2023?

**Q8.7:** Show Netflix's net income Q1 2023

### Incomplete Queries

**Q8.8:** Apple revenue

**Q8.9:** Microsoft Q2

**Q8.10:** Show margins

---

## 📊 Expected Results Format

### Example 1: Simple Metric
**Query:** What is Apple's revenue in Q2 2023?

**Expected Output:**
```
Apple Inc. (AAPL) reported revenue of $81.80B for Q2 FY2023.

Sources: ALPHAVANTAGE_FIN (as_reported, 2025-10-12 10:33:18); YF; FRED
```

### Example 2: Growth
**Query:** What is Apple's revenue YoY growth Q2 2023?

**Expected Output:**
```
Apple Inc. (AAPL) - Q2 FY2023

Revenue: $81.80B
YoY Growth: -2.5%

Sources: ALPHAVANTAGE_FIN (as_reported, 2025-10-12 10:33:18); YF; FRED
```

### Example 3: Comparison
**Query:** Compare Apple and Microsoft revenue Q2 2023

**Expected Output:**
```
Revenue Comparison - Q2 2023:

Apple Inc. (AAPL): $81.80B
Microsoft Corporation (MSFT): $52.86B

Apple leads by $28.94B (+54.8%)

Sources: ALPHAVANTAGE_FIN (as_reported, 2025-10-12 10:33:18); YF; FRED
```

### Example 4: Macro Context
**Query:** Show Apple's revenue with CPI for Q2 2023

**Expected Output:**
```
Apple Inc. (AAPL) reported revenue of $81.80B for Q2 FY2023. 
Macro context: GDP $26.79T, CPI 304.13, unemployment 3.50%, 
Fed rate 5.08%, S&P 500 4,179.83.

Sources: ALPHAVANTAGE_FIN (as_reported, 2025-10-12 10:33:18); YF; FRED
```

---

## ✅ Testing Checklist

For each query, verify:

- [ ] Query is understood correctly
- [ ] SQL is generated and executed
- [ ] Data is retrieved from database
- [ ] Response is displayed in chat
- [ ] Numbers are formatted properly ($XXB, XX.X%)
- [ ] Company names are correct
- [ ] Periods are correct (Q2 2023, FY 2023, etc.)
- [ ] Citations are included
- [ ] Response makes logical sense
- [ ] No errors or exceptions
- [ ] Response time < 5 seconds

---

**Total Queries: 110**
**Estimated Testing Time: 2-3 hours**
