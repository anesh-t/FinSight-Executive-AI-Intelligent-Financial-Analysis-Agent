-- ============================================================================
-- CREATE COMBINED ANNUAL VIEWS - LAYERED APPROACH (MATERIALIZED)
-- Run this in your database admin tool (pgAdmin, psql, etc.)
-- ============================================================================
-- Purpose: Create 3 layers of combined annual views as MATERIALIZED VIEWS
--   Layer 1: Core Company (Financials + Ratios + Stock)
--   Layer 2: With Macro Context (Layer 1 + Macro Indicators)
--   Layer 3: Full Picture (Layer 2 + Sensitivity Betas)
-- Note: Annual views are MATERIALIZED for performance (pre-computed)
-- ============================================================================

-- ============================================================================
-- LAYER 1: CORE COMPANY VIEW (Annual)
-- ============================================================================
-- Combines: Financials + Ratios + Stock Prices (annual aggregates)
-- Use: Comprehensive annual company snapshot without macro context

DROP MATERIALIZED VIEW IF EXISTS mv_company_complete_annual CASCADE;

CREATE MATERIALIZED VIEW mv_company_complete_annual AS
SELECT 
    -- ========================================
    -- IDENTIFIERS
    -- ========================================
    c.company_id,
    c.ticker,
    c.name,
    fa.fiscal_year,
    
    -- ========================================
    -- FINANCIALS - ANNUAL (19 metrics)
    -- ========================================
    -- Revenue & Income (annual totals)
    fa.revenue_annual,
    fa.gross_profit_annual,
    fa.operating_income_annual,
    fa.net_income_annual,
    fa.ebitda_annual,
    fa.eps_diluted_annual,
    
    -- Expenses (annual totals)
    fa.rd_expenses_annual,
    fa.sga_expenses_annual,
    fa.cogs_annual,
    
    -- Balance Sheet (Q4 values)
    fa.total_assets_q4,
    fa.total_liabilities_q4,
    fa.total_equity_q4,
    fa.total_debt_q4,
    fa.cash_and_equiv_q4,
    
    -- Cash Flow (annual totals)
    fa.operating_cf_annual,
    fa.investing_cf_annual,
    fa.financing_cf_annual,
    fa.capex_annual,
    fa.dividends_paid_annual,
    
    -- ========================================
    -- RATIOS - ANNUAL (9 ratios)
    -- ========================================
    ra.gross_margin_annual,
    ra.operating_margin_annual,
    ra.net_margin_annual,
    ra.roe_annual,
    ra.roa_annual,
    ra.debt_to_equity_q4,
    ra.debt_to_assets_q4,
    ra.rd_intensity_annual,
    ra.sga_intensity_annual,
    
    -- ========================================
    -- STOCK PRICES - ANNUAL (16 metrics)
    -- ========================================
    sa.avg_price_annual,
    sa.avg_open_price_annual,
    sa.avg_close_price_annual,
    sa.high_price_annual,
    sa.low_price_annual,
    sa.close_price_eoy,
    sa.return_annual,
    sa.volatility_pct_annual,
    sa.volume_total_annual,
    sa.volume_avg_annual,
    sa.dividend_per_share_annual,
    sa.dividend_yield_annual,
    sa.shares_outstanding_eoy,
    sa.market_cap_eoy,
    sa.buyback_amount_annual,
    sa.price_change_annual

FROM mv_financials_annual fa
JOIN dim_company c USING (company_id)
LEFT JOIN mv_ratios_annual ra 
    ON fa.company_id = ra.company_id 
    AND fa.fiscal_year = ra.fiscal_year
LEFT JOIN mv_stock_prices_annual sa 
    ON fa.company_id = sa.company_id 
    AND fa.fiscal_year = sa.fiscal_year;

-- Create indexes for performance
CREATE INDEX idx_mv_company_complete_annual_company ON mv_company_complete_annual(company_id);
CREATE INDEX idx_mv_company_complete_annual_year ON mv_company_complete_annual(fiscal_year);
CREATE INDEX idx_mv_company_complete_annual_ticker ON mv_company_complete_annual(ticker);
CREATE INDEX idx_mv_company_complete_annual_company_year ON mv_company_complete_annual(company_id, fiscal_year);

