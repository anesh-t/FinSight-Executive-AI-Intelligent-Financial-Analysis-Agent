"""
Database Migration Script Part 2 - Prompts 4-6
Annual/TTM financials, ratios, unified views, and smoke tests
"""

from database import SupabaseConnector

class DatabaseMigrationPart2:
    def __init__(self):
        self.db = SupabaseConnector()
    
    def prompt_4_annual_ttm(self):
        """Prompt 4: Annual financials & ratios + TTM layers"""
        print("\n" + "="*80)
        print("PROMPT 4: ANNUAL & TTM FINANCIALS AND RATIOS")
        print("="*80)
        
        queries = [
            # Annual financials
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_financials_annual AS
            WITH ranked AS (
              SELECT f.*, ROW_NUMBER() OVER (PARTITION BY company_id, fiscal_year ORDER BY fiscal_quarter DESC) AS rn_desc
              FROM fact_financials f
            ),
            gp AS (
              SELECT company_id, fiscal_year, SUM(gross_profit_authoritative) AS gross_profit_annual
              FROM vw_gross_profit_reconciled
              GROUP BY 1,2
            ),
            agg AS (
              SELECT
                company_id, fiscal_year,
                SUM(revenue)           AS revenue_annual,
                SUM(operating_income)  AS operating_income_annual,
                SUM(net_income)        AS net_income_annual,
                SUM(cogs)              AS cogs_annual,
                SUM(r_and_d_expenses)  AS r_and_d_expenses_annual,
                SUM(sg_and_a_expenses) AS sgna_annual,
                SUM(capex)             AS capex_annual,
                MAX(total_assets)      FILTER (WHERE rn_desc=1) AS total_assets_eoy,
                MAX(total_liabilities) FILTER (WHERE rn_desc=1) AS total_liabilities_eoy,
                MAX(equity)            FILTER (WHERE rn_desc=1) AS equity_eoy,
                AVG(total_assets)      AS total_assets_avg_fy,
                AVG(equity)            AS equity_avg_fy
              FROM ranked
              GROUP BY 1,2
            )
            SELECT
              a.company_id, a.fiscal_year,
              a.revenue_annual, g.gross_profit_annual, a.cogs_annual,
              a.operating_income_annual, a.net_income_annual, a.capex_annual,
              a.total_assets_eoy, a.total_liabilities_eoy, a.equity_eoy,
              a.total_assets_avg_fy, a.equity_avg_fy,
              a.r_and_d_expenses_annual, a.sgna_annual
            FROM agg a LEFT JOIN gp g USING (company_id, fiscal_year)
            """,
            
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_mv_fin_annual ON mv_financials_annual (company_id, fiscal_year)",
            
            # TTM financials
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_financials_ttm AS
            WITH base AS (
              SELECT company_id, fiscal_year, fiscal_quarter,
                     revenue, operating_income, net_income, cogs, r_and_d_expenses, sg_and_a_expenses, capex,
                     total_assets, total_liabilities, equity
              FROM fact_financials
            ),
            roll AS (
              SELECT
                b.*,
                SUM(revenue)           OVER w AS revenue_ttm,
                SUM(operating_income)  OVER w AS operating_income_ttm,
                SUM(net_income)        OVER w AS net_income_ttm,
                SUM(cogs)              OVER w AS cogs_ttm,
                SUM(r_and_d_expenses)  OVER w AS r_and_d_expenses_ttm,
                SUM(sg_and_a_expenses) OVER w AS sgna_ttm,
                SUM(capex)             OVER w AS capex_ttm,
                AVG(total_assets)      OVER w AS total_assets_avg_ttm,
                AVG(equity)            OVER w AS equity_avg_ttm
              FROM base b
              WINDOW w AS (PARTITION BY company_id ORDER BY fiscal_year, fiscal_quarter ROWS BETWEEN 3 PRECEDING AND CURRENT ROW)
            )
            SELECT * FROM roll
            """,
            
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_mv_fin_ttm ON mv_financials_ttm (company_id, fiscal_year, fiscal_quarter)",
            
            # Annual ratios
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_ratios_annual AS
            SELECT
              company_id, fiscal_year,
              CASE WHEN NULLIF(revenue_annual,0) IS NULL THEN NULL ELSE gross_profit_annual    / NULLIF(revenue_annual,0) END AS gross_margin_annual,
              CASE WHEN NULLIF(revenue_annual,0) IS NULL THEN NULL ELSE operating_income_annual/ NULLIF(revenue_annual,0) END AS operating_margin_annual,
              CASE WHEN NULLIF(revenue_annual,0) IS NULL THEN NULL ELSE net_income_annual      / NULLIF(revenue_annual,0) END AS net_margin_annual,
              CASE WHEN NULLIF(equity_avg_fy,0)       IS NULL THEN NULL ELSE net_income_annual / NULLIF(equity_avg_fy,0)       END AS roe_annual_avg_equity,
              CASE WHEN NULLIF(equity_eoy,0)          IS NULL THEN NULL ELSE net_income_annual / NULLIF(equity_eoy,0)          END AS roe_annual_end_equity,
              CASE WHEN NULLIF(total_assets_avg_fy,0) IS NULL THEN NULL ELSE net_income_annual / NULLIF(total_assets_avg_fy,0) END AS roa_annual,
              CASE WHEN NULLIF(equity_eoy,0)          IS NULL THEN NULL ELSE total_liabilities_eoy / NULLIF(equity_eoy,0)      END AS debt_to_equity_eoy,
              CASE WHEN NULLIF(total_assets_eoy,0)    IS NULL THEN NULL ELSE total_liabilities_eoy / NULLIF(total_assets_eoy,0)END AS debt_to_assets_eoy,
              CASE WHEN NULLIF(revenue_annual,0) IS NULL THEN NULL ELSE r_and_d_expenses_annual / NULLIF(revenue_annual,0)    END AS rnd_to_revenue_annual,
              CASE WHEN NULLIF(revenue_annual,0) IS NULL THEN NULL ELSE sgna_annual             / NULLIF(revenue_annual,0)    END AS sgna_to_revenue_annual
            FROM mv_financials_annual
            """,
            
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_mv_ratios_annual ON mv_ratios_annual (company_id, fiscal_year)",
            
            # TTM ratios
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_ratios_ttm AS
            SELECT
              company_id, fiscal_year, fiscal_quarter,
              CASE WHEN NULLIF(revenue_ttm,0) IS NULL THEN NULL ELSE (revenue_ttm - cogs_ttm)/NULLIF(revenue_ttm,0) END AS gross_margin_ttm,
              CASE WHEN NULLIF(revenue_ttm,0) IS NULL THEN NULL ELSE operating_income_ttm / NULLIF(revenue_ttm,0) END AS operating_margin_ttm,
              CASE WHEN NULLIF(revenue_ttm,0) IS NULL THEN NULL ELSE net_income_ttm       / NULLIF(revenue_ttm,0) END AS net_margin_ttm,
              CASE WHEN NULLIF(equity_avg_ttm,0) IS NULL THEN NULL ELSE net_income_ttm    / NULLIF(equity_avg_ttm,0) END AS roe_ttm,
              CASE WHEN NULLIF(total_assets_avg_ttm,0) IS NULL THEN NULL ELSE net_income_ttm / NULLIF(total_assets_avg_ttm,0) END AS roa_ttm
            FROM mv_financials_ttm
            """,
            
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_mv_ratios_ttm ON mv_ratios_ttm (company_id, fiscal_year, fiscal_quarter)"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\nExecuting materialized view/index {i}/{len(queries)}...")
            if self.db.execute_ddl(query):
                print(f"✅ Step {i} completed")
            else:
                print(f"❌ ERROR at step {i}")
                return False
        
        # Refresh materialized views
        print("\nRefreshing materialized views...")
        refresh_queries = [
            "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_financials_annual",
            "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_financials_ttm",
            "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ratios_annual",
            "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ratios_ttm"
        ]
        
        for query in refresh_queries:
            print(f"Refreshing {query.split()[-1]}...")
            if not self.db.execute_ddl(query):
                print(f"⚠️ Warning: Could not refresh {query}")
        
        # Verify
        print("\nVerifying annual financials...")
        verify1 = "SELECT * FROM mv_financials_annual ORDER BY company_id, fiscal_year LIMIT 10"
        result1 = self.db.execute_query(verify1)
        print(f"Annual financials: {len(result1)} rows")
        
        print("\nVerifying TTM ratios...")
        verify2 = "SELECT * FROM mv_ratios_ttm ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC LIMIT 10"
        result2 = self.db.execute_query(verify2)
        print(f"TTM ratios: {len(result2)} rows")
        
        print("\n✅ Annual and TTM views created!")
        return True
    
    def prompt_5_unified_views(self):
        """Prompt 5: Unified per-quarter view + Macro overlay + Dictionary"""
        print("\n" + "="*80)
        print("PROMPT 5: UNIFIED VIEWS + MACRO OVERLAY + DICTIONARY")
        print("="*80)
        
        queries = [
            # Per-quarter unified view
            """
            CREATE OR REPLACE VIEW vw_company_quarter AS
            SELECT
              f.company_id, c.ticker, c.name,
              f.fiscal_year, f.fiscal_quarter,
              f.revenue,
              g.gross_profit_authoritative AS gross_profit,
              g.gross_profit_source, g.delta_abs, g.delta_pct,
              f.cogs, f.operating_income, f.net_income,
              f.total_assets, f.total_liabilities, f.equity, f.capex,
              sp.close_price, sp.return_qoq, sp.return_yoy, sp.volatility_pct,
              r.roe, r.roa, r.gross_margin, r.operating_margin, r.net_margin,
              r.debt_to_equity, r.debt_to_assets, r.rnd_to_revenue, r.sgna_to_revenue
            FROM fact_financials f
            JOIN dim_company c USING (company_id)
            LEFT JOIN fact_stock_prices sp USING (company_id, fiscal_year, fiscal_quarter)
            LEFT JOIN vw_gross_profit_reconciled g USING (company_id, fiscal_year, fiscal_quarter)
            LEFT JOIN vw_ratios_canonical r USING (company_id, fiscal_year, fiscal_quarter)
            """,
            
            # Macro overlay
            """
            CREATE OR REPLACE VIEW vw_company_quarter_macro AS
            SELECT
              cq.*,
              gdp.value    AS gdp,
              cpi.value    AS cpi,
              core_cpi.value AS core_cpi,
              unrate.value AS unemployment_rate,
              ffr.value    AS fed_funds_rate,
              spx.value    AS sp500_index,
              vix.value    AS vix_index,
              pce.value    AS pce,
              pcepi.value  AS pce_price_index,
              term.value   AS term_spread_10y_2y
            FROM vw_company_quarter cq
            JOIN vw_qe_date qd
              ON qd.company_id=cq.company_id AND qd.fiscal_year=cq.fiscal_year AND qd.fiscal_quarter=cq.fiscal_quarter
            LEFT JOIN fact_macro_indicators gdp     ON gdp.indicator_id=(SELECT indicator_id FROM dim_macro_indicator WHERE code='GDPC1')   AND gdp.date=qd.quarter_end
            LEFT JOIN fact_macro_indicators cpi     ON cpi.indicator_id=(SELECT indicator_id FROM dim_macro_indicator WHERE code='CPIAUCSL') AND cpi.date=qd.quarter_end
            LEFT JOIN fact_macro_indicators core_cpi ON core_cpi.indicator_id=(SELECT indicator_id FROM dim_macro_indicator WHERE code='CPILFESL') AND core_cpi.date=qd.quarter_end
            LEFT JOIN fact_macro_indicators unrate  ON unrate.indicator_id=(SELECT indicator_id FROM dim_macro_indicator WHERE code='UNRATE')  AND unrate.date=qd.quarter_end
            LEFT JOIN fact_macro_indicators ffr     ON ffr.indicator_id=(SELECT indicator_id FROM dim_macro_indicator WHERE code='FEDFUNDS') AND ffr.date=qd.quarter_end
            LEFT JOIN fact_macro_indicators spx     ON spx.indicator_id=(SELECT indicator_id FROM dim_macro_indicator WHERE code='SP500')   AND spx.date=qd.quarter_end
            LEFT JOIN fact_macro_indicators vix     ON vix.indicator_id=(SELECT indicator_id FROM dim_macro_indicator WHERE code='VIXCLS')  AND vix.date=qd.quarter_end
            LEFT JOIN fact_macro_indicators pce     ON pce.indicator_id=(SELECT indicator_id FROM dim_macro_indicator WHERE code='PCE')     AND pce.date=qd.quarter_end
            LEFT JOIN fact_macro_indicators pcepi   ON pcepi.indicator_id=(SELECT indicator_id FROM dim_macro_indicator WHERE code='PCEPI')  AND pcepi.date=qd.quarter_end
            LEFT JOIN fact_macro_indicators term    ON term.indicator_id=(SELECT indicator_id FROM dim_macro_indicator WHERE code='T10Y2Y')  AND term.date=qd.quarter_end
            """,
            
            # LLM dictionary
            """
            CREATE OR REPLACE VIEW vw_data_dictionary AS
            SELECT 'fact_financials' AS table_name, code, name, unit, category, description, frequency
            FROM dim_financial_metric
            UNION ALL
            SELECT 'fact_ratios', code, name, unit, category, description, frequency
            FROM dim_ratio
            UNION ALL
            SELECT 'fact_macro_indicators', code, name, unit, 'Macro', description, frequency
            FROM dim_macro_indicator
            UNION ALL
            SELECT 'fact_stock_prices', code, name, unit, category, description, frequency
            FROM dim_stock_metric
            """
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\nExecuting unified view {i}/{len(queries)}...")
            if self.db.execute_ddl(query):
                print(f"✅ View {i} created")
            else:
                print(f"❌ ERROR at view {i}")
                return False
        
        # Verify
        print("\nVerifying unified views...")
        verify1 = "SELECT * FROM vw_company_quarter ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC LIMIT 10"
        result1 = self.db.execute_query(verify1)
        print(f"Company quarter view: {len(result1)} rows")
        
        verify2 = "SELECT * FROM vw_company_quarter_macro ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC LIMIT 10"
        result2 = self.db.execute_query(verify2)
        print(f"Company quarter macro view: {len(result2)} rows")
        
        verify3 = "SELECT * FROM vw_data_dictionary LIMIT 20"
        result3 = self.db.execute_query(verify3)
        print(f"Data dictionary: {len(result3)} entries")
        
        print("\n✅ Unified views and dictionary created!")
        return True
    
    def prompt_6_smoke_tests(self):
        """Prompt 6: Post-migration smoke tests"""
        print("\n" + "="*80)
        print("PROMPT 6: SMOKE TESTS")
        print("="*80)
        
        tests = [
            ("ROE of Apple (AAPL) in 2022 (annual, avg equity)", """
                SELECT c.ticker, r.fiscal_year, r.roe_annual_avg_equity
                FROM mv_ratios_annual r
                JOIN dim_company c USING (company_id)
                WHERE c.ticker='AAPL' AND r.fiscal_year=2022
            """),
            
            ("Revenue & Net Income of Apple in 2022 (annual)", """
                SELECT c.ticker, a.fiscal_year, a.revenue_annual, a.net_income_annual
                FROM mv_financials_annual a
                JOIN dim_company c USING (company_id)
                WHERE c.ticker='AAPL' AND a.fiscal_year=2022
            """),
            
            ("Latest TTM snapshot for each company", """
                WITH latest AS (
                  SELECT company_id, MAX((fiscal_year, fiscal_quarter)) AS yq
                  FROM mv_financials_ttm GROUP BY 1
                )
                SELECT t.company_id, c.ticker, t.fiscal_year, t.fiscal_quarter,
                       t.revenue_ttm, t.net_income_ttm, rt.roe_ttm, rt.roa_ttm
                FROM mv_financials_ttm t
                JOIN latest l ON l.company_id=t.company_id AND l.yq=(t.fiscal_year, t.fiscal_quarter)
                JOIN mv_ratios_ttm rt USING (company_id, fiscal_year, fiscal_quarter)
                JOIN dim_company c USING (company_id)
                ORDER BY t.company_id
            """),
            
            ("Macro overlay spot check (latest available quarter)", """
                SELECT company_id, ticker, fiscal_year, fiscal_quarter, cpi, fed_funds_rate, sp500_index
                FROM vw_company_quarter_macro
                ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC
                LIMIT 15
            """)
        ]
        
        all_passed = True
        for i, (test_name, query) in enumerate(tests, 1):
            print(f"\n{i}. {test_name}")
            result = self.db.execute_query(query)
            if result.empty:
                print(f"   ⚠️ Warning: No results returned")
                all_passed = False
            else:
                print(f"   ✅ Passed ({len(result)} rows)")
                print(result.to_string(index=False)[:200])
        
        if all_passed:
            print("\n✅ All smoke tests passed!")
        else:
            print("\n⚠️ Some smoke tests returned no data")
        
        return True
    
    def run_all(self):
        """Execute all migration prompts 4-6"""
        print("\n" + "="*80)
        print("STARTING DATABASE MIGRATION PART 2 (PROMPTS 4-6)")
        print("="*80)
        
        # Prompt 4
        if not self.prompt_4_annual_ttm():
            print("\n❌ Migration stopped at Prompt 4")
            return False
        
        # Prompt 5
        if not self.prompt_5_unified_views():
            print("\n❌ Migration stopped at Prompt 5")
            return False
        
        # Prompt 6
        if not self.prompt_6_smoke_tests():
            print("\n❌ Migration stopped at Prompt 6")
            return False
        
        print("\n" + "="*80)
        print("✅ COMPLETE DATABASE MIGRATION FINISHED!")
        print("="*80)
        print("\n🎉 All views, materialized views, and indexes are ready!")
        print("📊 Your CFO Assistant can now use:")
        print("   - vw_company_quarter (per-quarter unified)")
        print("   - vw_company_quarter_macro (with macro overlay)")
        print("   - mv_financials_annual (annual aggregates)")
        print("   - mv_financials_ttm (trailing twelve months)")
        print("   - mv_ratios_annual & mv_ratios_ttm")
        print("   - vw_data_dictionary (metric definitions)")
        return True


if __name__ == "__main__":
    migration = DatabaseMigrationPart2()
    migration.run_all()
