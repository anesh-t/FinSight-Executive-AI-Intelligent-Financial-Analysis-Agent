# DATA SOURCE MAPPING - All 9 Ratios

## Complete mapping of where each ratio is sourced for annual and quarterly queries

---

## 📊 **ANNUAL RATIOS (All from `mv_ratios_annual`)**

| Ratio | DB Column | Template | Status |
|-------|-----------|----------|--------|
| **ROE** | `roe_annual_avg_equity` | `annual_metrics` | ✅ Working |
| **ROA** | `roa_annual` | `annual_metrics` | ✅ Working |
| **Gross Margin** | `gross_margin_annual` | `annual_metrics` | ✅ Working |
| **Operating Margin** | `operating_margin_annual` | `annual_metrics` | ✅ Working |
| **Net Margin** | `net_margin_annual` | `annual_metrics` | ✅ Working |
| **Debt-to-Equity** | `debt_to_equity_annual` | `annual_metrics` | ⚠️ Verbose |
| **Debt-to-Assets** | `debt_to_assets_annual` | `annual_metrics` | ⚠️ Verbose |
| **R&D Intensity** | `rnd_to_revenue_annual` | `annual_metrics` | ✅ Working |
| **SG&A Intensity** | `sgna_to_revenue_annual` | `annual_metrics` | ✅ Working |

**SQL Join:**
```sql
FROM mv_financials_annual mv
JOIN mv_ratios_annual r USING (company_id, fiscal_year)
```

---

## 📊 **QUARTERLY RATIOS - Current Implementation**

### **Source 1: `fact_financials` (via `quarter_snapshot` template)**

**Working Ratios (5/9):**

| Ratio | DB Column | Calculation | Status |
|-------|-----------|-------------|--------|
| **ROE** | N/A | `f.net_income/NULLIF(f.equity,0)` | ✅ Working |
| **ROA** | N/A | `f.net_income/NULLIF(f.total_assets,0)` | ✅ Working |
| **Gross Margin** | N/A | `f.gross_profit/NULLIF(f.revenue,0)` | ✅ Working |
| **Operating Margin** | N/A | `f.operating_income/NULLIF(f.revenue,0)` | ✅ Working |
| **Net Margin** | N/A | `f.net_income/NULLIF(f.revenue,0)` | ✅ Working |

**SQL:**
```sql
SELECT 
  c.ticker, f.fiscal_year, f.fiscal_quarter,
  f.gross_profit/NULLIF(f.revenue,0) as gross_margin,
  f.operating_income/NULLIF(f.revenue,0) as operating_margin,
  f.net_income/NULLIF(f.revenue,0) as net_margin,
  f.net_income/NULLIF(f.equity,0) as roe,
  f.net_income/NULLIF(f.total_assets,0) as roa
FROM fact_financials f
JOIN dim_company c USING (company_id)
WHERE c.ticker = :ticker 
  AND f.fiscal_year = :fy 
  AND f.fiscal_quarter = :fq
```

---

### **Source 2: `fact_ratios` (via `quarterly_ratios` template)**

**Available but Not Routing (4/9):**

| Ratio | DB Column | Template | Status |
|-------|-----------|----------|--------|
| **Debt-to-Equity** | `debt_to_equity` | `quarterly_ratios` | ❌ Not routing |
| **Debt-to-Assets** | `debt_to_assets` | `quarterly_ratios` | ❌ Not routing |
| **R&D Intensity** | `rnd_to_revenue` | `quarterly_ratios` | ❌ Not routing |
| **SG&A Intensity** | `sgna_to_revenue` | `quarterly_ratios` | ❌ Not routing |

**SQL:**
```sql
SELECT 
  c.ticker, fr.fiscal_year, fr.fiscal_quarter,
  fr.debt_to_equity,
  fr.debt_to_assets,
  fr.rnd_to_revenue,
  fr.sgna_to_revenue
FROM fact_ratios fr
JOIN dim_company c USING (company_id)
WHERE c.ticker = :ticker 
  AND fr.fiscal_year = :fy 
  AND fr.fiscal_quarter = :fq
```

**Verified Data (Apple Q2 2023):**
```
debt_to_equity:  4.5586
debt_to_assets:  0.8201
rnd_to_revenue:  0.0910 (9.1%)
sgna_to_revenue: 0.0730 (7.3%)
```

