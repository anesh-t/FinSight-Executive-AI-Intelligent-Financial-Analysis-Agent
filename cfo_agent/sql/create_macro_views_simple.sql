-- ============================================================================
-- CREATE MACRO INDICATOR VIEWS - Quarterly & Annual
-- Run this in your database admin tool (pgAdmin, psql, etc.)
-- ============================================================================
-- Purpose: Create clean quarterly and annual views for macro indicators
--          to match the pattern used for financials and stock prices
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. QUARTERLY MACRO INDICATORS VIEW (Wide Format)
-- ----------------------------------------------------------------------------
-- Pivot the long format into wide format with one row per quarter
-- Each indicator becomes a column (gdp, cpi, unemployment, etc.)

DROP VIEW IF EXISTS vw_macro_quarter CASCADE;

CREATE VIEW vw_macro_quarter AS
SELECT 
    fiscal_year,
    fiscal_quarter,
    
    -- Economic Output
    MAX(CASE WHEN mi.code = 'GDPC1' THEN fm.value END) as gdp,
    MAX(CASE WHEN mi.code = 'PCE' THEN fm.value END) as pce,
    
    -- Inflation
    MAX(CASE WHEN mi.code = 'CPIAUCSL' THEN fm.value END) as cpi,
    MAX(CASE WHEN mi.code = 'CPILFESL' THEN fm.value END) as core_cpi,
    MAX(CASE WHEN mi.code = 'PCEPI' THEN fm.value END) as pce_price_index,
    
    -- Labor Market
    MAX(CASE WHEN mi.code = 'UNRATE' THEN fm.value END) as unemployment_rate,
    
    -- Interest Rates & Yield Curve
    MAX(CASE WHEN mi.code = 'FEDFUNDS' THEN fm.value END) as fed_funds_rate,
    MAX(CASE WHEN mi.code = 'T10Y2Y' THEN fm.value END) as term_spread_10y_2y,
    
    -- Market Indicators
    MAX(CASE WHEN mi.code = 'SP500' THEN fm.value END) as sp500_index,
    MAX(CASE WHEN mi.code = 'VIXCLS' THEN fm.value END) as vix_index,
    
    -- Metadata
    MAX(fm.version_ts) as version_ts
    
FROM fact_macro_indicators fm
JOIN dim_macro_indicator mi USING (indicator_id)
GROUP BY fiscal_year, fiscal_quarter;

COMMENT ON VIEW vw_macro_quarter IS 'Quarterly macro indicators in wide format - mirrors pattern of vw_stock_prices_quarter';


-- ----------------------------------------------------------------------------
-- 2. ANNUAL MACRO INDICATORS MATERIALIZED VIEW
-- ----------------------------------------------------------------------------
-- Aggregate quarterly macro data to annual (fiscal year averages)
-- This mirrors the pattern of mv_financials_annual and mv_stock_prices_annual

DROP MATERIALIZED VIEW IF EXISTS mv_macro_annual CASCADE;

CREATE MATERIALIZED VIEW mv_macro_annual AS
SELECT 
    fiscal_year,
    
    -- Economic Output (annual averages)
    AVG(gdp) as gdp_annual,
    AVG(pce) as pce_annual,
    
    -- Inflation (annual averages)
    AVG(cpi) as cpi_annual,
    AVG(core_cpi) as core_cpi_annual,
    AVG(pce_price_index) as pce_price_index_annual,
    
    -- Labor Market (annual average)
    AVG(unemployment_rate) as unemployment_rate_annual,
    
    -- Interest Rates (annual averages)
    AVG(fed_funds_rate) as fed_funds_rate_annual,
    AVG(term_spread_10y_2y) as term_spread_10y_2y_annual,
    
    -- Market Indicators (annual averages)
    AVG(sp500_index) as sp500_index_annual,
    AVG(vix_index) as vix_index_annual,
    
    -- Year-end values (from Q4)
    MAX(CASE WHEN fiscal_quarter = 4 THEN gdp END) as gdp_q4,
    MAX(CASE WHEN fiscal_quarter = 4 THEN cpi END) as cpi_q4,
    MAX(CASE WHEN fiscal_quarter = 4 THEN unemployment_rate END) as unemployment_rate_q4,
    MAX(CASE WHEN fiscal_quarter = 4 THEN fed_funds_rate END) as fed_funds_rate_q4,
    MAX(CASE WHEN fiscal_quarter = 4 THEN sp500_index END) as sp500_index_q4,
    
    -- Metadata
    MAX(version_ts) as version_ts
    
