# 📋 SCHEMA FOR SQL GENERATION PROMPT

Copy this into your generative_sql_prompt.md file

---

**dim_company**: company_id, ticker, name, sector, industry, aliases

**fact_financials**: financial_id, company_id, fiscal_year, fiscal_quarter, revenue, operating_income, net_income, eps, total_assets, total_liabilities, equity, cash_flow_ops, cash_flow_investing, cash_flow_financing, cogs, gross_profit, r_and_d_expenses, sg_and_a_expenses, ebit, ebitda, capex, dividends, buybacks, source_id, as_reported, version_ts

**mv_company_complete_annual**: company_id, ticker, name, fiscal_year, revenue_annual, net_income_annual, operating_income_annual, gross_profit_annual, ebit_annual, ebitda_annual, r_and_d_expenses_annual, sg_and_a_expenses_annual, cogs_annual, total_assets_eoy, total_liabilities_eoy, equity_eoy, cash_flow_ops_annual, cash_flow_investing_annual, cash_flow_financing_annual, capex_annual, quarters_count, has_full_year, gross_margin_annual, operating_margin_annual, net_margin_annual, roa_annual, roe_annual, debt_to_assets_annual, debt_to_equity_annual, rd_intensity_annual ... and 13 more

**mv_company_full_annual**: company_id, ticker, name, fiscal_year, revenue_annual, net_income_annual, operating_income_annual, gross_profit_annual, ebit_annual, ebitda_annual, r_and_d_expenses_annual, sg_and_a_expenses_annual, cogs_annual, total_assets_eoy, total_liabilities_eoy, equity_eoy, cash_flow_ops_annual, cash_flow_investing_annual, cash_flow_financing_annual, capex_annual, quarters_count, has_full_year, gross_margin_annual, operating_margin_annual, net_margin_annual, roa_annual, roe_annual, debt_to_assets_annual, debt_to_equity_annual, rd_intensity_annual ... and 31 more

**mv_company_macro_context_annual**: company_id, ticker, name, fiscal_year, revenue_annual, net_income_annual, operating_income_annual, gross_profit_annual, ebit_annual, ebitda_annual, r_and_d_expenses_annual, sg_and_a_expenses_annual, cogs_annual, total_assets_eoy, total_liabilities_eoy, equity_eoy, cash_flow_ops_annual, cash_flow_investing_annual, cash_flow_financing_annual, capex_annual, quarters_count, has_full_year, gross_margin_annual, operating_margin_annual, net_margin_annual, roa_annual, roe_annual, debt_to_assets_annual, debt_to_equity_annual, rd_intensity_annual ... and 23 more

**mv_financials_annual**: company_id, fiscal_year, quarters_count, has_full_year, revenue_annual, operating_income_annual, net_income_annual, gross_profit_annual, cogs_annual, r_and_d_expenses_annual, sg_and_a_expenses_annual, ebit_annual, ebitda_annual, cash_flow_ops_annual, cash_flow_investing_annual, cash_flow_financing_annual, capex_annual, total_assets_eoy, total_liabilities_eoy, equity_eoy

**mv_financials_ttm**: company_id, fiscal_year, fiscal_quarter, revenue, operating_income, net_income, cogs, r_and_d_expenses, sg_and_a_expenses, capex, total_assets, total_liabilities, equity, revenue_ttm, operating_income_ttm, net_income_ttm, cogs_ttm, r_and_d_expenses_ttm, sgna_ttm, capex_ttm, total_assets_avg_ttm, equity_avg_ttm

**mv_macro_annual**: fiscal_year, gdp_annual, pce_annual, cpi_annual, core_cpi_annual, pce_price_index_annual, unemployment_rate_annual, fed_funds_rate_annual, term_spread_10y_2y_annual, sp500_index_annual, vix_index_annual, gdp_q4, cpi_q4, unemployment_rate_q4, fed_funds_rate_q4, sp500_index_q4, version_ts