COMMENT ON MATERIALIZED VIEW mv_company_complete_annual IS 'Layer 1: Core company annual data (Financials + Ratios + Stock) - ~44 metrics';

-- Refresh the view
REFRESH MATERIALIZED VIEW mv_company_complete_annual;


-- ============================================================================
-- LAYER 2: WITH MACRO CONTEXT (Annual)
-- ============================================================================
-- Adds: Macro Indicators to Layer 1
-- Use: Company performance with economic context

DROP MATERIALIZED VIEW IF EXISTS mv_company_macro_context_annual CASCADE;

CREATE MATERIALIZED VIEW mv_company_macro_context_annual AS
SELECT 
    -- ========================================
    -- ALL FROM LAYER 1 (Core Company)
    -- ========================================
    cc.*,
    
    -- ========================================
    -- MACRO INDICATORS - ANNUAL (10 indicators)
    -- ========================================
    ma.gdp_annual,
    ma.pce_annual,
    ma.cpi_annual,
    ma.core_cpi_annual,
    ma.pce_price_index_annual,
    ma.unemployment_rate_annual,
    ma.fed_funds_rate_annual,
    ma.term_spread_10y_2y_annual,
    ma.sp500_index_annual,
    ma.vix_index_annual

FROM mv_company_complete_annual cc
LEFT JOIN mv_macro_annual ma 
    ON cc.fiscal_year = ma.fiscal_year;

-- Create indexes for performance
CREATE INDEX idx_mv_company_macro_annual_company ON mv_company_macro_context_annual(company_id);
CREATE INDEX idx_mv_company_macro_annual_year ON mv_company_macro_context_annual(fiscal_year);
CREATE INDEX idx_mv_company_macro_annual_ticker ON mv_company_macro_context_annual(ticker);

COMMENT ON MATERIALIZED VIEW mv_company_macro_context_annual IS 'Layer 2: Company annual data with macro context (~54 metrics)';

-- Refresh the view
REFRESH MATERIALIZED VIEW mv_company_macro_context_annual;


-- ============================================================================
-- LAYER 3: FULL PICTURE (Annual)
-- ============================================================================
-- Adds: Macro Sensitivity Betas to Layer 2
-- Use: Complete picture including macro responsiveness

DROP MATERIALIZED VIEW IF EXISTS mv_company_full_annual CASCADE;

CREATE MATERIALIZED VIEW mv_company_full_annual AS
SELECT 
    -- ========================================
    -- ALL FROM LAYER 2 (Company + Macro)
    -- ========================================
    cmc.*,
    
    -- ========================================
    -- MACRO SENSITIVITY - ANNUAL (18 betas)
    -- ========================================
    -- Margins (annual averages from sensitivity view)
    msa.gross_margin_annual as gross_margin_sensitivity_annual,
    msa.operating_margin_annual as operating_margin_sensitivity_annual,
    msa.net_margin_annual as net_margin_sensitivity_annual,
    
    -- Macro values (annual averages from sensitivity view)
    msa.cpi_annual as cpi_sensitivity_annual,
    msa.fed_funds_rate_annual as fed_funds_rate_sensitivity_annual,
    msa.sp500_index_annual as sp500_index_sensitivity_annual,
    msa.unemployment_rate_annual as unemployment_rate_sensitivity_annual,
    
    -- Beta coefficients (annual averages)
    msa.beta_gm_cpi_annual,
    msa.beta_om_cpi_annual,
    msa.beta_nm_cpi_annual,
    msa.beta_gm_ffr_annual,
    msa.beta_om_ffr_annual,
    msa.beta_nm_ffr_annual,
    msa.beta_nm_spx_annual,
    msa.beta_nm_unrate_annual

FROM mv_company_macro_context_annual cmc
LEFT JOIN mv_macro_sensitivity_annual msa 
    ON cmc.company_id = msa.company_id 
    AND cmc.fiscal_year = msa.fiscal_year;

-- Create indexes for performance
CREATE INDEX idx_mv_company_full_annual_company ON mv_company_full_annual(company_id);
CREATE INDEX idx_mv_company_full_annual_year ON mv_company_full_annual(fiscal_year);
CREATE INDEX idx_mv_company_full_annual_ticker ON mv_company_full_annual(ticker);

