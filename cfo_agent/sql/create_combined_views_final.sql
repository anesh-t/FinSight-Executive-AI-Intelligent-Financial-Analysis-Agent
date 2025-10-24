-- ============================================================================
-- CREATE COMBINED VIEWS - FINAL VERSION (VERIFIED COLUMNS ONLY)
-- Run this in Supabase SQL Editor
-- ============================================================================
-- Based on actual verified schema:
-- fact_financials: revenue, net_income, eps, r_and_d_expenses, sg_and_a_expenses, buybacks, etc.
-- fact_stock_prices: open_price, close_price, avg_price, volume_total, volatility_pct, dividend_per_share, etc.
-- vw_ratios_quarter: gross_margin, operating_margin, net_margin, roe, roa, rnd_to_revenue, sgna_to_revenue
-- vw_macro_quarter: gdp, cpi, unemployment_rate, fed_funds_rate, sp500_index, vix_index
-- vw_macro_sensitivity_rolling: margins + betas
-- mv_financials_annual: revenue_annual, net_income_annual, eps_annual, etc.
-- mv_ratios_annual: (assuming similar to quarterly)
-- mv_stock_prices_annual: avg_price_annual, return_annual, etc.
-- mv_macro_annual: gdp_annual, cpi_annual, etc.
-- mv_macro_sensitivity_annual: betas
-- ============================================================================

-- ============================================================================
-- PART 1: QUARTERLY VIEWS
-- ============================================================================

-- [1/6] Layer 1 - Core Company (Quarterly)

DROP VIEW IF EXISTS vw_company_complete_quarter CASCADE;

CREATE VIEW vw_company_complete_quarter AS
SELECT 
    -- Identifiers
    c.company_id, c.ticker, c.name, 
    f.fiscal_year, f.fiscal_quarter,
    
    -- Financials (from fact_financials)
    f.revenue, f.gross_profit, f.operating_income, f.net_income, f.ebitda, f.eps,
    f.r_and_d_expenses, f.sg_and_a_expenses, f.cogs,
    f.total_assets, f.total_liabilities, f.equity,
    f.cash_flow_ops, f.cash_flow_investing, f.cash_flow_financing,
    f.capex, f.dividends, f.buybacks,
    
    -- Ratios (from vw_ratios_quarter)
    r.gross_margin, r.operating_margin, r.net_margin,
    r.roe, r.roa,
    r.debt_to_equity, r.debt_to_assets,
    r.rnd_to_revenue as rd_intensity,
    r.sgna_to_revenue as sga_intensity,
    
    -- Stock (from vw_stock_prices_quarter - actual columns only)
    sp.open_price, sp.close_price, sp.high_price, sp.low_price, sp.avg_price,
    sp.return_qoq, sp.return_yoy,
    sp.price_change_abs, sp.price_change_pct,
    sp.volume_total, sp.volume_avg, sp.volatility_pct,
    sp.dividend_yield, sp.dividend_per_share
    
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

-- ----------------------------------------------------------------------------

-- [2/6] Layer 2 - With Macro Context (Quarterly)

DROP VIEW IF EXISTS vw_company_macro_context_quarter CASCADE;

CREATE VIEW vw_company_macro_context_quarter AS
SELECT 
    cc.*,
    -- Macro indicators (from vw_macro_quarter)
    m.gdp, m.pce, m.cpi, m.core_cpi, m.pce_price_index,
    m.unemployment_rate, m.fed_funds_rate, m.term_spread_10y_2y,
    m.sp500_index, m.vix_index
FROM vw_company_complete_quarter cc
LEFT JOIN vw_macro_quarter m 
    ON cc.fiscal_year = m.fiscal_year 
    AND cc.fiscal_quarter = m.fiscal_quarter;

-- ----------------------------------------------------------------------------

-- [3/6] Layer 3 - Full Picture (Quarterly)

DROP VIEW IF EXISTS vw_company_full_quarter CASCADE;

CREATE VIEW vw_company_full_quarter AS
SELECT 
    cmc.*,
    -- Sensitivity betas (from vw_macro_sensitivity_rolling)
    ms.beta_gm_cpi_12q, ms.beta_om_cpi_12q, ms.beta_nm_cpi_12q,
    ms.beta_gm_ffr_12q, ms.beta_om_ffr_12q, ms.beta_nm_ffr_12q,
    ms.beta_nm_spx_12q, ms.beta_nm_unrate_12q