**mv_macro_sensitivity_annual**: company_id, fiscal_year, gross_margin_annual, operating_margin_annual, net_margin_annual, cpi_annual, fed_funds_rate_annual, sp500_index_annual, unemployment_rate_annual, beta_gm_cpi_annual, beta_om_cpi_annual, beta_nm_cpi_annual, beta_gm_ffr_annual, beta_om_ffr_annual, beta_nm_ffr_annual, beta_nm_spx_annual, beta_nm_unrate_annual, gross_margin_q4, operating_margin_q4, net_margin_q4

**mv_ratios_annual**: company_id, fiscal_year, has_full_year, gross_margin_annual, operating_margin_annual, net_margin_annual, roa_annual, roe_annual_avg_equity, debt_to_assets_annual, debt_to_equity_annual, rnd_to_revenue_annual, sgna_to_revenue_annual

**mv_ratios_ttm**: company_id, fiscal_year, fiscal_quarter, gross_margin_ttm, operating_margin_ttm, net_margin_ttm, roe_ttm, roa_ttm

**mv_stock_prices_annual**: company_id, fiscal_year, avg_open_price_annual, avg_close_price_annual, avg_price_annual, high_price_annual, low_price_annual, close_price_eoy, return_annual, volatility_pct_annual, volume_total_annual, volume_avg_annual, dividend_per_share_annual, dividend_yield_annual, version_ts

**vw_cfo_answers**: company_id, ticker, name, fiscal_year, fiscal_quarter, fyq_label, revenue, gross_profit, operating_income, net_income, total_assets, total_liabilities, equity, capex, gross_margin, operating_margin, net_margin, roe, roa, revenue_qoq, net_income_qoq, revenue_yoy, net_income_yoy, revenue_ttm, net_income_ttm, revenue_ttm_delta, net_income_ttm_delta, rank_revenue, pct_revenue, z_revenue ... and 12 more

**vw_company_complete_quarter**: company_id, ticker, name, fiscal_year, fiscal_quarter, revenue, gross_profit, operating_income, net_income, ebitda, eps, r_and_d_expenses, sg_and_a_expenses, cogs, total_assets, total_liabilities, equity, cash_flow_ops, cash_flow_investing, cash_flow_financing, capex, dividends, buybacks, gross_margin, operating_margin, net_margin, roe, roa, debt_to_equity, debt_to_assets ... and 16 more

**vw_company_full_quarter**: company_id, ticker, name, fiscal_year, fiscal_quarter, revenue, gross_profit, operating_income, net_income, ebitda, eps, r_and_d_expenses, sg_and_a_expenses, cogs, total_assets, total_liabilities, equity, cash_flow_ops, cash_flow_investing, cash_flow_financing, capex, dividends, buybacks, gross_margin, operating_margin, net_margin, roe, roa, debt_to_equity, debt_to_assets ... and 34 more

**vw_company_macro_context_quarter**: company_id, ticker, name, fiscal_year, fiscal_quarter, revenue, gross_profit, operating_income, net_income, ebitda, eps, r_and_d_expenses, sg_and_a_expenses, cogs, total_assets, total_liabilities, equity, cash_flow_ops, cash_flow_investing, cash_flow_financing, capex, dividends, buybacks, gross_margin, operating_margin, net_margin, roe, roa, debt_to_equity, debt_to_assets ... and 26 more

**vw_company_quarter**: company_id, ticker, name, fiscal_year, fiscal_quarter, revenue, gross_profit, gross_profit_source, delta_abs, delta_pct, cogs, operating_income, net_income, total_assets, total_liabilities, equity, capex, close_price, return_qoq, return_yoy, volatility_pct, roe, roa, gross_margin, operating_margin, net_margin, debt_to_equity, debt_to_assets, rnd_to_revenue, sgna_to_revenue

**vw_company_quarter_macro**: company_id, ticker, name, fiscal_year, fiscal_quarter, revenue, gross_profit, gross_profit_source, delta_abs, delta_pct, cogs, operating_income, net_income, total_assets, total_liabilities, equity, capex, close_price, return_qoq, return_yoy, volatility_pct, roe, roa, gross_margin, operating_margin, net_margin, debt_to_equity, debt_to_assets, rnd_to_revenue, sgna_to_revenue ... and 10 more