FROM vw_macro_quarter
GROUP BY fiscal_year;

-- Create indexes for performance
CREATE INDEX idx_mv_macro_annual_year ON mv_macro_annual(fiscal_year);

COMMENT ON MATERIALIZED VIEW mv_macro_annual IS 'Annual macro indicator data aggregated from quarterly - mirrors pattern of mv_ratios_annual';

-- Refresh the materialized view
REFRESH MATERIALIZED VIEW mv_macro_annual;


-- ----------------------------------------------------------------------------
-- 3. VERIFICATION QUERIES
-- ----------------------------------------------------------------------------

-- Check quarterly view
SELECT 
    'vw_macro_quarter' as view_name,
    COUNT(*) as total_records,
    MIN(fiscal_year) as earliest_year,
    MAX(fiscal_year) as latest_year
FROM vw_macro_quarter;

-- Check annual materialized view  
SELECT 
    'mv_macro_annual' as view_name,
    COUNT(*) as total_records,
    MIN(fiscal_year) as earliest_year,
    MAX(fiscal_year) as latest_year
FROM mv_macro_annual;

-- Sample quarterly data
SELECT 
    fiscal_year,
    fiscal_quarter,
    ROUND(gdp::numeric, 2) as gdp,
    ROUND(cpi::numeric, 2) as cpi,
    ROUND(unemployment_rate::numeric, 2) as unemployment,
    ROUND(fed_funds_rate::numeric, 2) as fed_rate
FROM vw_macro_quarter
WHERE fiscal_year = 2023
ORDER BY fiscal_quarter;

-- Sample annual data
SELECT 
    fiscal_year,
    ROUND(gdp_annual::numeric, 2) as gdp_avg,
    ROUND(cpi_annual::numeric, 2) as cpi_avg,
    ROUND(unemployment_rate_annual::numeric, 2) as unemployment_avg,
    ROUND(fed_funds_rate_annual::numeric, 2) as fed_rate_avg
FROM mv_macro_annual
WHERE fiscal_year IN (2022, 2023, 2024)
ORDER BY fiscal_year;


-- ----------------------------------------------------------------------------
-- 4. GRANT PERMISSIONS (if needed)
-- ----------------------------------------------------------------------------

-- Grant SELECT to your application user (adjust role name as needed)
-- GRANT SELECT ON vw_macro_quarter TO your_app_user;
-- GRANT SELECT ON mv_macro_annual TO your_app_user;


-- ============================================================================
-- USAGE EXAMPLES FOR CFO AGENT
-- ============================================================================

/*

QUARTERLY QUERIES:
------------------
"show GDP Q2 2023"
SELECT fiscal_year, fiscal_quarter, gdp
FROM vw_macro_quarter
WHERE fiscal_year = 2023 AND fiscal_quarter = 2;

"show inflation Q3 2023"
SELECT fiscal_year, fiscal_quarter, cpi, core_cpi, pce_price_index
FROM vw_macro_quarter
WHERE fiscal_year = 2023 AND fiscal_quarter = 3;

"show unemployment rate Q2 2023"
SELECT fiscal_year, fiscal_quarter, unemployment_rate
FROM vw_macro_quarter
WHERE fiscal_year = 2023 AND fiscal_quarter = 2;

"show Fed rate Q1 2024"
SELECT fiscal_year, fiscal_quarter, fed_funds_rate
FROM vw_macro_quarter
WHERE fiscal_year = 2024 AND fiscal_quarter = 1;


ANNUAL QUERIES:
---------------
"show GDP 2023"
SELECT fiscal_year, gdp_annual, gdp_q4
FROM mv_macro_annual
WHERE fiscal_year = 2023;

"show inflation 2023"
SELECT fiscal_year, cpi_annual, core_cpi_annual, pce_price_index_annual
FROM mv_macro_annual
WHERE fiscal_year = 2023;

"show unemployment rate 2023"
SELECT fiscal_year, unemployment_rate_annual, unemployment_rate_q4
FROM mv_macro_annual
WHERE fiscal_year = 2023;

"show macro indicators 2023"
SELECT 
    fiscal_year,
    gdp_annual, cpi_annual, unemployment_rate_annual, 
    fed_funds_rate_annual, sp500_index_annual
FROM mv_macro_annual
WHERE fiscal_year = 2023;

*/