---

### **Source 3: `mv_ratios_ttm` (via `ttm_snapshot` template)**

**TTM Ratios Alternative (5/9):**

| Ratio | DB Column | Template | Status |
|-------|-----------|----------|--------|
| **ROE (TTM)** | `roe_ttm` | `ttm_snapshot` | ⏸️ Available |
| **ROA (TTM)** | `roa_ttm` | `ttm_snapshot` | ⏸️ Available |
| **Gross Margin (TTM)** | `gross_margin_ttm` | `ttm_snapshot` | ⏸️ Available |
| **Operating Margin (TTM)** | `operating_margin_ttm` | `ttm_snapshot` | ⏸️ Available |
| **Net Margin (TTM)** | `net_margin_ttm` | `ttm_snapshot` | ⏸️ Available |

**Note:** You recreated this view. It contains only 5 ratios (margins + ROE + ROA), no debt or intensity.

**SQL:**
```sql
SELECT 
  c.ticker, r.fiscal_year, r.fiscal_quarter,
  r.gross_margin_ttm,
  r.operating_margin_ttm,
  r.net_margin_ttm,
  r.roe_ttm,
  r.roa_ttm
FROM mv_ratios_ttm r
JOIN dim_company c USING (company_id)
WHERE c.ticker = :ticker 
  AND r.fiscal_year = :fy 
  AND r.fiscal_quarter = :fq
```

---

## 🗺️ **COMPLETE QUERY ROUTING MAP**

```
Annual Query: "show Apple ROE for 2023"
  ├─ Template: annual_metrics
  ├─ Source: mv_ratios_annual
  ├─ Column: roe_annual_avg_equity
  └─ Status: ✅ Working

Quarterly Query: "show Apple ROE for Q2 2023"
  ├─ Template: quarter_snapshot
  ├─ Source: fact_financials
  ├─ Calculation: net_income/equity
  └─ Status: ✅ Working

Quarterly Query: "show Apple debt to equity for Q2 2023"
  ├─ Currently routes to: quarter_snapshot
  ├─ Current source: fact_financials
  ├─ Current output: ❌ Shows equity only
  ├─ Should route to: quarterly_ratios
  ├─ Should use source: fact_ratios
  ├─ Should use column: debt_to_equity
  └─ Status: ❌ Routing issue
```

---

## 🔍 **WHY ROUTING ISSUE EXISTS**

### **Template Selection Priority:**

When user asks: `"show Apple debt to equity for Q2 2023"`

**Current behavior:**
1. Decomposer sees: "Apple" (company) + "Q2 2023" (quarterly) + "debt to equity" (metric)
2. Looks for matching template
3. Finds `quarter_snapshot`: ✅ Has "quarterly" keywords
4. Finds `quarterly_ratios`: ✅ Has "debt-to-equity" keywords
5. Selects: `quarter_snapshot` (more generic, selected first)
6. Result: ❌ Returns equity value, not debt-to-equity ratio

**Desired behavior:**
1. Same decomposition
2. Should prioritize `quarterly_ratios` for "debt" and "intensity" keywords
3. Should select: `quarterly_ratios`
4. Result: ✅ Returns debt-to-equity ratio

---

## 📋 **SUMMARY**

### **Data Availability:**
| Source | Ratios Available | Status |
|--------|------------------|--------|
| `mv_ratios_annual` | 9/9 | ✅ All working |
| `fact_financials` (calc) | 5/9 | ✅ Working |
| `fact_ratios` | 9/9 | ⚠️ Data exists, routing issue |
| `mv_ratios_ttm` | 5/9 | ⏸️ Available (recreated) |

### **Template Coverage:**
| Template | Purpose | Status |
|----------|---------|--------|
| `annual_metrics` | Annual ratios | ✅ Working |
| `quarter_snapshot` | Quarterly financials + calculated ratios | ✅ Working |
| `quarterly_ratios` | Quarterly pre-calculated ratios | ⚠️ Not routing |
| `ttm_snapshot` | TTM ratios | ⏸️ Available |

### **Overall:**
- **All data infrastructure in place** ✅
- **12/18 queries working perfectly** ✅
- **6/18 queries need routing refinement** ⚠️
- **No missing data** ✅
