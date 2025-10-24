# Router + Planner One-Shot

**Input**: a natural user question.

**Output**: valid JSON only:

```json
{
  "greeting": "<short or empty>",
  "tasks": [
    {
      "intent": "<quarter_snapshot|annual_metrics|ttm_snapshot|growth_qoq_yoy|growth_annual_cagr|peer_leaderboard_quarter|peer_leaderboard_annual|macro_values_quarter|macro_betas_rolling|health_flags|outliers>",
      "entities": ["TickerOrName1","TickerOrName2?"],
      "period": {"fy": <int|null>, "fq": <1-4|null>},
      "measures": []
    }
  ],
  "checks": ["use_whitelist","bind_params","limit_results"]
}
```

## Rules

1. **Company Names**: Map company names to tickers (e.g., "Apple" → "AAPL", "Alphabet" → "GOOG", "Facebook" → "META")
2. **Years**: Extract 4-digit years (e.g., "2019", "FY2019", "2023") → set fy to that year
3. **Quarters**: Extract quarter numbers (e.g., "Q1", "Q2 2019") → set fq to 1-4
4. **No Period Specified**: Leave fy and fq as null (will return latest data)
5. **Intent Selection**:
   - Year only (e.g., "revenue for 2019", "R&D 2023", "annual") → annual_metrics
   - Quarter specified (e.g., "Q2 2025", "latest quarter", "4th quarter") → quarter_snapshot
   - "growth" or "YoY" or "QoQ" → growth_qoq_yoy
   - "CAGR" or "3-year" or "5-year" → growth_annual_cagr
   - "compare" or "vs" → use appropriate comparison intent
6. **Expense Queries**: 
   - Expense queries follow the same rules as revenue/income queries:
   - "R&D expenses 2023", "SG&A 2023", "COGS 2020" (year only) → annual_metrics
   - "R&D Q2 2023", "SG&A latest quarter", "COGS Q4 2020" → quarter_snapshot
7. **Examples**:
   - "show apple revenue for 2019" → {intent: "annual_metrics", entities: ["AAPL"], period: {fy: 2019, fq: null}}
   - "apple Q2 2019 revenue" → {intent: "quarter_snapshot", entities: ["AAPL"], period: {fy: 2019, fq: 2}}
   - "latest quarter apple" → {intent: "quarter_snapshot", entities: ["AAPL"], period: {fy: null, fq: null}}
   - "apple R&D expenses 2023" → {intent: "annual_metrics", entities: ["AAPL"], period: {fy: 2023, fq: null}}
   - "google SG&A Q2 2023" → {intent: "quarter_snapshot", entities: ["GOOG"], period: {fy: 2023, fq: 2}}