FROM vw_company_macro_context_quarter cmc
LEFT JOIN vw_macro_sensitivity_rolling ms 
    ON cmc.company_id = ms.company_id 
    AND cmc.fiscal_year = ms.fiscal_year 
    AND cmc.fiscal_quarter = ms.fiscal_quarter;

-- ============================================================================
-- PART 2: ANNUAL VIEWS
-- ============================================================================

-- [4/6] Layer 1 - Core Company (Annual)

DROP MATERIALIZED VIEW IF EXISTS mv_company_complete_annual CASCADE;

CREATE MATERIALIZED VIEW mv_company_complete_annual AS
SELECT 
    -- Identifiers
    c.company_id, c.ticker, c.name,
    fa.fiscal_year,
    
    -- Financials (from mv_financials_annual)
    fa.revenue_annual, fa.net_income_annual, fa.operating_income_annual, fa.gross_profit_annual,
    fa.eps_annual,
    fa.r_and_d_expenses_annual, fa.sgna_annual as sg_and_a_expenses_annual, fa.cogs_annual,
    fa.total_assets_eoy, fa.total_liabilities_eoy, fa.equity_eoy,
    fa.cash_flow_ops_annual, fa.cash_flow_investing_annual, fa.cash_flow_financing_annual,
    fa.capex_annual, fa.dividends_annual, fa.buybacks_annual,
    
    -- Ratios (from mv_ratios_annual if it exists, otherwise calculate)
    COALESCE(ra.gross_margin_annual, 
        CASE WHEN fa.revenue_annual > 0 THEN fa.gross_profit_annual / fa.revenue_annual END) as gross_margin_annual,
    COALESCE(ra.operating_margin_annual,
        CASE WHEN fa.revenue_annual > 0 THEN fa.operating_income_annual / fa.revenue_annual END) as operating_margin_annual,
    COALESCE(ra.net_margin_annual,
        CASE WHEN fa.revenue_annual > 0 THEN fa.net_income_annual / fa.revenue_annual END) as net_margin_annual,
    COALESCE(ra.roe_annual,
        CASE WHEN fa.equity_eoy > 0 THEN fa.net_income_annual / fa.equity_eoy END) as roe_annual,
    COALESCE(ra.roa_annual,
        CASE WHEN fa.total_assets_eoy > 0 THEN fa.net_income_annual / fa.total_assets_eoy END) as roa_annual,
    COALESCE(ra.debt_to_equity_annual,
        CASE WHEN fa.equity_eoy > 0 THEN (fa.total_liabilities_eoy - fa.equity_eoy) / fa.equity_eoy END) as debt_to_equity_annual,
    COALESCE(ra.debt_to_assets_annual,
        CASE WHEN fa.total_assets_eoy > 0 THEN (fa.total_liabilities_eoy - fa.equity_eoy) / fa.total_assets_eoy END) as debt_to_assets_annual,
    COALESCE(ra.rnd_to_revenue_annual,
        CASE WHEN fa.revenue_annual > 0 THEN fa.r_and_d_expenses_annual / fa.revenue_annual END) as rd_intensity_annual,
    COALESCE(ra.sgna_to_revenue_annual,
        CASE WHEN fa.revenue_annual > 0 THEN fa.sgna_annual / fa.revenue_annual END) as sga_intensity_annual,
    
    -- Stock (from mv_stock_prices_annual)
    sa.avg_open_price_annual, sa.avg_close_price_annual, sa.avg_price_annual,
    sa.high_price_annual, sa.low_price_annual, sa.close_price_eoy,
    sa.return_annual, sa.volatility_pct_annual,
    sa.volume_total_annual, sa.volume_avg_annual,
    sa.dividend_per_share_annual, sa.dividend_yield_annual
    
FROM mv_financials_annual fa
JOIN dim_company c USING (company_id)
LEFT JOIN mv_ratios_annual ra 
    ON fa.company_id = ra.company_id 
    AND fa.fiscal_year = ra.fiscal_year
LEFT JOIN mv_stock_prices_annual sa 
    ON fa.company_id = sa.company_id 
    AND fa.fiscal_year = sa.fiscal_year;

