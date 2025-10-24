-- ============================================================================
-- CREATE ALL COMBINED VIEWS - SUPABASE COMPATIBLE
-- Run this ENTIRE file in Supabase SQL Editor
-- ============================================================================
-- Creates 6 combined views (3 quarterly + 3 annual) in layered approach
-- NO psql meta-commands - pure SQL only
-- ============================================================================

-- ============================================================================
-- PART 1: QUARTERLY VIEWS (Real-time)
-- ============================================================================

-- [1/6] Creating vw_company_complete_quarter (Layer 1 - Quarterly)

DROP VIEW IF EXISTS vw_company_complete_quarter CASCADE;

CREATE VIEW vw_company_complete_quarter AS
SELECT 
    c.company_id, c.ticker, c.name, f.fiscal_year, f.fiscal_quarter,
    -- Financials
    f.revenue, f.gross_profit, f.operating_income, f.net_income, f.ebitda, f.eps_diluted,
    f.rd_expenses, f.sga_expenses, f.cogs,
    f.total_assets, f.total_liabilities, f.total_equity, f.total_debt, f.cash_and_equiv,
    f.operating_cf, f.investing_cf, f.financing_cf, f.capex, f.dividends_paid,
    -- Ratios
    r.gross_margin, r.operating_margin, r.net_margin, r.roe, r.roa,
    r.debt_to_equity, r.debt_to_assets, r.rd_intensity, r.sga_intensity,
    -- Stock
    sp.avg_price_quarter, sp.avg_open_price_quarter, sp.avg_close_price_quarter,
    sp.high_price_quarter, sp.low_price_quarter, sp.close_price_eoq,
    sp.return_qoq, sp.return_yoy, sp.volatility_pct_quarter,
    sp.volume_total_quarter, sp.volume_avg_quarter,
    sp.dividend_per_share_quarter, sp.dividend_yield_quarter,
    sp.shares_outstanding, sp.market_cap_eoq, sp.buyback_amount
FROM fact_financials f
JOIN dim_company c USING (company_id)
LEFT JOIN vw_ratios_quarter r ON f.company_id = r.company_id AND f.fiscal_year = r.fiscal_year AND f.fiscal_quarter = r.fiscal_quarter
LEFT JOIN vw_stock_prices_quarter sp ON f.company_id = sp.company_id AND f.fiscal_year = sp.fiscal_year AND f.fiscal_quarter = sp.fiscal_quarter
WHERE f.fiscal_quarter IS NOT NULL;

-- ----------------------------------------------------------------------------

-- [2/6] Creating vw_company_macro_context_quarter (Layer 2 - Quarterly)

DROP VIEW IF EXISTS vw_company_macro_context_quarter CASCADE;

CREATE VIEW vw_company_macro_context_quarter AS
SELECT 
    cc.*,
    m.gdp, m.pce, m.cpi, m.core_cpi, m.pce_price_index,
    m.unemployment_rate, m.fed_funds_rate, m.term_spread_10y_2y,
    m.sp500_index, m.vix_index
FROM vw_company_complete_quarter cc
LEFT JOIN vw_macro_quarter m ON cc.fiscal_year = m.fiscal_year AND cc.fiscal_quarter = m.fiscal_quarter;

-- ----------------------------------------------------------------------------

-- [3/6] Creating vw_company_full_quarter (Layer 3 - Quarterly)

DROP VIEW IF EXISTS vw_company_full_quarter CASCADE;

CREATE VIEW vw_company_full_quarter AS
SELECT 
    cmc.*,
    ms.gross_margin as gross_margin_sensitivity,
    ms.operating_margin as operating_margin_sensitivity,
    ms.net_margin as net_margin_sensitivity,
    ms.cpi as cpi_sensitivity,
    ms.fed_funds_rate as fed_funds_rate_sensitivity,
    ms.sp500_index as sp500_index_sensitivity,
    ms.unemployment_rate as unemployment_rate_sensitivity,
    ms.beta_gm_cpi_12q, ms.beta_om_cpi_12q, ms.beta_nm_cpi_12q,
    ms.beta_gm_ffr_12q, ms.beta_om_ffr_12q, ms.beta_nm_ffr_12q,
    ms.beta_nm_spx_12q, ms.beta_nm_unrate_12q
FROM vw_company_macro_context_quarter cmc
LEFT JOIN vw_macro_sensitivity_rolling ms ON cmc.company_id = ms.company_id AND cmc.fiscal_year = ms.fiscal_year AND cmc.fiscal_quarter = ms.fiscal_quarter;

-- ============================================================================
-- PART 2: ANNUAL VIEWS (Materialized)
-- ============================================================================

-- [4/6] Creating mv_company_complete_annual (Layer 1 - Annual)

DROP MATERIALIZED VIEW IF EXISTS mv_company_complete_annual CASCADE;

