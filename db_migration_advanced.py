"""
Advanced Database Migration - Prompts A-H
Peer groups, growth layers, rankings, sensitivities, and final answer surface
"""

from database import SupabaseConnector

class AdvancedMigration:
    def __init__(self):
        self.db = SupabaseConnector()
    
    def prompt_a_peer_groups(self):
        """Prompt A: Create peer groups (ALL_COMPANIES)"""
        print("\n" + "="*80)
        print("PROMPT A: PEER GROUPS")
        print("="*80)
        
        queries = [
            """
            CREATE TABLE IF NOT EXISTS dim_peer_group (
              peer_group_id serial PRIMARY KEY,
              name          text UNIQUE NOT NULL,
              description   text
            )
            """,
            
            """
            CREATE TABLE IF NOT EXISTS bridge_company_peer_group (
              peer_group_id int REFERENCES dim_peer_group(peer_group_id) ON DELETE CASCADE,
              company_id    int REFERENCES dim_company(company_id) ON DELETE CASCADE,
              PRIMARY KEY(peer_group_id, company_id)
            )
            """,
            
            """
            INSERT INTO dim_peer_group (name, description)
            VALUES ('ALL_COMPANIES', 'All companies in the current dataset')
            ON CONFLICT (name) DO NOTHING
            """,
            
            """
            INSERT INTO bridge_company_peer_group (peer_group_id, company_id)
            SELECT pg.peer_group_id, c.company_id
            FROM dim_peer_group pg
            JOIN dim_company c ON TRUE
            WHERE pg.name='ALL_COMPANIES'
            ON CONFLICT DO NOTHING
            """
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\nExecuting step {i}/{len(queries)}...")
            if self.db.execute_ddl(query):
                print(f"✅ Step {i} completed")
            else:
                print(f"❌ ERROR at step {i}")
                return False
        
        # Verify
        print("\nVerifying peer groups...")
        verify = """
        SELECT dpg.name, COUNT(*) AS members
        FROM dim_peer_group dpg
        JOIN bridge_company_peer_group b USING (peer_group_id)
        GROUP BY 1
        """
        result = self.db.execute_query(verify)
        print(result.to_string(index=False))
        
        print("\n✅ Peer groups created!")
        return True
    
    def prompt_b_helpers(self):
        """Prompt B: Helpers (latest quarter & label)"""
        print("\n" + "="*80)
        print("PROMPT B: HELPER VIEWS AND FUNCTIONS")
        print("="*80)
        
        queries = [
            """
            CREATE OR REPLACE VIEW vw_latest_company_quarter AS
            SELECT DISTINCT ON (company_id)
              company_id, fiscal_year, fiscal_quarter
            FROM fact_financials
            ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC
            """,
            
            """
            CREATE OR REPLACE FUNCTION fmt_fyq(fy int, fq int)
            RETURNS text LANGUAGE sql IMMUTABLE AS $$
              SELECT format('FY%s Q%s', fy, fq);
            $$
            """
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\nExecuting helper {i}/{len(queries)}...")
            if self.db.execute_ddl(query):
                print(f"✅ Helper {i} created")
            else:
                print(f"❌ ERROR at helper {i}")
                return False
        
        # Verify
        print("\nVerifying helpers...")
        verify1 = "SELECT * FROM vw_latest_company_quarter ORDER BY company_id"
        result1 = self.db.execute_query(verify1)
        print(f"Latest quarters: {len(result1)} companies")
        
        verify2 = "SELECT fmt_fyq(2025,2) as label"
        result2 = self.db.execute_query(verify2)
        print(f"FYQ formatter: {result2['label'].iloc[0]}")
        
        print("\n✅ Helpers created!")
        return True
    
    def prompt_c_growth_layers(self):
        """Prompt C: Growth layers (QoQ/YoY/TTM delta, Annual YoY & CAGR)"""
        print("\n" + "="*80)
        print("PROMPT C: GROWTH LAYERS")
        print("="*80)
        
        queries = [
            # Quarterly growth
            """
            CREATE OR REPLACE VIEW vw_growth_quarter AS
            WITH q AS (
              SELECT
                cq.*,
                LAG(revenue)      OVER (PARTITION BY company_id ORDER BY fiscal_year, fiscal_quarter) AS rev_prev_q,
                LAG(net_income)   OVER (PARTITION BY company_id ORDER BY fiscal_year, fiscal_quarter) AS ni_prev_q,
                LAG(revenue,4)    OVER (PARTITION BY company_id ORDER BY fiscal_year, fiscal_quarter) AS rev_prev_y,
                LAG(net_income,4) OVER (PARTITION BY company_id ORDER BY fiscal_year, fiscal_quarter) AS ni_prev_y
              FROM vw_company_quarter cq
            )
            SELECT
              q.*,
              CASE WHEN NULLIF(rev_prev_q,0) IS NULL THEN NULL ELSE (q.revenue - rev_prev_q)/rev_prev_q END AS revenue_qoq,
              CASE WHEN NULLIF(ni_prev_q,0)  IS NULL THEN NULL ELSE (q.net_income - ni_prev_q)/ni_prev_q END AS net_income_qoq,
              CASE WHEN NULLIF(rev_prev_y,0) IS NULL THEN NULL ELSE (q.revenue - rev_prev_y)/rev_prev_y END AS revenue_yoy,
              CASE WHEN NULLIF(ni_prev_y,0)  IS NULL THEN NULL ELSE (q.net_income - ni_prev_y)/ni_prev_y END AS net_income_yoy
            FROM q
            """,
            
            # TTM growth deltas
            """
            CREATE OR REPLACE VIEW vw_growth_ttm AS
            WITH t AS (
              SELECT
                f.*,
                LAG(revenue_ttm)    OVER (PARTITION BY company_id ORDER BY fiscal_year, fiscal_quarter) AS rev_ttm_prev,
                LAG(net_income_ttm) OVER (PARTITION BY company_id ORDER BY fiscal_year, fiscal_quarter) AS ni_ttm_prev
              FROM mv_financials_ttm f
            )
            SELECT
              t.*,
              CASE WHEN NULLIF(rev_ttm_prev,0) IS NULL THEN NULL ELSE (t.revenue_ttm - rev_ttm_prev)/rev_ttm_prev END AS revenue_ttm_delta,
              CASE WHEN NULLIF(ni_ttm_prev,0)  IS NULL THEN NULL ELSE (t.net_income_ttm - ni_ttm_prev)/ni_ttm_prev END AS net_income_ttm_delta
            FROM t
            """,
            
            # Annual YoY + CAGR
            """
            CREATE OR REPLACE VIEW vw_growth_annual AS
            WITH a AS (
              SELECT
                f.*,
                LAG(revenue_annual)    OVER (PARTITION BY company_id ORDER BY fiscal_year) AS rev_prev_year,
                LAG(net_income_annual) OVER (PARTITION BY company_id ORDER BY fiscal_year) AS ni_prev_year,
                LAG(revenue_annual,3)  OVER (PARTITION BY company_id ORDER BY fiscal_year) AS rev_3y_ago,
                LAG(revenue_annual,5)  OVER (PARTITION BY company_id ORDER BY fiscal_year) AS rev_5y_ago
              FROM mv_financials_annual f
            )
            SELECT
              a.*,
              CASE WHEN NULLIF(rev_prev_year,0) IS NULL THEN NULL ELSE (a.revenue_annual - rev_prev_year)/rev_prev_year END AS revenue_yoy,
              CASE WHEN NULLIF(ni_prev_year,0)  IS NULL THEN NULL ELSE (a.net_income_annual - ni_prev_year)/ni_prev_year END AS net_income_yoy,
              CASE WHEN rev_3y_ago IS NULL OR rev_3y_ago <= 0 OR a.revenue_annual <= 0 THEN NULL
                   ELSE POWER(a.revenue_annual / rev_3y_ago, 1.0/3) - 1 END AS revenue_cagr_3y,
              CASE WHEN rev_5y_ago IS NULL OR rev_5y_ago <= 0 OR a.revenue_annual <= 0 THEN NULL
                   ELSE POWER(a.revenue_annual / rev_5y_ago, 1.0/5) - 1 END AS revenue_cagr_5y
            FROM a
            """
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\nExecuting growth view {i}/{len(queries)}...")
            if self.db.execute_ddl(query):
                print(f"✅ Growth view {i} created")
            else:
                print(f"❌ ERROR at growth view {i}")
                return False
        
        # Verify
        print("\nVerifying growth views...")
        verify1 = "SELECT * FROM vw_growth_quarter LIMIT 5"
        result1 = self.db.execute_query(verify1)
        print(f"Quarterly growth: {len(result1)} rows")
        
        verify2 = "SELECT * FROM vw_growth_annual LIMIT 5"
        result2 = self.db.execute_query(verify2)
        print(f"Annual growth: {len(result2)} rows")
        
        print("\n✅ Growth layers created!")
        return True
    
    def prompt_d_peer_stats(self):
        """Prompt D: Peer stats (ranks, percentiles, z-scores)"""
        print("\n" + "="*80)
        print("PROMPT D: PEER STATISTICS")
        print("="*80)
        
        queries = [
            # Quarterly peer stats
            """
            CREATE OR REPLACE VIEW vw_peer_stats_quarter AS
            WITH pg AS (
              SELECT peer_group_id FROM dim_peer_group WHERE name='ALL_COMPANIES'
            ),
            universe AS (
              SELECT b.peer_group_id, cq.*
              FROM vw_company_quarter cq
              JOIN pg ON TRUE
              JOIN bridge_company_peer_group b ON b.company_id=cq.company_id AND b.peer_group_id=pg.peer_group_id
            )
            SELECT
              u.peer_group_id,
              u.company_id, u.fiscal_year, u.fiscal_quarter,
              u.revenue, u.net_income, u.operating_income, u.gross_profit,
              u.gross_margin, u.operating_margin, u.net_margin, u.roe, u.roa,
              RANK()      OVER (PARTITION BY peer_group_id, fiscal_year, fiscal_quarter ORDER BY u.revenue DESC)        AS rank_revenue,
              CUME_DIST() OVER (PARTITION BY peer_group_id, fiscal_year, fiscal_quarter ORDER BY u.revenue)              AS pct_revenue,
              (u.revenue - AVG(u.revenue) OVER (PARTITION BY peer_group_id, fiscal_year, fiscal_quarter))
                / NULLIF(STDDEV_POP(u.revenue) OVER (PARTITION BY peer_group_id, fiscal_year, fiscal_quarter),0)        AS z_revenue,
              RANK()      OVER (PARTITION BY peer_group_id, fiscal_year, fiscal_quarter ORDER BY u.net_margin DESC)      AS rank_net_margin,
              CUME_DIST() OVER (PARTITION BY peer_group_id, fiscal_year, fiscal_quarter ORDER BY u.net_margin)           AS pct_net_margin,
              (u.net_margin - AVG(u.net_margin) OVER (PARTITION BY peer_group_id, fiscal_year, fiscal_quarter))
                / NULLIF(STDDEV_POP(u.net_margin) OVER (PARTITION BY peer_group_id, fiscal_year, fiscal_quarter),0)     AS z_net_margin,
              RANK()      OVER (PARTITION BY peer_group_id, fiscal_year, fiscal_quarter ORDER BY u.roe DESC)             AS rank_roe,
              CUME_DIST() OVER (PARTITION BY peer_group_id, fiscal_year, fiscal_quarter ORDER BY u.roe)                  AS pct_roe
            FROM universe u
            """,
            
            # Annual peer stats
            """
            CREATE OR REPLACE VIEW vw_peer_stats_annual AS
            WITH pg AS (
              SELECT peer_group_id FROM dim_peer_group WHERE name='ALL_COMPANIES'
            ),
            universe AS (
              SELECT b.peer_group_id, a.company_id, a.fiscal_year,
                     a.revenue_annual, a.net_income_annual, a.operating_income_annual,
                     a.gross_profit_annual, 
                     r.gross_margin_annual, r.operating_margin_annual, r.net_margin_annual,
                     r.roe_annual_avg_equity, r.roa_annual
              FROM mv_financials_annual a
              JOIN mv_ratios_annual r USING (company_id, fiscal_year)
              JOIN pg ON TRUE
              JOIN bridge_company_peer_group b ON b.company_id=a.company_id AND b.peer_group_id=pg.peer_group_id
            )
            SELECT
              u.peer_group_id,
              u.company_id, u.fiscal_year,
              u.revenue_annual, u.net_income_annual, u.operating_income_annual,
              u.gross_profit_annual, u.gross_margin_annual, u.operating_margin_annual, u.net_margin_annual,
              u.roe_annual_avg_equity, u.roa_annual,
              RANK()      OVER (PARTITION BY peer_group_id, fiscal_year ORDER BY u.revenue_annual DESC) AS rank_revenue_annual,
              CUME_DIST() OVER (PARTITION BY peer_group_id, fiscal_year ORDER BY u.revenue_annual)       AS pct_revenue_annual,
              (u.revenue_annual - AVG(u.revenue_annual) OVER (PARTITION BY peer_group_id, fiscal_year))
                / NULLIF(STDDEV_POP(u.revenue_annual) OVER (PARTITION BY peer_group_id, fiscal_year),0)  AS z_revenue_annual
            FROM universe u
            """
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\nExecuting peer stats view {i}/{len(queries)}...")
            if self.db.execute_ddl(query):
                print(f"✅ Peer stats view {i} created")
            else:
                print(f"❌ ERROR at peer stats view {i}")
                return False
        
        # Verify
        print("\nVerifying peer stats...")
        verify = "SELECT * FROM vw_peer_stats_quarter ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC LIMIT 5"
        result = self.db.execute_query(verify)
        print(f"Peer stats quarterly: {len(result)} rows")
        
        print("\n✅ Peer statistics created!")
        return True
    
    def prompt_e_health_checks(self):
        """Prompt E: Health checks & outliers"""
        print("\n" + "="*80)
        print("PROMPT E: HEALTH CHECKS & OUTLIERS")
        print("="*80)
        
        queries = [
            # Financial health
            """
            CREATE OR REPLACE VIEW vw_financial_health_quarter AS
            SELECT
              company_id, fiscal_year, fiscal_quarter,
              total_assets, total_liabilities, equity,
              (total_liabilities + equity) AS liabilities_plus_equity,
              (total_assets - (total_liabilities + equity)) AS balance_gap,
              CASE WHEN ABS(COALESCE(total_assets,0) - COALESCE(total_liabilities,0) - COALESCE(equity,0))
                        <= GREATEST(ABS(total_assets)*0.005, 1000000)
                   THEN 'within_tolerance' ELSE 'out_of_balance' END AS balance_status,
              CASE WHEN equity < 0 THEN 1 ELSE 0 END AS flag_negative_equity,
              CASE WHEN net_income < 0 THEN 1 ELSE 0 END AS flag_net_loss
            FROM vw_company_quarter
            """,
            
            # Outliers
            """
            CREATE OR REPLACE VIEW vw_outliers_quarter AS
            WITH s AS (
              SELECT
                company_id, fiscal_year, fiscal_quarter, revenue, net_margin,
                AVG(revenue)   OVER (PARTITION BY company_id) AS mu_rev,
                STDDEV_POP(revenue) OVER (PARTITION BY company_id) AS sd_rev,
                AVG(net_margin) OVER (PARTITION BY company_id) AS mu_nm,
                STDDEV_POP(net_margin) OVER (PARTITION BY company_id) AS sd_nm
              FROM vw_company_quarter
            )
            SELECT *,
              CASE WHEN sd_rev=0 OR sd_rev IS NULL THEN NULL ELSE (revenue - mu_rev)/sd_rev END AS z_rev,
              CASE WHEN sd_nm=0 OR sd_nm IS NULL THEN NULL ELSE (net_margin - mu_nm)/sd_nm END AS z_nm,
              CASE WHEN ABS(CASE WHEN sd_rev=0 OR sd_rev IS NULL THEN 0 ELSE (revenue - mu_rev)/sd_rev END) >= 3 THEN 1 ELSE 0 END AS outlier_revenue_3sigma,
              CASE WHEN ABS(CASE WHEN sd_nm=0 OR sd_nm IS NULL THEN 0 ELSE (net_margin - mu_nm)/sd_nm END) >= 3 THEN 1 ELSE 0 END AS outlier_net_margin_3sigma
            FROM s
            """
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\nExecuting health check view {i}/{len(queries)}...")
            if self.db.execute_ddl(query):
                print(f"✅ Health check view {i} created")
            else:
                print(f"❌ ERROR at health check view {i}")
                return False
        
        # Verify
        print("\nVerifying health checks...")
        verify1 = "SELECT * FROM vw_financial_health_quarter ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC LIMIT 5"
        result1 = self.db.execute_query(verify1)
        print(f"Financial health: {len(result1)} rows")
        
        verify2 = "SELECT * FROM vw_outliers_quarter WHERE outlier_revenue_3sigma=1 OR outlier_net_margin_3sigma=1"
        result2 = self.db.execute_query(verify2)
        print(f"Outliers detected: {len(result2)} rows")
        
        print("\n✅ Health checks created!")
        return True
    
    def prompt_f_macro_sensitivities(self):
        """Prompt F: Macro sensitivities (rolling regressions)"""
        print("\n" + "="*80)
        print("PROMPT F: MACRO SENSITIVITIES")
        print("="*80)
        
        query = """
        CREATE OR REPLACE VIEW vw_macro_sensitivity_rolling AS
        WITH base AS (
          SELECT
            m.company_id, m.fiscal_year, m.fiscal_quarter,
            m.gross_margin, m.operating_margin, m.net_margin,
            m.cpi, m.fed_funds_rate, m.sp500_index, m.unemployment_rate
          FROM vw_company_quarter_macro m
        ),
        roll AS (
          SELECT
            b.*,
            REGR_SLOPE(gross_margin, cpi)                OVER w AS beta_gm_cpi_12q,
            REGR_SLOPE(operating_margin, cpi)            OVER w AS beta_om_cpi_12q,
            REGR_SLOPE(net_margin, cpi)                  OVER w AS beta_nm_cpi_12q,
            REGR_SLOPE(gross_margin, fed_funds_rate)     OVER w AS beta_gm_ffr_12q,
            REGR_SLOPE(operating_margin, fed_funds_rate) OVER w AS beta_om_ffr_12q,
            REGR_SLOPE(net_margin, fed_funds_rate)       OVER w AS beta_nm_ffr_12q,
            REGR_SLOPE(net_margin, sp500_index)          OVER w AS beta_nm_spx_12q,
            REGR_SLOPE(net_margin, unemployment_rate)    OVER w AS beta_nm_unrate_12q
          FROM base b
          WINDOW w AS (
            PARTITION BY company_id
            ORDER BY fiscal_year, fiscal_quarter
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
          )
        )
        SELECT * FROM roll
        """
        
        print("\nExecuting macro sensitivity view...")
        if self.db.execute_ddl(query):
            print("✅ Macro sensitivity view created")
        else:
            print("❌ ERROR creating macro sensitivity view")
            return False
        
        # Verify
        print("\nVerifying macro sensitivities...")
        verify = "SELECT * FROM vw_macro_sensitivity_rolling ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC LIMIT 10"
        result = self.db.execute_query(verify)
        print(f"Macro sensitivities: {len(result)} rows")
        
        print("\n✅ Macro sensitivities created!")
        return True
    
    def prompt_g_final_answer_surface(self):
        """Prompt G: Final LLM answer surface"""
        print("\n" + "="*80)
        print("PROMPT G: FINAL CFO ANSWER SURFACE")
        print("="*80)
        
        query = """
        CREATE OR REPLACE VIEW vw_cfo_answers AS
        SELECT
          cq.company_id, dc.ticker, dc.name,
          cq.fiscal_year, cq.fiscal_quarter, fmt_fyq(cq.fiscal_year, cq.fiscal_quarter) AS fyq_label,
          -- core
          cq.revenue, cq.gross_profit, cq.operating_income, cq.net_income,
          cq.total_assets, cq.total_liabilities, cq.equity, cq.capex,
          cq.gross_margin, cq.operating_margin, cq.net_margin, cq.roe, cq.roa,
          -- growth
          gq.revenue_qoq, gq.net_income_qoq, gq.revenue_yoy, gq.net_income_yoy,
          gt.revenue_ttm, gt.net_income_ttm, gt.revenue_ttm_delta, gt.net_income_ttm_delta,
          -- peer standings
          psq.rank_revenue, psq.pct_revenue, psq.z_revenue,
          psq.rank_net_margin, psq.pct_net_margin, psq.z_net_margin, psq.rank_roe, psq.pct_roe,
          -- macro sensitivities
          ms.beta_nm_cpi_12q, ms.beta_nm_ffr_12q, ms.beta_nm_spx_12q, ms.beta_nm_unrate_12q,
          -- GP reconciliation transparency
          cq.gross_profit_source, cq.delta_abs AS gp_delta_abs, cq.delta_pct AS gp_delta_pct
        FROM vw_company_quarter cq
        JOIN dim_company dc USING (company_id)
        LEFT JOIN vw_growth_quarter gq USING (company_id, fiscal_year, fiscal_quarter)
        LEFT JOIN vw_growth_ttm gt USING (company_id, fiscal_year, fiscal_quarter)
        LEFT JOIN vw_peer_stats_quarter psq USING (company_id, fiscal_year, fiscal_quarter)
        LEFT JOIN vw_macro_sensitivity_rolling ms USING (company_id, fiscal_year, fiscal_quarter)
        """
        
        print("\nExecuting final answer surface view...")
        if self.db.execute_ddl(query):
            print("✅ CFO answer surface created")
        else:
            print("❌ ERROR creating CFO answer surface")
            return False
        
        # Add comment
        comment = """
        COMMENT ON VIEW vw_cfo_answers IS
          'Per-company per-quarter KPIs, growth (QoQ/YoY/TTM), peer ranks/percentiles/z-scores, macro sensitivities, and GP reconciliation flags.'
        """
        self.db.execute_ddl(comment)
        
        # Verify
        print("\nVerifying CFO answer surface...")
        verify = "SELECT ticker, fyq_label, revenue, net_margin, rank_revenue, rank_net_margin FROM vw_cfo_answers ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC LIMIT 10"
        result = self.db.execute_query(verify)
        print(result.to_string(index=False))
        
        print("\n✅ Final CFO answer surface created!")
        return True
    
    def prompt_h_refresh_and_smoke_tests(self):
        """Prompt H: Refresh helpers & smoke tests"""
        print("\n" + "="*80)
        print("PROMPT H: REFRESH & SMOKE TESTS")
        print("="*80)
        
        # Refresh MVs
        print("\nRefreshing materialized views...")
        refresh_queries = [
            "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_financials_annual",
            "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_financials_ttm",
            "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ratios_annual",
            "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ratios_ttm"
        ]
        
        for query in refresh_queries:
            print(f"Refreshing {query.split()[-1]}...")
            self.db.execute_ddl(query)
        
        # Smoke tests
        print("\n" + "-"*80)
        print("SMOKE TESTS")
        print("-"*80)
        
        tests = [
            ("1. Apple ROE 2022 (annual, avg equity)", """
                SELECT c.ticker, r.fiscal_year, r.roe_annual_avg_equity
                FROM mv_ratios_annual r
                JOIN dim_company c USING (company_id)
                WHERE c.ticker='AAPL' AND r.fiscal_year=2022
            """),
            
            ("2. Apple revenue & net income 2022 (annual sums)", """
                SELECT c.ticker, a.fiscal_year, a.revenue_annual, a.net_income_annual
                FROM mv_financials_annual a
                JOIN dim_company c USING (company_id)
                WHERE c.ticker='AAPL' AND a.fiscal_year=2022
            """),
            
            ("3. Who leads on net margin last quarter (peer ranks)", """
                SELECT c.ticker, p.fiscal_year, p.fiscal_quarter, p.net_margin, p.rank_net_margin
                FROM vw_peer_stats_quarter p
                JOIN dim_company c USING (company_id)
                WHERE (fiscal_year, fiscal_quarter) = (SELECT fiscal_year, fiscal_quarter FROM vw_peer_stats_quarter ORDER BY fiscal_year DESC, fiscal_quarter DESC LIMIT 1)
                ORDER BY rank_net_margin ASC
                LIMIT 5
            """),
            
            ("4. Macro sensitivity preview (latest)", """
                SELECT company_id, fiscal_year, fiscal_quarter, 
                       ROUND(beta_nm_cpi_12q::numeric, 4) as beta_cpi,
                       ROUND(beta_nm_ffr_12q::numeric, 4) as beta_ffr
                FROM vw_macro_sensitivity_rolling
                ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC
                LIMIT 10
            """)
        ]
        
        for test_name, query in tests:
            print(f"\n{test_name}")
            result = self.db.execute_query(query)
            if result.empty:
                print("   ⚠️ No results")
            else:
                print(f"   ✅ Passed ({len(result)} rows)")
                print(result.to_string(index=False)[:300])
        
        print("\n✅ Refresh and smoke tests complete!")
        return True
    
    def run_all(self):
        """Execute all advanced migration prompts A-H"""
        print("\n" + "="*80)
        print("STARTING ADVANCED DATABASE MIGRATION (PROMPTS A-H)")
        print("="*80)
        
        prompts = [
            ("A", self.prompt_a_peer_groups),
            ("B", self.prompt_b_helpers),
            ("C", self.prompt_c_growth_layers),
            ("D", self.prompt_d_peer_stats),
            ("E", self.prompt_e_health_checks),
            ("F", self.prompt_f_macro_sensitivities),
            ("G", self.prompt_g_final_answer_surface),
            ("H", self.prompt_h_refresh_and_smoke_tests)
        ]
        
        for prompt_name, prompt_func in prompts:
            if not prompt_func():
                print(f"\n❌ Migration stopped at Prompt {prompt_name}")
                return False
        
        print("\n" + "="*80)
        print("✅ ADVANCED MIGRATION COMPLETE!")
        print("="*80)
        print("\n🎉 All advanced features ready:")
        print("   - Peer groups & rankings")
        print("   - Growth calculations (QoQ/YoY/TTM/CAGR)")
        print("   - Peer statistics (ranks, percentiles, z-scores)")
        print("   - Health checks & outlier detection")
        print("   - Macro sensitivities (rolling regressions)")
        print("   - vw_cfo_answers (unified answer surface)")
        return True


if __name__ == "__main__":
    migration = AdvancedMigration()
    migration.run_all()