CREATE INDEX idx_mv_company_complete_annual_company ON mv_company_complete_annual(company_id);
CREATE INDEX idx_mv_company_complete_annual_year ON mv_company_complete_annual(fiscal_year);
CREATE INDEX idx_mv_company_complete_annual_ticker ON mv_company_complete_annual(ticker);

REFRESH MATERIALIZED VIEW mv_company_complete_annual;

-- ----------------------------------------------------------------------------

-- [5/6] Layer 2 - With Macro Context (Annual)

DROP MATERIALIZED VIEW IF EXISTS mv_company_macro_context_annual CASCADE;

CREATE MATERIALIZED VIEW mv_company_macro_context_annual AS
SELECT 
    cc.*,
    -- Macro indicators (from mv_macro_annual)
    ma.gdp_annual, ma.pce_annual, ma.cpi_annual, ma.core_cpi_annual, ma.pce_price_index_annual,
    ma.unemployment_rate_annual, ma.fed_funds_rate_annual, ma.term_spread_10y_2y_annual,
    ma.sp500_index_annual, ma.vix_index_annual
FROM mv_company_complete_annual cc
LEFT JOIN mv_macro_annual ma 
    ON cc.fiscal_year = ma.fiscal_year;

CREATE INDEX idx_mv_company_macro_annual_company ON mv_company_macro_context_annual(company_id);
CREATE INDEX idx_mv_company_macro_annual_year ON mv_company_macro_context_annual(fiscal_year);
CREATE INDEX idx_mv_company_macro_annual_ticker ON mv_company_macro_context_annual(ticker);

REFRESH MATERIALIZED VIEW mv_company_macro_context_annual;

-- ----------------------------------------------------------------------------

-- [6/6] Layer 3 - Full Picture (Annual)

DROP MATERIALIZED VIEW IF EXISTS mv_company_full_annual CASCADE;

CREATE MATERIALIZED VIEW mv_company_full_annual AS
SELECT 
    cmc.*,
    -- Sensitivity betas (from mv_macro_sensitivity_annual)
    msa.beta_gm_cpi_annual, msa.beta_om_cpi_annual, msa.beta_nm_cpi_annual,
    msa.beta_gm_ffr_annual, msa.beta_om_ffr_annual, msa.beta_nm_ffr_annual,
    msa.beta_nm_spx_annual, msa.beta_nm_unrate_annual
FROM mv_company_macro_context_annual cmc
LEFT JOIN mv_macro_sensitivity_annual msa 
    ON cmc.company_id = msa.company_id 
    AND cmc.fiscal_year = msa.fiscal_year;

CREATE INDEX idx_mv_company_full_annual_company ON mv_company_full_annual(company_id);
CREATE INDEX idx_mv_company_full_annual_year ON mv_company_full_annual(fiscal_year);
CREATE INDEX idx_mv_company_full_annual_ticker ON mv_company_full_annual(ticker);

REFRESH MATERIALIZED VIEW mv_company_full_annual;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

SELECT 'QUARTERLY VIEWS' as category, 
       'vw_company_complete_quarter' as view_name,
       COUNT(*) as records,
       COUNT(DISTINCT company_id) as companies
FROM vw_company_complete_quarter
UNION ALL
SELECT 'QUARTERLY VIEWS', 'vw_company_macro_context_quarter', COUNT(*), COUNT(DISTINCT company_id)
FROM vw_company_macro_context_quarter
UNION ALL
SELECT 'QUARTERLY VIEWS', 'vw_company_full_quarter', COUNT(*), COUNT(DISTINCT company_id)
FROM vw_company_full_quarter
UNION ALL
SELECT 'ANNUAL VIEWS', 'mv_company_complete_annual', COUNT(*), COUNT(DISTINCT company_id)
FROM mv_company_complete_annual
UNION ALL
SELECT 'ANNUAL VIEWS', 'mv_company_macro_context_annual', COUNT(*), COUNT(DISTINCT company_id)
FROM mv_company_macro_context_annual
UNION ALL
SELECT 'ANNUAL VIEWS', 'mv_company_full_annual', COUNT(*), COUNT(DISTINCT company_id)
FROM mv_company_full_annual;

-- ============================================================================
-- SUCCESS! ALL 6 COMBINED VIEWS CREATED
-- ============================================================================