CREATE MATERIALIZED VIEW mv_company_complete_annual AS
SELECT 
    c.company_id, c.ticker, c.name, fa.fiscal_year,
    -- Financials
    fa.revenue_annual, fa.gross_profit_annual, fa.operating_income_annual, 
    fa.net_income_annual, fa.ebitda_annual, fa.eps_diluted_annual,
    fa.rd_expenses_annual, fa.sga_expenses_annual, fa.cogs_annual,
    fa.total_assets_q4, fa.total_liabilities_q4, fa.total_equity_q4, 
    fa.total_debt_q4, fa.cash_and_equiv_q4,
    fa.operating_cf_annual, fa.investing_cf_annual, fa.financing_cf_annual, 
    fa.capex_annual, fa.dividends_paid_annual,
    -- Ratios
    ra.gross_margin_annual, ra.operating_margin_annual, ra.net_margin_annual, 
    ra.roe_annual, ra.roa_annual,
    ra.debt_to_equity_q4, ra.debt_to_assets_q4, 
    ra.rd_intensity_annual, ra.sga_intensity_annual,
    -- Stock
    sa.avg_price_annual, sa.avg_open_price_annual, sa.avg_close_price_annual,
    sa.high_price_annual, sa.low_price_annual, sa.close_price_eoy,
    sa.return_annual, sa.volatility_pct_annual,
    sa.volume_total_annual, sa.volume_avg_annual,
    sa.dividend_per_share_annual, sa.dividend_yield_annual,
    sa.shares_outstanding_eoy, sa.market_cap_eoy, 
    sa.buyback_amount_annual, sa.price_change_annual
FROM mv_financials_annual fa
JOIN dim_company c USING (company_id)
LEFT JOIN mv_ratios_annual ra ON fa.company_id = ra.company_id AND fa.fiscal_year = ra.fiscal_year
LEFT JOIN mv_stock_prices_annual sa ON fa.company_id = sa.company_id AND fa.fiscal_year = sa.fiscal_year;

CREATE INDEX idx_mv_company_complete_annual_company ON mv_company_complete_annual(company_id);
CREATE INDEX idx_mv_company_complete_annual_year ON mv_company_complete_annual(fiscal_year);
CREATE INDEX idx_mv_company_complete_annual_ticker ON mv_company_complete_annual(ticker);

REFRESH MATERIALIZED VIEW mv_company_complete_annual;

-- ----------------------------------------------------------------------------

-- [5/6] Creating mv_company_macro_context_annual (Layer 2 - Annual)

DROP MATERIALIZED VIEW IF EXISTS mv_company_macro_context_annual CASCADE;

CREATE MATERIALIZED VIEW mv_company_macro_context_annual AS
SELECT 
    cc.*,
    ma.gdp_annual, ma.pce_annual, ma.cpi_annual, ma.core_cpi_annual, ma.pce_price_index_annual,
    ma.unemployment_rate_annual, ma.fed_funds_rate_annual, ma.term_spread_10y_2y_annual,
    ma.sp500_index_annual, ma.vix_index_annual
FROM mv_company_complete_annual cc
LEFT JOIN mv_macro_annual ma ON cc.fiscal_year = ma.fiscal_year;

CREATE INDEX idx_mv_company_macro_annual_company ON mv_company_macro_context_annual(company_id);
CREATE INDEX idx_mv_company_macro_annual_year ON mv_company_macro_context_annual(fiscal_year);
CREATE INDEX idx_mv_company_macro_annual_ticker ON mv_company_macro_context_annual(ticker);

REFRESH MATERIALIZED VIEW mv_company_macro_context_annual;

-- ----------------------------------------------------------------------------

-- [6/6] Creating mv_company_full_annual (Layer 3 - Annual)

DROP MATERIALIZED VIEW IF EXISTS mv_company_full_annual CASCADE;

CREATE MATERIALIZED VIEW mv_company_full_annual AS
SELECT 
    cmc.*,
    msa.gross_margin_annual as gross_margin_sensitivity_annual,
    msa.operating_margin_annual as operating_margin_sensitivity_annual,
    msa.net_margin_annual as net_margin_sensitivity_annual,
    msa.cpi_annual as cpi_sensitivity_annual,
    msa.fed_funds_rate_annual as fed_funds_rate_sensitivity_annual,
    msa.sp500_index_annual as sp500_index_sensitivity_annual,
    msa.unemployment_rate_annual as unemployment_rate_sensitivity_annual,
    msa.beta_gm_cpi_annual, msa.beta_om_cpi_annual, msa.beta_nm_cpi_annual,
    msa.beta_gm_ffr_annual, msa.beta_om_ffr_annual, msa.beta_nm_ffr_annual,
    msa.beta_nm_spx_annual, msa.beta_nm_unrate_annual
FROM mv_company_macro_context_annual cmc
LEFT JOIN mv_macro_sensitivity_annual msa ON cmc.company_id = msa.company_id AND cmc.fiscal_year = msa.fiscal_year;

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
