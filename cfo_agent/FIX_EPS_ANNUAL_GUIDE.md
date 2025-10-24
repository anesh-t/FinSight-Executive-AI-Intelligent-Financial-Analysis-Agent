# 🔧 Fix: Annual EPS Should Be SUM, Not Average

## ❌ **The Problem:**

**Before:**
- Annual EPS was calculated as `AVG(quarterly_eps)` 
- Example: Microsoft 2023
  - Q1: $2.45, Q2: $2.69, Q3: $2.99, Q4: $2.93
  - **Wrong calculation:** AVG = $2.76
  - **Correct calculation:** SUM = $11.06

**Why it's wrong:**
- Annual EPS should represent total earnings per share for the entire year
- Averaging dilutes the true earnings power
- Industry standard is to **sum** quarterly EPS values

---

## ✅ **The Solution:**

### **Step 1: Update Database Schema**

Add `eps_annual` column to `mv_financials_annual` materialized view that **sums** quarterly EPS.

**Location:** `/migrations/add_eps_annual.sql`

**What it does:**
```sql
-- Before: eps was not in mv_financials_annual at all
-- After: eps_annual = SUM of all quarterly EPS

SUM(eps) AS eps_annual
```

### **Step 2: Run Migration in Supabase**

**Instructions:**

1. Go to your Supabase project
2. Open **SQL Editor**
3. Copy and paste the contents of `/migrations/add_eps_annual.sql`
4. Click **Run**

**The migration will:**
1. ✅ Drop old `mv_financials_annual` view
2. ✅ Create new view with `eps_annual` column
3. ✅ Sum quarterly EPS values for each year
4. ✅ Create performance indexes
5. ✅ Grant necessary permissions

---

### **Step 3: Update SQL Template** ✅ **ALREADY DONE**

**File:** `catalog/templates.json`

**Change:**
```json
// OLD (was calculating AVG on the fly):
"AVG(f.eps) as eps"

// NEW (uses pre-calculated SUM from view):
"mv.eps_annual as eps"
```

**Also simplified the query:**
- Removed complex JOIN with fact_financials for aggregation
- Now directly reads from mv_financials_annual
- Cash flow and eps_annual are pre-calculated in the view

---

## 📊 **Verification:**

### **Expected Results After Migration:**

**Microsoft 2023:**
| Quarter | EPS |
|---------|-----|
| Q1 | $2.45 |
| Q2 | $2.69 |
| Q3 | $2.99 |
| Q4 | $2.93 |
| **Annual (SUM)** | **$11.06** |

**Before fix:** Agent would return $2.76 (average)
**After fix:** Agent will return $11.06 (sum)

---

## 🚀 **Migration Steps (Run in Supabase SQL Editor):**

```sql
-- Step 1: Drop existing view
DROP MATERIALIZED VIEW IF EXISTS mv_financials_annual CASCADE;

-- Step 2: Create with eps_annual
CREATE MATERIALIZED VIEW mv_financials_annual AS
SELECT
    company_id,
    fiscal_year,
    SUM(revenue) AS revenue_annual,
    SUM(net_income) AS net_income_annual,
    SUM(operating_income) AS operating_income_annual,
    SUM(gross_profit) AS gross_profit_annual,
    SUM(r_and_d_expenses) AS r_and_d_expenses_annual,
    SUM(sg_and_a_expenses) AS sgna_annual,
    SUM(cogs) AS cogs_annual,
    SUM(eps) AS eps_annual,  -- THIS IS THE KEY FIX
    SUM(cash_flow_ops) AS cash_flow_ops_annual,
    SUM(cash_flow_investing) AS cash_flow_investing_annual,
    SUM(cash_flow_financing) AS cash_flow_financing_annual,
    SUM(capex) AS capex_annual,
    SUM(dividends) AS dividends_annual,
    SUM(buybacks) AS buybacks_annual,
    MAX(CASE WHEN fiscal_quarter = 4 THEN total_assets ELSE NULL END) AS total_assets_eoy,
    MAX(CASE WHEN fiscal_quarter = 4 THEN total_liabilities ELSE NULL END) AS total_liabilities_eoy,
    MAX(CASE WHEN fiscal_quarter = 4 THEN equity ELSE NULL END) AS equity_eoy,
    COUNT(*) AS quarter_count,
    MAX(version_ts) AS latest_version_ts
FROM fact_financials
GROUP BY company_id, fiscal_year
ORDER BY company_id, fiscal_year;

-- Step 3: Create indexes
CREATE INDEX idx_mv_financials_annual_company ON mv_financials_annual(company_id);
CREATE INDEX idx_mv_financials_annual_year ON mv_financials_annual(fiscal_year);
CREATE INDEX idx_mv_financials_annual_company_year ON mv_financials_annual(company_id, fiscal_year);

-- Step 4: Grant permissions
GRANT SELECT ON mv_financials_annual TO anon, authenticated;

-- Step 5: Verify
SELECT 
    c.ticker,
    mv.fiscal_year,
    mv.eps_annual,
    mv.quarter_count
FROM mv_financials_annual mv
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'MSFT'
ORDER BY mv.fiscal_year DESC
LIMIT 5;
```

---

## 🔍 **What Changed:**

### **Before:**
```sql
-- Template was doing complex aggregation on-the-fly
SELECT 
    AVG(f.eps) as eps  -- WRONG: Takes average
FROM mv_financials_annual mv
LEFT JOIN fact_financials f ...
GROUP BY ...
```

### **After:**
```sql
-- Template now reads pre-calculated value
SELECT 
    mv.eps_annual as eps  -- CORRECT: Uses summed value
FROM mv_financials_annual mv
...
-- No need for JOIN or GROUP BY!
```

---

## 📋 **Checklist:**

- [x] Created migration SQL file
- [x] Updated SQL template to use `eps_annual`
- [x] Simplified query (removed complex joins)
- [ ] **TODO: Run migration in Supabase SQL Editor**
- [ ] **TODO: Restart app.py and streamlit_app.py**
- [ ] **TODO: Test query: "show microsoft eps for 2023"**
- [ ] **TODO: Verify it returns $11.06 (not $2.76)**

---

## 🧪 **Test Queries After Migration:**

```bash
# Test annual EPS
"show microsoft eps for 2023"
Expected: "Microsoft reported EPS of $11.06 for FY2023"

"show apple eps for 2023"  
Expected: "Apple reported EPS of $6.43 for FY2023"

"show google eps for 2023"
Expected: "Google reported EPS of $5.81 for FY2023"

# Test quarterly EPS (should be unchanged)
"show microsoft eps for Q2 2023"
Expected: "Microsoft reported EPS of $2.69 for Q2 FY2023"
```

---

## 📊 **Expected Annual EPS Values (SUM):**

| Company | 2023 Annual EPS (Correct) |
|---------|---------------------------|
| **MSFT** | $11.06 |
| **AAPL** | $6.43 |
| **GOOG** | $5.81 |
| **AMZN** | $2.89 |
| **META** | $14.90 |

---

## 🎯 **Summary:**

1. ✅ Migration file created: `/migrations/add_eps_annual.sql`
2. ✅ SQL template updated: `catalog/templates.json`
3. ⏳ **Next step:** Run migration in Supabase SQL Editor
4. ⏳ **Then:** Restart services and test

**After migration, annual EPS will correctly show SUM of quarterly values!**
