-- ============================================================================
-- Migration: Add eps_annual to mv_financials_annual
-- ============================================================================
-- Purpose: Add calculated column that SUMS quarterly EPS for each year
-- Annual EPS = Sum of all quarterly EPS (not average!)
-- 
-- Run this in Supabase SQL Editor
-- ============================================================================

-- Step 1: Drop the existing materialized view
DROP MATERIALIZED VIEW IF EXISTS mv_financials_annual CASCADE;

-- Step 2: Recreate with eps_annual column
CREATE MATERIALIZED VIEW mv_financials_annual AS
SELECT
    company_id,
    fiscal_year,
    
    -- Revenue
    SUM(revenue) AS revenue_annual,
    
    -- Income Statement
    SUM(net_income) AS net_income_annual,
    SUM(operating_income) AS operating_income_annual,
    SUM(gross_profit) AS gross_profit_annual,
    
    -- Expenses
    SUM(r_and_d_expenses) AS r_and_d_expenses_annual,
    SUM(sg_and_a_expenses) AS sgna_annual,
    SUM(cogs) AS cogs_annual,
    
    -- Per-Share Metrics (SUM of quarterly EPS - THIS IS NEW!)
    SUM(eps) AS eps_annual,
    
    -- Balance Sheet (End of Year - take Q4 or latest available)
    MAX(CASE WHEN fiscal_quarter = 4 THEN total_assets ELSE NULL END) AS total_assets_eoy,
    MAX(CASE WHEN fiscal_quarter = 4 THEN total_liabilities ELSE NULL END) AS total_liabilities_eoy,
    MAX(CASE WHEN fiscal_quarter = 4 THEN equity ELSE NULL END) AS equity_eoy,
    
    -- Cash Flow (sum across year)
    SUM(cash_flow_ops) AS cash_flow_ops_annual,
    SUM(cash_flow_investing) AS cash_flow_investing_annual,
    SUM(cash_flow_financing) AS cash_flow_financing_annual,
    SUM(capex) AS capex_annual,
    
    -- Shareholder Actions
    SUM(dividends) AS dividends_annual,
    SUM(buybacks) AS buybacks_annual,
    
    -- Metadata
    COUNT(*) AS quarter_count,
    MAX(version_ts) AS latest_version_ts
FROM fact_financials
GROUP BY company_id, fiscal_year
ORDER BY company_id, fiscal_year;

-- Step 3: Create indexes for performance
CREATE INDEX idx_mv_financials_annual_company ON mv_financials_annual(company_id);
CREATE INDEX idx_mv_financials_annual_year ON mv_financials_annual(fiscal_year);
CREATE INDEX idx_mv_financials_annual_company_year ON mv_financials_annual(company_id, fiscal_year);

-- Step 4: Grant permissions
GRANT SELECT ON mv_financials_annual TO anon, authenticated;

-- Step 5: Verify the data (optional - check results)
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
