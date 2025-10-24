-- ============================================================================
-- STOCK PRICE VIEWS - QUARTERLY & ANNUAL
-- ============================================================================
-- Purpose: Create clean views for stock price data to match the pattern used
--          for financial data (fact_financials → mv_financials_annual)
-- 
-- Pattern:
--   - Quarterly: vw_stock_prices_quarter (passthrough from fact_stock_prices)
--   - Annual: mv_stock_prices_annual (aggregated materialized view)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. QUARTERLY STOCK PRICES VIEW
-- ----------------------------------------------------------------------------
-- Simple view that provides clean column names and joins with company info
-- This mirrors the pattern of vw_ratios_quarter for financial ratios

DROP VIEW IF EXISTS vw_stock_prices_quarter CASCADE;

CREATE VIEW vw_stock_prices_quarter AS
SELECT 
    -- Identifiers
    sp.company_id,
    sp.fiscal_year,
    sp.fiscal_quarter,
    
    -- Price metrics (quarterly)
    sp.open_price,
    sp.close_price,
    sp.high_price,
    sp.low_price,
    sp.avg_price,                    -- Average price for the quarter
    
    -- Returns
    sp.return_qoq,                   -- Quarter-over-quarter return (%)
    sp.return_yoy,                   -- Year-over-year return (%)
    sp.price_change_abs,             -- Absolute price change in quarter
    sp.price_change_pct,             -- Percentage price change in quarter
    
    -- Trading metrics
    sp.volume_total,                 -- Total volume traded in quarter
    sp.volume_avg,                   -- Average daily volume
    sp.volatility_pct,               -- Quarterly volatility (%)
    
    -- Dividends
    sp.dividend_yield,               -- Dividend yield (%)
    sp.dividend_per_share,           -- Dividend per share ($)
    
    -- Metadata
    sp.version_ts
FROM fact_stock_prices sp;

COMMENT ON VIEW vw_stock_prices_quarter IS 'Quarterly stock price data with clean column names - mirrors pattern of vw_ratios_quarter';


-- ----------------------------------------------------------------------------
-- 2. ANNUAL STOCK PRICES MATERIALIZED VIEW
-- ----------------------------------------------------------------------------
-- Aggregates quarterly stock price data to annual (fiscal year)
-- This mirrors the pattern of mv_financials_annual and mv_ratios_annual

DROP MATERIALIZED VIEW IF EXISTS mv_stock_prices_annual CASCADE;

CREATE MATERIALIZED VIEW mv_stock_prices_annual AS
SELECT 
    -- Identifiers
    company_id,
    fiscal_year,
    
    -- Annual price metrics (averages)
    AVG(open_price) as avg_open_price_annual,
    AVG(close_price) as avg_close_price_annual,
    AVG(avg_price) as avg_price_annual,         -- Average of quarterly averages
    
    -- Year-high and year-low
    MAX(high_price) as high_price_annual,       -- Highest price in the year
    MIN(low_price) as low_price_annual,         -- Lowest price in the year
    
    -- End of year prices (from Q4)
    MAX(CASE WHEN fiscal_quarter = 4 THEN open_price END) as open_price_eoy,
    MAX(CASE WHEN fiscal_quarter = 4 THEN close_price END) as close_price_eoy,
    
    -- Annual return calculation (using EOY close and previous EOY close)
    -- Note: This will be calculated via window function in the next level
    (MAX(CASE WHEN fiscal_quarter = 4 THEN close_price END) - 
     MIN(CASE WHEN fiscal_quarter = 1 THEN open_price END)) / 
     NULLIF(MIN(CASE WHEN fiscal_quarter = 1 THEN open_price END), 0) 
     as return_annual,
    
    -- Annual volatility (average of quarterly volatilities)
    AVG(volatility_pct) as volatility_pct_annual,
    
    -- Annual trading metrics
    SUM(volume_total) as volume_total_annual,   -- Total volume for the year
    AVG(volume_avg) as volume_avg_annual,       -- Average daily volume for year
    
    -- Dividends (total for the year)
    SUM(COALESCE(dividend_per_share, 0)) as dividend_per_share_annual,
    AVG(dividend_yield) as dividend_yield_annual,
    
    -- Metadata
    MAX(version_ts) as version_ts
    
FROM fact_stock_prices
GROUP BY company_id, fiscal_year;

