-- ============================================================================
-- CREATE COMBINED QUARTERLY VIEWS - LAYERED APPROACH
-- Run this in your database admin tool (pgAdmin, psql, etc.)
-- ============================================================================
-- Purpose: Create 3 layers of combined quarterly views
--   Layer 1: Core Company (Financials + Ratios + Stock)
--   Layer 2: With Macro Context (Layer 1 + Macro Indicators)
--   Layer 3: Full Picture (Layer 2 + Sensitivity Betas)
-- ============================================================================

-- ============================================================================
-- LAYER 1: CORE COMPANY VIEW (Quarterly)
-- ============================================================================
-- Combines: Financials + Ratios + Stock Prices
-- Use: Comprehensive company snapshot without macro context

DROP VIEW IF EXISTS vw_company_complete_quarter CASCADE;

CREATE VIEW vw_company_complete_quarter AS
SELECT 
    -- ========================================
    -- IDENTIFIERS
    -- ========================================
    c.company_id,
    c.ticker,
    c.name,
    f.fiscal_year,
    f.fiscal_quarter,
    
    -- ========================================
    -- FINANCIALS (19 metrics)
    -- ========================================
    -- Revenue & Income
    f.revenue,
    f.gross_profit,
    f.operating_income,
    f.net_income,
    f.ebitda,
    f.eps_diluted,
    
    -- Expenses
    f.rd_expenses,
    f.sga_expenses,
    f.cogs,
    
    -- Balance Sheet
    f.total_assets,
    f.total_liabilities,
    f.total_equity,
    f.total_debt,
    f.cash_and_equiv,
    
    -- Cash Flow
    f.operating_cf,
    f.investing_cf,
    f.financing_cf,
    f.capex,
    f.dividends_paid,
    
    -- ========================================
    -- RATIOS (9 ratios)
    -- ========================================
    r.gross_margin,
    r.operating_margin,
    r.net_margin,
    r.roe,
    r.roa,
    r.debt_to_equity,
    r.debt_to_assets,
    r.rd_intensity,
    r.sga_intensity,
    
    -- ========================================
    -- STOCK PRICES (16 metrics)
    -- ========================================
    sp.avg_price_quarter,
    sp.avg_open_price_quarter,
    sp.avg_close_price_quarter,
    sp.high_price_quarter,
    sp.low_price_quarter,
    sp.close_price_eoq,
    sp.return_qoq,
    sp.return_yoy,
    sp.volatility_pct_quarter,
    sp.volume_total_quarter,
    sp.volume_avg_quarter,
    sp.dividend_per_share_quarter,
    sp.dividend_yield_quarter,
    sp.shares_outstanding,
    sp.market_cap_eoq,
    sp.buyback_amount

FROM fact_financials f
JOIN dim_company c USING (company_id)
LEFT JOIN vw_ratios_quarter r 
    ON f.company_id = r.company_id 
    AND f.fiscal_year = r.fiscal_year 
    AND f.fiscal_quarter = r.fiscal_quarter
LEFT JOIN vw_stock_prices_quarter sp 
    ON f.company_id = sp.company_id 
    AND f.fiscal_year = sp.fiscal_year 
    AND f.fiscal_quarter = sp.fiscal_quarter
WHERE f.fiscal_quarter IS NOT NULL;

COMMENT ON VIEW vw_company_complete_quarter IS 'Layer 1: Core company quarterly data (Financials + Ratios + Stock) - ~44 metrics';


-- ============================================================================
-- LAYER 2: WITH MACRO CONTEXT (Quarterly)
-- ============================================================================
-- Adds: Macro Indicators to Layer 1
-- Use: Company performance with economic context

DROP VIEW IF EXISTS vw_company_macro_context_quarter CASCADE;

CREATE VIEW vw_company_macro_context_quarter AS
SELECT 
    -- ========================================
    -- ALL FROM LAYER 1 (Core Company)
    -- ========================================
    cc.*,
    
    -- ========================================
    -- MACRO INDICATORS (10 indicators)
    -- ========================================
    m.gdp,
    m.pce,
    m.cpi,
    m.core_cpi,
    m.pce_price_index,
    m.unemployment_rate,
    m.fed_funds_rate,
    m.term_spread_10y_2y,
    m.sp500_index,
    m.vix_index

FROM vw_company_complete_quarter cc
LEFT JOIN vw_macro_quarter m 
    ON cc.fiscal_year = m.fiscal_year 
    AND cc.fiscal_quarter = m.fiscal_quarter;

COMMENT ON VIEW vw_company_macro_context_quarter IS 'Layer 2: Company quarterly data with macro context (~54 metrics)';


-- ============================================================================
-- LAYER 3: FULL PICTURE (Quarterly)
-- ============================================================================
-- Adds: Macro Sensitivity Betas to Layer 2
-- Use: Complete picture including macro responsiveness

DROP VIEW IF EXISTS vw_company_full_quarter CASCADE;

