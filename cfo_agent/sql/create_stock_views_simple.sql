-- ============================================================================
-- CREATE STOCK PRICE VIEWS - Quarterly & Annual
-- Run this in your database admin tool (pgAdmin, psql, etc.)
-- ============================================================================

-- 1. Quarterly View (passthrough from fact_stock_prices)
DROP VIEW IF EXISTS vw_stock_prices_quarter CASCADE;

CREATE VIEW vw_stock_prices_quarter AS
SELECT 
    company_id,
    fiscal_year,
    fiscal_quarter,
    open_price,
    close_price,
    high_price,
    low_price,
    avg_price,
    return_qoq,
    return_yoy,
    price_change_abs,
    price_change_pct,
    volume_total,
    volume_avg,
    volatility_pct,
    dividend_yield,
    dividend_per_share,
    version_ts
FROM fact_stock_prices;


-- 2. Annual Materialized View (aggregated from quarterly)
DROP MATERIALIZED VIEW IF EXISTS mv_stock_prices_annual CASCADE;

CREATE MATERIALIZED VIEW mv_stock_prices_annual AS
SELECT 
    company_id,
    fiscal_year,
    AVG(open_price) as avg_open_price_annual,
    AVG(close_price) as avg_close_price_annual,
    AVG(avg_price) as avg_price_annual,
    MAX(high_price) as high_price_annual,
    MIN(low_price) as low_price_annual,
    MAX(CASE WHEN fiscal_quarter = 4 THEN close_price END) as close_price_eoy,
    (MAX(CASE WHEN fiscal_quarter = 4 THEN close_price END) - 
     MIN(CASE WHEN fiscal_quarter = 1 THEN open_price END)) / 
     NULLIF(MIN(CASE WHEN fiscal_quarter = 1 THEN open_price END), 0) as return_annual,
    AVG(volatility_pct) as volatility_pct_annual,
    SUM(volume_total) as volume_total_annual,
    AVG(volume_avg) as volume_avg_annual,
    SUM(COALESCE(dividend_per_share, 0)) as dividend_per_share_annual,
    AVG(dividend_yield) as dividend_yield_annual,
    MAX(version_ts) as version_ts
FROM fact_stock_prices
GROUP BY company_id, fiscal_year;


-- 3. Create indexes
CREATE INDEX idx_mv_stock_annual_company ON mv_stock_prices_annual(company_id);
CREATE INDEX idx_mv_stock_annual_year ON mv_stock_prices_annual(fiscal_year);
CREATE INDEX idx_mv_stock_annual_company_year ON mv_stock_prices_annual(company_id, fiscal_year);


-- 4. Refresh the materialized view
REFRESH MATERIALIZED VIEW mv_stock_prices_annual;


-- 5. Verify
SELECT 'Quarterly View' as view_type, COUNT(*) as records FROM vw_stock_prices_quarter;
SELECT 'Annual View' as view_type, COUNT(*) as records FROM mv_stock_prices_annual;
