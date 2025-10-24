"""
Data Governance & Provenance Migration - Prompts 1-5
Fiscal calendar, source tracking, citations, metric dictionary, and agent guardrails
"""

from database import SupabaseConnector

class GovernanceMigration:
    def __init__(self):
        self.db = SupabaseConnector()
    
    def prompt_1_fiscal_calendar(self):
        """Prompt 1: Fiscal calendar spine + macro overlay re-point"""
        print("\n" + "="*80)
        print("PROMPT 1: FISCAL CALENDAR & MACRO OVERLAY")
        print("="*80)
        
        queries = [
            # 1A: Fiscal calendar spine
            """
            CREATE TABLE IF NOT EXISTS dim_fiscal_calendar (
              company_id int REFERENCES dim_company(company_id) ON DELETE CASCADE,
              fiscal_year int NOT NULL,
              fiscal_quarter int NOT NULL CHECK (fiscal_quarter BETWEEN 1 AND 4),
              quarter_start date NOT NULL,
              quarter_end   date NOT NULL,
              PRIMARY KEY(company_id, fiscal_year, fiscal_quarter)
            )
            """,
            
            """
            INSERT INTO dim_fiscal_calendar (company_id, fiscal_year, fiscal_quarter, quarter_start, quarter_end)
            SELECT DISTINCT f.company_id, f.fiscal_year, f.fiscal_quarter,
                   (date_trunc('quarter', make_date(f.fiscal_year, 3*f.fiscal_quarter, 1)))::date AS quarter_start,
                   (date_trunc('quarter', make_date(f.fiscal_year, 3*f.fiscal_quarter, 1)) + interval '3 months - 1 day')::date AS quarter_end
            FROM fact_financials f
            ON CONFLICT DO NOTHING
            """,
            
            """
            CREATE OR REPLACE VIEW vw_quarter_end AS
            SELECT company_id, fiscal_year, fiscal_quarter, quarter_end
            FROM dim_fiscal_calendar
            """,
            
            # 1B: Re-point macro overlay
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
            JOIN vw_quarter_end qd
              USING (company_id, fiscal_year, fiscal_quarter)
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
        print("\nVerifying fiscal calendar...")
        verify1 = "SELECT * FROM vw_quarter_end ORDER BY company_id, fiscal_year, fiscal_quarter LIMIT 10"
        result1 = self.db.execute_query(verify1)
        print(f"Quarter end dates: {len(result1)} rows")
        
        verify2 = """
        SELECT company_id, fiscal_year, fiscal_quarter, cpi, fed_funds_rate, sp500_index
        FROM vw_company_quarter_macro
        ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC
        LIMIT 10
        """
        result2 = self.db.execute_query(verify2)
        print(f"Macro overlay: {len(result2)} rows")
        
        print("\n✅ Fiscal calendar and macro overlay created!")
        return True
    
    def prompt_2_provenance(self):
        """Prompt 2: Provenance - sources + columns + backfill"""
        print("\n" + "="*80)
        print("PROMPT 2: PROVENANCE & SOURCE TRACKING")
        print("="*80)
        
        queries = [
            # 2A: Source registry
            """
            CREATE TABLE IF NOT EXISTS dim_data_source (
              source_id serial PRIMARY KEY,
              code text UNIQUE NOT NULL,
              name text,
              description text
            )
            """,
            
            """
            INSERT INTO dim_data_source (code, name, description) VALUES
             ('ALPHAVANTAGE_FIN','Alpha Vantage Financials','Quarterly financial statements'),
             ('FRED','Federal Reserve Economic Data','US macro indicators'),
             ('YF','Yahoo Finance','Stock prices & market data')
            ON CONFLICT (code) DO NOTHING
            """,
            
            # 2B: Add provenance columns
            """
            ALTER TABLE fact_financials
              ADD COLUMN IF NOT EXISTS source_id int REFERENCES dim_data_source(source_id),
              ADD COLUMN IF NOT EXISTS as_reported boolean DEFAULT true,
              ADD COLUMN IF NOT EXISTS version_ts timestamptz DEFAULT now()
            """,
            
            """
            ALTER TABLE fact_stock_prices
              ADD COLUMN IF NOT EXISTS source_id int REFERENCES dim_data_source(source_id),
              ADD COLUMN IF NOT EXISTS version_ts timestamptz DEFAULT now()
            """,
            
            """
            ALTER TABLE fact_macro_indicators
              ADD COLUMN IF NOT EXISTS source_id int REFERENCES dim_data_source(source_id),
              ADD COLUMN IF NOT EXISTS version_ts timestamptz DEFAULT now()
            """,
            
            # 2C: Backfill sources
            """
            UPDATE fact_financials f
            SET source_id = (SELECT source_id FROM dim_data_source WHERE code='ALPHAVANTAGE_FIN')
            WHERE f.source_id IS NULL
            """,
            
            """
            UPDATE fact_stock_prices s
            SET source_id = (SELECT source_id FROM dim_data_source WHERE code='YF')
            WHERE s.source_id IS NULL
            """,
            
            """
            UPDATE fact_macro_indicators m
            SET source_id = (SELECT source_id FROM dim_data_source WHERE code='FRED')
            WHERE m.source_id IS NULL
            """,
            
            # 2D: Lineage log
            """
            CREATE TABLE IF NOT EXISTS etl_lineage_log (
              lineage_id bigserial PRIMARY KEY,
              table_name text NOT NULL,
              company_id int,
              fiscal_year int,
              fiscal_quarter int,
              source_id int REFERENCES dim_data_source(source_id),
              op text NOT NULL,
              loaded_at timestamptz DEFAULT now(),
              extra jsonb
            )
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
        print("\nVerifying provenance...")
        verify1 = "SELECT code, source_id FROM dim_data_source ORDER BY source_id"
        result1 = self.db.execute_query(verify1)
        print("Data sources:")
        print(result1.to_string(index=False))
        
        verify2 = "SELECT COUNT(*) AS fin_missing_source FROM fact_financials WHERE source_id IS NULL"
        result2 = self.db.execute_query(verify2)
        print(f"\nFinancials missing source: {result2['fin_missing_source'].iloc[0]}")
        
        verify3 = "SELECT COUNT(*) AS stk_missing_source FROM fact_stock_prices WHERE source_id IS NULL"
        result3 = self.db.execute_query(verify3)
        print(f"Stock prices missing source: {result3['stk_missing_source'].iloc[0]}")
        
        verify4 = "SELECT COUNT(*) AS macro_missing_source FROM fact_macro_indicators WHERE source_id IS NULL"
        result4 = self.db.execute_query(verify4)
        print(f"Macro indicators missing source: {result4['macro_missing_source'].iloc[0]}")
        
        print("\n✅ Provenance tracking created!")
        return True
    
    def prompt_3_citations(self):
        """Prompt 3: Citations views (financials, stock, macro)"""
        print("\n" + "="*80)
        print("PROMPT 3: CITATIONS VIEWS")
        print("="*80)
        
        queries = [
            # Financials citations
            """
            CREATE OR REPLACE VIEW vw_fact_citations AS
            SELECT
              f.company_id, c.ticker, f.fiscal_year, f.fiscal_quarter,
              q.quarter_end,
              f.revenue, f.cogs, f.gross_profit, f.operating_income, f.net_income,
              f.total_assets, f.total_liabilities, f.equity, f.capex,
              f.as_reported, f.version_ts,
              ds.source_id, ds.code AS source_code, ds.name AS source_name
            FROM fact_financials f
            JOIN dim_company c USING (company_id)
            JOIN vw_quarter_end q USING (company_id, fiscal_year, fiscal_quarter)
            LEFT JOIN dim_data_source ds ON ds.source_id=f.source_id
            """,
            
            # Stock citations
            """
            CREATE OR REPLACE VIEW vw_stock_citations AS
            SELECT
              s.company_id, c.ticker, s.fiscal_year, s.fiscal_quarter,
              q.quarter_end,
              s.close_price, s.return_qoq, s.return_yoy, s.volatility_pct,
              s.version_ts,
              ds.source_id, ds.code AS source_code, ds.name AS source_name
            FROM fact_stock_prices s
            JOIN dim_company c USING (company_id)
            JOIN vw_quarter_end q USING (company_id, fiscal_year, fiscal_quarter)
            LEFT JOIN dim_data_source ds ON ds.source_id=s.source_id
            """,
            
            # Macro citations
            """
            CREATE OR REPLACE VIEW vw_macro_citations AS
            SELECT
              m.indicator_id, dmi.code AS indicator_code, dmi.name AS indicator_name,
              m.date AS quarter_end, m.value,
              m.version_ts,
              ds.source_id, ds.code AS source_code, ds.name AS source_name
            FROM fact_macro_indicators m
            JOIN dim_macro_indicator dmi USING (indicator_id)
            LEFT JOIN dim_data_source ds ON ds.source_id=m.source_id
            """
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\nExecuting citations view {i}/{len(queries)}...")
            if self.db.execute_ddl(query):
                print(f"✅ Citations view {i} created")
            else:
                print(f"❌ ERROR at citations view {i}")
                return False
        
        # Verify
        print("\nVerifying citations views...")
        verify1 = "SELECT * FROM vw_fact_citations ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC LIMIT 5"
        result1 = self.db.execute_query(verify1)
        print(f"Fact citations: {len(result1)} rows")
        
        verify2 = "SELECT * FROM vw_stock_citations ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC LIMIT 5"
        result2 = self.db.execute_query(verify2)
        print(f"Stock citations: {len(result2)} rows")
        
        verify3 = "SELECT * FROM vw_macro_citations ORDER BY quarter_end DESC, indicator_code LIMIT 5"
        result3 = self.db.execute_query(verify3)
        print(f"Macro citations: {len(result3)} rows")
        
        print("\n✅ Citations views created!")
        return True
    
    def prompt_4_metric_dictionary(self):
        """Prompt 4: Metric dictionary enrichment (synonyms, tags)"""
        print("\n" + "="*80)
        print("PROMPT 4: METRIC DICTIONARY ENRICHMENT")
        print("="*80)
        
        queries = [
            # Add synonym columns
            """
            ALTER TABLE dim_financial_metric
              ADD COLUMN IF NOT EXISTS synonyms text[] DEFAULT '{}',
              ADD COLUMN IF NOT EXISTS xbrl_tags text[] DEFAULT '{}'
            """,
            
            """
            ALTER TABLE dim_ratio
              ADD COLUMN IF NOT EXISTS synonyms text[] DEFAULT '{}'
            """,
            
            # Unified metric dictionary
            """
            CREATE OR REPLACE VIEW vw_metric_dictionary AS
            SELECT 'financial' AS kind, code, name, unit, category, description, synonyms, xbrl_tags
            FROM dim_financial_metric
            UNION ALL
            SELECT 'ratio', code, name, unit, category, description, synonyms, '{}'::text[]
            FROM dim_ratio
            UNION ALL
            SELECT 'macro', code, name, unit, 'Macro' AS category, description, '{}'::text[], '{}'::text[]
            FROM dim_macro_indicator
            UNION ALL
            SELECT 'stock', code, name, unit, category, description, '{}'::text[], '{}'::text[]
            FROM dim_stock_metric
            """,
            
            # Seed synonyms
            """
            UPDATE dim_financial_metric
            SET synonyms = ARRAY['sales','top line','total revenue']
            WHERE code='REVENUE'
            """,
            
            """
            UPDATE dim_financial_metric
            SET synonyms = ARRAY['cost of revenue','costs of goods sold']
            WHERE code='COGS'
            """,
            
            """
            UPDATE dim_ratio
            SET synonyms = ARRAY['leverage','leverage ratio']
            WHERE code='DEBT_TO_EQUITY'
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
        print("\nVerifying metric dictionary...")
        verify = "SELECT * FROM vw_metric_dictionary WHERE code IN ('REVENUE','COGS','DEBT_TO_EQUITY') LIMIT 10"
        result = self.db.execute_query(verify)
        print(result.to_string(index=False))
        
        print("\n✅ Metric dictionary enriched!")
        return True
    
    def prompt_5_agent_guardrails(self):
        """Prompt 5: Agent guardrails (DB-level whitelist + schema cache)"""
        print("\n" + "="*80)
        print("PROMPT 5: AGENT GUARDRAILS")
        print("="*80)
        
        queries = [
            # Whitelist table
            """
            CREATE TABLE IF NOT EXISTS agent_allowed_surfaces (
              surface_name text PRIMARY KEY
            )
            """,
            
            # Populate whitelist
            """
            INSERT INTO agent_allowed_surfaces(surface_name) VALUES
             ('vw_cfo_answers'),
             ('vw_company_quarter'),
             ('vw_company_quarter_macro'),
             ('vw_growth_quarter'),
             ('vw_growth_ttm'),
             ('vw_growth_annual'),
             ('vw_peer_stats_quarter'),
             ('vw_peer_stats_annual'),
             ('vw_financial_health_quarter'),
             ('vw_outliers_quarter'),
             ('vw_macro_sensitivity_rolling'),
             ('mv_financials_annual'),
             ('mv_financials_ttm'),
             ('mv_ratios_annual'),
             ('mv_ratios_ttm'),
             ('vw_fact_citations'),
             ('vw_stock_citations'),
             ('vw_macro_citations')
            ON CONFLICT DO NOTHING
            """,
            
            # Schema cache
            """
            CREATE OR REPLACE VIEW vw_schema_cache AS
            SELECT
              a.surface_name,
              c.column_name,
              c.data_type
            FROM agent_allowed_surfaces a
            JOIN information_schema.columns c
              ON c.table_schema='public' AND c.table_name=a.surface_name
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
        print("\nVerifying agent guardrails...")
        verify1 = "SELECT COUNT(*) as allowed_surfaces FROM agent_allowed_surfaces"
        result1 = self.db.execute_query(verify1)
        print(f"Allowed surfaces: {result1['allowed_surfaces'].iloc[0]}")
        
        verify2 = "SELECT * FROM vw_schema_cache ORDER BY surface_name, column_name LIMIT 20"
        result2 = self.db.execute_query(verify2)
        print(f"Schema cache entries: {len(result2)} (showing first 20)")
        print(result2.to_string(index=False))
        
        print("\n✅ Agent guardrails created!")
        return True
    
    def run_all(self):
        """Execute all governance migration prompts 1-5"""
        print("\n" + "="*80)
        print("STARTING DATA GOVERNANCE MIGRATION (PROMPTS 1-5)")
        print("="*80)
        
        prompts = [
            ("1", self.prompt_1_fiscal_calendar),
            ("2", self.prompt_2_provenance),
            ("3", self.prompt_3_citations),
            ("4", self.prompt_4_metric_dictionary),
            ("5", self.prompt_5_agent_guardrails)
        ]
        
        for prompt_name, prompt_func in prompts:
            if not prompt_func():
                print(f"\n❌ Migration stopped at Prompt {prompt_name}")
                return False
        
        print("\n" + "="*80)
        print("✅ DATA GOVERNANCE MIGRATION COMPLETE!")
        print("="*80)
        print("\n🎉 All governance features ready:")
        print("   - Fiscal calendar spine (dim_fiscal_calendar)")
        print("   - Macro overlay re-pointed to fiscal calendar")
        print("   - Source tracking (dim_data_source)")
        print("   - Provenance columns (source_id, as_reported, version_ts)")
        print("   - Citations views (vw_fact_citations, vw_stock_citations, vw_macro_citations)")
        print("   - Metric dictionary with synonyms (vw_metric_dictionary)")
        print("   - Agent guardrails (agent_allowed_surfaces, vw_schema_cache)")
        return True


if __name__ == "__main__":
    migration = GovernanceMigration()
    migration.run_all()