**vw_data_dictionary**: table_name, code, name, unit, category, description, frequency

**vw_fact_citations**: company_id, ticker, fiscal_year, fiscal_quarter, quarter_end, revenue, cogs, gross_profit, operating_income, net_income, total_assets, total_liabilities, equity, capex, as_reported, version_ts, source_id, source_code, source_name

**vw_financial_health_quarter**: company_id, fiscal_year, fiscal_quarter, total_assets, total_liabilities, equity, liabilities_plus_equity, balance_gap, balance_status, flag_negative_equity, flag_net_loss

**vw_growth_quarter**: company_id, ticker, name, fiscal_year, fiscal_quarter, revenue, gross_profit, gross_profit_source, delta_abs, delta_pct, cogs, operating_income, net_income, total_assets, total_liabilities, equity, capex, close_price, return_qoq, return_yoy, volatility_pct, roe, roa, gross_margin, operating_margin, net_margin, debt_to_equity, debt_to_assets, rnd_to_revenue, sgna_to_revenue ... and 8 more

**vw_growth_ttm**: company_id, fiscal_year, fiscal_quarter, revenue, operating_income, net_income, cogs, r_and_d_expenses, sg_and_a_expenses, capex, total_assets, total_liabilities, equity, revenue_ttm, operating_income_ttm, net_income_ttm, cogs_ttm, r_and_d_expenses_ttm, sgna_ttm, capex_ttm, total_assets_avg_ttm, equity_avg_ttm, rev_ttm_prev, ni_ttm_prev, revenue_ttm_delta, net_income_ttm_delta

**vw_latest_company_quarter**: company_id, fiscal_year, fiscal_quarter

**vw_macro_citations**: indicator_id, indicator_code, indicator_name, quarter_end, value, version_ts, source_id, source_code, source_name

**vw_macro_quarter**: fiscal_year, fiscal_quarter, gdp, pce, cpi, core_cpi, pce_price_index, unemployment_rate, fed_funds_rate, term_spread_10y_2y, sp500_index, vix_index, version_ts

**vw_macro_sensitivity_rolling**: company_id, fiscal_year, fiscal_quarter, gross_margin, operating_margin, net_margin, cpi, fed_funds_rate, sp500_index, unemployment_rate, beta_gm_cpi_12q, beta_om_cpi_12q, beta_nm_cpi_12q, beta_gm_ffr_12q, beta_om_ffr_12q, beta_nm_ffr_12q, beta_nm_spx_12q, beta_nm_unrate_12q

**vw_outliers_quarter**: company_id, fiscal_year, fiscal_quarter, revenue, net_margin, mu_rev, sd_rev, mu_nm, sd_nm, z_rev, z_nm, outlier_revenue_3sigma, outlier_net_margin_3sigma

**vw_peer_stats_quarter**: peer_group_id, company_id, fiscal_year, fiscal_quarter, revenue, net_income, operating_income, gross_profit, gross_margin, operating_margin, net_margin, roe, roa, rank_revenue, pct_revenue, z_revenue, rank_net_margin, pct_net_margin, z_net_margin, rank_roe, pct_roe

**vw_ratios_quarter**: company_id, ticker, company_name, fiscal_year, fiscal_quarter, roe, roa, gross_margin, operating_margin, net_margin, debt_to_equity, debt_to_assets, rnd_to_revenue, sgna_to_revenue

**vw_stock_citations**: company_id, ticker, fiscal_year, fiscal_quarter, quarter_end, close_price, return_qoq, return_yoy, volatility_pct, version_ts, source_id, source_code, source_name

**vw_stock_prices_quarter**: company_id, fiscal_year, fiscal_quarter, open_price, close_price, high_price, low_price, avg_price, return_qoq, return_yoy, price_change_abs, price_change_pct, volume_total, volume_avg, volatility_pct, dividend_yield, dividend_per_share, version_ts