COMMENT ON MATERIALIZED VIEW mv_company_full_annual IS 'Layer 3: Complete annual picture with sensitivity (~72 metrics)';

-- Refresh the view
REFRESH MATERIALIZED VIEW mv_company_full_annual;


-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check Layer 1: Core Company
SELECT 
    'Layer 1 (Core - Annual)' as layer,
    COUNT(*) as total_records,
    COUNT(DISTINCT company_id) as num_companies,
    MIN(fiscal_year) as earliest_year,
    MAX(fiscal_year) as latest_year,
    COUNT(CASE WHEN revenue_annual IS NOT NULL THEN 1 END) as has_financials,
    COUNT(CASE WHEN gross_margin_annual IS NOT NULL THEN 1 END) as has_ratios,
    COUNT(CASE WHEN avg_price_annual IS NOT NULL THEN 1 END) as has_stock
FROM mv_company_complete_annual;

-- Check Layer 2: With Macro
SELECT 
    'Layer 2 (Macro Context - Annual)' as layer,
    COUNT(*) as total_records,
    COUNT(CASE WHEN gdp_annual IS NOT NULL THEN 1 END) as has_macro
FROM mv_company_macro_context_annual;

-- Check Layer 3: Full Picture
SELECT 
    'Layer 3 (Full - Annual)' as layer,
    COUNT(*) as total_records,
    COUNT(CASE WHEN beta_nm_cpi_annual IS NOT NULL THEN 1 END) as has_sensitivity
FROM mv_company_full_annual;

-- Sample data from Layer 3 (full picture)
SELECT 
    ticker,
    fiscal_year,
    -- Financials
    ROUND(revenue_annual/1e9, 2) as revenue_b,
    -- Ratios
    ROUND(net_margin_annual::numeric, 4) as net_margin,
    -- Stock
    ROUND(avg_price_annual::numeric, 2) as stock_price,
    ROUND(return_annual::numeric, 4) as annual_return,
    -- Macro
    ROUND(gdp_annual/1e3, 2) as gdp_t,
    ROUND(cpi_annual::numeric, 2) as cpi,
    -- Sensitivity
    ROUND(beta_nm_cpi_annual::numeric, 6) as beta_nm_cpi
FROM mv_company_full_annual
WHERE fiscal_year = 2023
ORDER BY ticker
LIMIT 5;

-- Compare view sizes
SELECT 
    'mv_company_complete_annual' as view_name,
    pg_size_pretty(pg_total_relation_size('mv_company_complete_annual')) as size
UNION ALL
SELECT 
    'mv_company_macro_context_annual',
    pg_size_pretty(pg_total_relation_size('mv_company_macro_context_annual'))
UNION ALL
SELECT 
    'mv_company_full_annual',
    pg_size_pretty(pg_total_relation_size('mv_company_full_annual'));


-- ============================================================================
-- USAGE EXAMPLES FOR CFO AGENT
-- ============================================================================

/*

LAYER 1 QUERIES (Core Company - Annual):
-----------------------------------------
"show Apple complete picture 2023"
"give me everything about Microsoft 2023"
"comprehensive annual view of Google 2023"

SELECT * FROM mv_company_complete_annual 
WHERE ticker = 'AAPL' AND fiscal_year = 2023;


LAYER 2 QUERIES (With Macro Context - Annual):
-----------------------------------------------
"show Apple with economic context 2023"
"Microsoft annual performance with macro 2023"
"Google results with inflation context 2023"

SELECT * FROM mv_company_macro_context_annual 
WHERE ticker = 'MSFT' AND fiscal_year = 2023;


LAYER 3 QUERIES (Full Picture - Annual):
-----------------------------------------
"show Apple full analysis 2023"
"everything about Amazon with sensitivity 2023"
"complete picture including betas for Meta 2023"

SELECT * FROM mv_company_full_annual 
WHERE ticker = 'AMZN' AND fiscal_year = 2023;

*/


-- ============================================================================
-- REFRESH SCHEDULE (Optional - for automated refresh)
-- ============================================================================

/*
-- Add to cron or PostgreSQL scheduled job:
-- Refresh daily at 2 AM

REFRESH MATERIALIZED VIEW CONCURRENTLY mv_company_complete_annual;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_company_macro_context_annual;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_company_full_annual;
*/
