-- ============================================================================
-- CREATE MACRO SENSITIVITY ANNUAL VIEW
-- Run this in your database admin tool (pgAdmin, psql, etc.)
-- ============================================================================
-- Purpose: Create annual aggregated view for macro sensitivity (betas)
--          to match the pattern used for financials, stock prices, and macro indicators
-- ============================================================================

-- ----------------------------------------------------------------------------
-- ANNUAL MACRO SENSITIVITY MATERIALIZED VIEW
-- ----------------------------------------------------------------------------
-- Aggregate quarterly macro sensitivity data to annual averages
-- Betas show how company margins respond to macro indicator changes
-- (e.g., how net margin changes with 1% change in CPI)

DROP MATERIALIZED VIEW IF EXISTS mv_macro_sensitivity_annual CASCADE;

CREATE MATERIALIZED VIEW mv_macro_sensitivity_annual AS
SELECT 
    company_id,
    fiscal_year,
    
    -- Average margins for the year
    AVG(gross_margin) as gross_margin_annual,
    AVG(operating_margin) as operating_margin_annual,
    AVG(net_margin) as net_margin_annual,
    
    -- Average macro indicators for the year
    AVG(cpi) as cpi_annual,
    AVG(fed_funds_rate) as fed_funds_rate_annual,
    AVG(sp500_index) as sp500_index_annual,
    AVG(unemployment_rate) as unemployment_rate_annual,
    
    -- Annual average betas (margin sensitivity to CPI)
    AVG(beta_gm_cpi_12q) as beta_gm_cpi_annual,
    AVG(beta_om_cpi_12q) as beta_om_cpi_annual,
    AVG(beta_nm_cpi_12q) as beta_nm_cpi_annual,
    
    -- Annual average betas (margin sensitivity to Fed Funds Rate)
    AVG(beta_gm_ffr_12q) as beta_gm_ffr_annual,
    AVG(beta_om_ffr_12q) as beta_om_ffr_annual,
    AVG(beta_nm_ffr_12q) as beta_nm_ffr_annual,
    
    -- Annual average betas (net margin sensitivity to other indicators)
    AVG(beta_nm_spx_12q) as beta_nm_spx_annual,
    AVG(beta_nm_unrate_12q) as beta_nm_unrate_annual,
    
    -- Q4 values (year-end snapshot)
    MAX(CASE WHEN fiscal_quarter = 4 THEN gross_margin END) as gross_margin_q4,
    MAX(CASE WHEN fiscal_quarter = 4 THEN operating_margin END) as operating_margin_q4,
    MAX(CASE WHEN fiscal_quarter = 4 THEN net_margin END) as net_margin_q4
    
FROM vw_macro_sensitivity_rolling
GROUP BY company_id, fiscal_year;

-- Create indexes for performance
CREATE INDEX idx_mv_sensitivity_annual_company ON mv_macro_sensitivity_annual(company_id);
CREATE INDEX idx_mv_sensitivity_annual_year ON mv_macro_sensitivity_annual(fiscal_year);
CREATE INDEX idx_mv_sensitivity_annual_company_year ON mv_macro_sensitivity_annual(company_id, fiscal_year);

COMMENT ON MATERIALIZED VIEW mv_macro_sensitivity_annual IS 'Annual macro sensitivity data (betas) aggregated from quarterly rolling 12Q betas';

-- Refresh the materialized view
REFRESH MATERIALIZED VIEW mv_macro_sensitivity_annual;


-- ----------------------------------------------------------------------------
-- VERIFICATION QUERIES
-- ----------------------------------------------------------------------------

-- Check view
SELECT 
    'mv_macro_sensitivity_annual' as view_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT company_id) as num_companies,
    MIN(fiscal_year) as earliest_year,
    MAX(fiscal_year) as latest_year,
    COUNT(CASE WHEN beta_nm_cpi_annual IS NOT NULL THEN 1 END) as records_with_betas
FROM mv_macro_sensitivity_annual;

-- Sample data for 2023
SELECT 
    c.ticker,
    sa.fiscal_year,
    ROUND(sa.gross_margin_annual::numeric, 4) as gm_annual,
    ROUND(sa.operating_margin_annual::numeric, 4) as om_annual,
    ROUND(sa.net_margin_annual::numeric, 4) as nm_annual,
    ROUND(sa.beta_gm_cpi_annual::numeric, 6) as beta_gm_cpi,
    ROUND(sa.beta_om_cpi_annual::numeric, 6) as beta_om_cpi,
    ROUND(sa.beta_nm_cpi_annual::numeric, 6) as beta_nm_cpi,
    ROUND(sa.beta_nm_ffr_annual::numeric, 6) as beta_nm_ffr,
    ROUND(sa.beta_nm_spx_annual::numeric, 6) as beta_nm_spx
FROM mv_macro_sensitivity_annual sa
JOIN dim_company c USING (company_id)
WHERE sa.fiscal_year = 2023
ORDER BY c.ticker;


-- ============================================================================
-- USAGE EXAMPLES FOR CFO AGENT
-- ============================================================================

/*

QUARTERLY QUERIES (using existing vw_macro_sensitivity_rolling):
------------------
"show Apple macro sensitivity Q2 2023"
"how does Microsoft margins respond to inflation Q3 2023"
"show Google beta to CPI Q1 2024"

SELECT 
    c.ticker, c.name, s.fiscal_year, s.fiscal_quarter,
    s.gross_margin, s.operating_margin, s.net_margin,
    s.beta_gm_cpi_12q, s.beta_om_cpi_12q, s.beta_nm_cpi_12q,
    s.beta_gm_ffr_12q, s.beta_om_ffr_12q, s.beta_nm_ffr_12q
FROM vw_macro_sensitivity_rolling s
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL' AND s.fiscal_year = 2023 AND s.fiscal_quarter = 2;


ANNUAL QUERIES (using new mv_macro_sensitivity_annual):
---------------
"show Apple macro sensitivity 2023"
"how does Amazon margins respond to inflation in 2023"
"show Meta beta to Fed rate 2024"

SELECT 
    c.ticker, c.name, sa.fiscal_year,
    sa.gross_margin_annual, sa.operating_margin_annual, sa.net_margin_annual,
    sa.beta_gm_cpi_annual, sa.beta_om_cpi_annual, sa.beta_nm_cpi_annual,
    sa.beta_gm_ffr_annual, sa.beta_om_ffr_annual, sa.beta_nm_ffr_annual,
    sa.beta_nm_spx_annual, sa.beta_nm_unrate_annual
FROM mv_macro_sensitivity_annual sa
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL' AND sa.fiscal_year = 2023;

*/