-- Create indexes for performance
CREATE INDEX idx_mv_stock_annual_company ON mv_stock_prices_annual(company_id);
CREATE INDEX idx_mv_stock_annual_year ON mv_stock_prices_annual(fiscal_year);
CREATE INDEX idx_mv_stock_annual_company_year ON mv_stock_prices_annual(company_id, fiscal_year);

COMMENT ON MATERIALIZED VIEW mv_stock_prices_annual IS 'Annual stock price data aggregated from quarterly - mirrors pattern of mv_ratios_annual';

-- Refresh the materialized view
REFRESH MATERIALIZED VIEW mv_stock_prices_annual;


-- ----------------------------------------------------------------------------
-- 3. VERIFICATION QUERIES
-- ----------------------------------------------------------------------------

-- Check quarterly view
SELECT 
    'vw_stock_prices_quarter' as view_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT company_id) as num_companies,
    MIN(fiscal_year) as earliest_year,
    MAX(fiscal_year) as latest_year
FROM vw_stock_prices_quarter;

-- Check annual materialized view  
SELECT 
    'mv_stock_prices_annual' as view_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT company_id) as num_companies,
    MIN(fiscal_year) as earliest_year,
    MAX(fiscal_year) as latest_year
FROM mv_stock_prices_annual;

-- Sample data from quarterly view
SELECT 
    c.ticker,
    c.name,
    sq.fiscal_year,
    sq.fiscal_quarter,
    ROUND(sq.avg_price::numeric, 2) as avg_price,
    ROUND(sq.return_qoq::numeric * 100, 2) as return_qoq_pct,
    ROUND(sq.volatility_pct::numeric * 100, 2) as volatility_pct
FROM vw_stock_prices_quarter sq
JOIN dim_company c USING (company_id)
WHERE sq.fiscal_year = 2023
ORDER BY c.ticker, sq.fiscal_quarter
LIMIT 10;

-- Sample data from annual view
SELECT 
    c.ticker,
    c.name,
    sa.fiscal_year,
    ROUND(sa.avg_price_annual::numeric, 2) as avg_price,
    ROUND(sa.high_price_annual::numeric, 2) as year_high,
    ROUND(sa.low_price_annual::numeric, 2) as year_low,
    ROUND(sa.return_annual::numeric * 100, 2) as return_annual_pct,
    ROUND(sa.volatility_pct_annual::numeric * 100, 2) as volatility_pct
FROM mv_stock_prices_annual sa
JOIN dim_company c USING (company_id)
WHERE sa.fiscal_year = 2023
ORDER BY c.ticker;


-- ----------------------------------------------------------------------------
-- 4. GRANT PERMISSIONS (if needed)
-- ----------------------------------------------------------------------------

-- Grant SELECT to your application user (adjust role name as needed)
-- GRANT SELECT ON vw_stock_prices_quarter TO your_app_user;
-- GRANT SELECT ON mv_stock_prices_annual TO your_app_user;


-- ============================================================================
-- USAGE EXAMPLES FOR CFO AGENT
-- ============================================================================

/*

QUARTERLY QUERIES:
------------------
"show Apple stock price Q2 2023"
SELECT 
    c.ticker, c.name, sq.fiscal_year, sq.fiscal_quarter,
    sq.avg_price, sq.return_qoq, sq.volatility_pct
FROM vw_stock_prices_quarter sq
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL' AND sq.fiscal_year = 2023 AND sq.fiscal_quarter = 2;

"show Microsoft quarterly returns 2023"
SELECT 
    c.ticker, sq.fiscal_year, sq.fiscal_quarter, sq.return_qoq
FROM vw_stock_prices_quarter sq
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'MSFT' AND sq.fiscal_year = 2023
ORDER BY sq.fiscal_quarter;


ANNUAL QUERIES:
---------------
"show Apple stock price 2023"
SELECT 
    c.ticker, c.name, sa.fiscal_year,
    sa.avg_price_annual, sa.return_annual, sa.high_price_annual, sa.low_price_annual
FROM mv_stock_prices_annual sa
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AAPL' AND sa.fiscal_year = 2023;

"show Amazon annual return 2023"
SELECT 
    c.ticker, sa.fiscal_year, sa.return_annual
FROM mv_stock_prices_annual sa
JOIN dim_company c USING (company_id)
WHERE c.ticker = 'AMZN' AND sa.fiscal_year = 2023;

*/