CREATE VIEW vw_company_full_quarter AS
SELECT 
    -- ========================================
    -- ALL FROM LAYER 2 (Company + Macro)
    -- ========================================
    cmc.*,
    
    -- ========================================
    -- MACRO SENSITIVITY (18 betas)
    -- ========================================
    -- Margins (from sensitivity view, will be same as ratios)
    ms.gross_margin as gross_margin_sensitivity,
    ms.operating_margin as operating_margin_sensitivity,
    ms.net_margin as net_margin_sensitivity,
    
    -- Macro values at time (from sensitivity view)
    ms.cpi as cpi_sensitivity,
    ms.fed_funds_rate as fed_funds_rate_sensitivity,
    ms.sp500_index as sp500_index_sensitivity,
    ms.unemployment_rate as unemployment_rate_sensitivity,
    
    -- Beta coefficients (12Q rolling)
    ms.beta_gm_cpi_12q,
    ms.beta_om_cpi_12q,
    ms.beta_nm_cpi_12q,
    ms.beta_gm_ffr_12q,
    ms.beta_om_ffr_12q,
    ms.beta_nm_ffr_12q,
    ms.beta_nm_spx_12q,
    ms.beta_nm_unrate_12q

FROM vw_company_macro_context_quarter cmc
LEFT JOIN vw_macro_sensitivity_rolling ms 
    ON cmc.company_id = ms.company_id 
    AND cmc.fiscal_year = ms.fiscal_year 
    AND cmc.fiscal_quarter = ms.fiscal_quarter;

COMMENT ON VIEW vw_company_full_quarter IS 'Layer 3: Complete quarterly picture with sensitivity (~72 metrics)';


-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check Layer 1: Core Company
SELECT 
    'Layer 1 (Core)' as layer,
    COUNT(*) as total_records,
    COUNT(DISTINCT company_id) as num_companies,
    MIN(fiscal_year) as earliest_year,
    MAX(fiscal_year) as latest_year,
    COUNT(CASE WHEN revenue IS NOT NULL THEN 1 END) as has_financials,
    COUNT(CASE WHEN gross_margin IS NOT NULL THEN 1 END) as has_ratios,
    COUNT(CASE WHEN avg_price_quarter IS NOT NULL THEN 1 END) as has_stock
FROM vw_company_complete_quarter;

-- Check Layer 2: With Macro
SELECT 
    'Layer 2 (Macro Context)' as layer,
    COUNT(*) as total_records,
    COUNT(CASE WHEN gdp IS NOT NULL THEN 1 END) as has_macro
FROM vw_company_macro_context_quarter;

-- Check Layer 3: Full Picture
SELECT 
    'Layer 3 (Full)' as layer,
    COUNT(*) as total_records,
    COUNT(CASE WHEN beta_nm_cpi_12q IS NOT NULL THEN 1 END) as has_sensitivity
FROM vw_company_full_quarter;

-- Sample data from Layer 3 (full picture)
SELECT 
    ticker,
    fiscal_year,
    fiscal_quarter,
    -- Financials
    ROUND(revenue/1e9, 2) as revenue_b,
    -- Ratios
    ROUND(net_margin::numeric, 4) as net_margin,
    -- Stock
    ROUND(avg_price_quarter::numeric, 2) as stock_price,
    -- Macro
    ROUND(gdp/1e3, 2) as gdp_t,
    ROUND(cpi::numeric, 2) as cpi,
    -- Sensitivity
    ROUND(beta_nm_cpi_12q::numeric, 6) as beta_nm_cpi
FROM vw_company_full_quarter
WHERE fiscal_year = 2023 AND fiscal_quarter = 2
ORDER BY ticker
LIMIT 5;


-- ============================================================================
-- USAGE EXAMPLES FOR CFO AGENT
-- ============================================================================

/*

LAYER 1 QUERIES (Core Company):
--------------------------------
"show Apple complete picture Q2 2023"
"give me everything about Microsoft Q3 2023"
"comprehensive view of Google Q2 2023"

SELECT * FROM vw_company_complete_quarter 
WHERE ticker = 'AAPL' AND fiscal_year = 2023 AND fiscal_quarter = 2;


LAYER 2 QUERIES (With Macro Context):
--------------------------------------
"show Apple with economic context Q2 2023"
"Microsoft performance with macro Q3 2023"
"Google results with inflation context Q2 2023"

SELECT * FROM vw_company_macro_context_quarter 
WHERE ticker = 'MSFT' AND fiscal_year = 2023 AND fiscal_quarter = 3;


LAYER 3 QUERIES (Full Picture):
--------------------------------
"show Apple full analysis Q2 2023"
"everything about Amazon with sensitivity Q3 2023"
"complete picture including betas for Meta Q2 2023"

SELECT * FROM vw_company_full_quarter 
WHERE ticker = 'AMZN' AND fiscal_year = 2023 AND fiscal_quarter = 3;

*/
