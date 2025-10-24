"""
Database Migration Script for CFO Analytics
Executes structured migration prompts with safety checks
"""

import os
from database import SupabaseConnector
from dotenv import load_dotenv

load_dotenv()

class DatabaseMigration:
    def __init__(self):
        self.db = SupabaseConnector()
        
    def prompt_1_verify_tables(self):
        """Prompt 1: Verify core tables exist"""
        print("\n" + "="*80)
        print("PROMPT 1: VERIFY CORE TABLES")
        print("="*80)
        
        query = """
        SELECT 'dim_company'  AS tbl, to_regclass('public.dim_company')  IS NOT NULL AS exists
        UNION ALL SELECT 'fact_financials',  to_regclass('public.fact_financials')  IS NOT NULL
        UNION ALL SELECT 'fact_ratios',      to_regclass('public.fact_ratios')      IS NOT NULL
        UNION ALL SELECT 'fact_stock_prices',to_regclass('public.fact_stock_prices')IS NOT NULL
        UNION ALL SELECT 'dim_macro_indicator', to_regclass('public.dim_macro_indicator') IS NOT NULL
        UNION ALL SELECT 'fact_macro_indicators',to_regclass('public.fact_macro_indicators') IS NOT NULL
        """
        
        result = self.db.execute_query(query)
        print("\nTable Verification Results:")
        print(result.to_string(index=False))
        
        missing = result[result['exists'] == False]
        if not missing.empty:
            print(f"\n❌ ERROR: Missing tables: {missing['tbl'].tolist()}")
            return False
        
        print("\n✅ All core tables exist!")
        return True
    
    def prompt_2_constraints_indexes(self):
        """Prompt 2: Add constraints, FKs, and indexes"""
        print("\n" + "="*80)
        print("PROMPT 2: CONSTRAINTS, FKS, AND INDEXES")
        print("="*80)
        
        # Execute in transaction
        queries = [
            # NOT NULLs
            """
            ALTER TABLE fact_financials ALTER COLUMN company_id SET NOT NULL,
                                       ALTER COLUMN fiscal_year SET NOT NULL,
                                       ALTER COLUMN fiscal_quarter SET NOT NULL
            """,
            """
            ALTER TABLE fact_ratios ALTER COLUMN company_id SET NOT NULL,
                                   ALTER COLUMN fiscal_year SET NOT NULL,
                                   ALTER COLUMN fiscal_quarter SET NOT NULL
            """,
            """
            ALTER TABLE fact_stock_prices ALTER COLUMN company_id SET NOT NULL,
                                         ALTER COLUMN fiscal_year SET NOT NULL,
                                         ALTER COLUMN fiscal_quarter SET NOT NULL
            """,
            """
            ALTER TABLE fact_macro_indicators ALTER COLUMN indicator_id SET NOT NULL,
                                             ALTER COLUMN date SET NOT NULL
            """,
            
            # Foreign Keys
            """
            DO $$
            BEGIN
              IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='fk_fin_co') THEN
                ALTER TABLE fact_financials ADD CONSTRAINT fk_fin_co FOREIGN KEY (company_id) REFERENCES dim_company(company_id);
              END IF;
              IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='fk_rat_co') THEN
                ALTER TABLE fact_ratios ADD CONSTRAINT fk_rat_co FOREIGN KEY (company_id) REFERENCES dim_company(company_id);
              END IF;
              IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='fk_sp_co') THEN
                ALTER TABLE fact_stock_prices ADD CONSTRAINT fk_sp_co FOREIGN KEY (company_id) REFERENCES dim_company(company_id);
              END IF;
              IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='fk_macro_dim') THEN
                ALTER TABLE fact_macro_indicators ADD CONSTRAINT fk_macro_dim FOREIGN KEY (indicator_id) REFERENCES dim_macro_indicator(indicator_id);
              END IF;
            END $$
            """,
            
            # Unique indexes
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_fact_financials_co_fy_fq ON fact_financials (company_id, fiscal_year, fiscal_quarter)",
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_fact_ratios_co_fy_fq ON fact_ratios (company_id, fiscal_year, fiscal_quarter)",
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_fact_stock_prices_co_fy_fq ON fact_stock_prices (company_id, fiscal_year, fiscal_quarter)",
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_fact_macro_indicator_date ON fact_macro_indicators (indicator_id, date)",
            
            # Hot-path indexes
            "CREATE INDEX IF NOT EXISTS ix_financials_filter ON fact_financials (company_id, fiscal_year DESC, fiscal_quarter DESC)",
            "CREATE INDEX IF NOT EXISTS ix_ratios_filter ON fact_ratios (company_id, fiscal_year DESC, fiscal_quarter DESC)",
            "CREATE INDEX IF NOT EXISTS ix_stock_filter ON fact_stock_prices (company_id, fiscal_year DESC, fiscal_quarter DESC)",
            "CREATE INDEX IF NOT EXISTS ix_macro_filter ON fact_macro_indicators (indicator_id, date DESC)"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\nExecuting step {i}/{len(queries)}...")
            if self.db.execute_ddl(query):
                print(f"✅ Step {i} completed")
            else:
                print(f"❌ ERROR at step {i}")
                return False
        
        # Verify no duplicates
        print("\nVerifying uniqueness...")
        dup_check = """
        SELECT 'fin_dups' AS check, COUNT(*) FROM (
          SELECT company_id, fiscal_year, fiscal_quarter, COUNT(*) c
          FROM fact_financials GROUP BY 1,2,3 HAVING COUNT(*)>1
        ) s
        UNION ALL
        SELECT 'rat_dups', COUNT(*) FROM (
          SELECT company_id, fiscal_year, fiscal_quarter, COUNT(*) c
          FROM fact_ratios GROUP BY 1,2,3 HAVING COUNT(*)>1
        ) s
        UNION ALL
        SELECT 'stk_dups', COUNT(*) FROM (
          SELECT company_id, fiscal_year, fiscal_quarter, COUNT(*) c
          FROM fact_stock_prices GROUP BY 1,2,3 HAVING COUNT(*)>1
        ) s
        UNION ALL
        SELECT 'macro_dups', COUNT(*) FROM (
          SELECT indicator_id, date, COUNT(*) c
          FROM fact_macro_indicators GROUP BY 1,2 HAVING COUNT(*)>1
        ) s
        """
        
        dup_result = self.db.execute_query(dup_check)
        print(dup_result.to_string(index=False))
        
        if dup_result['count'].sum() > 0:
            print("\n❌ ERROR: Duplicates found!")
            return False
        
        print("\n✅ Constraints and indexes applied successfully!")
        return True
    
    def prompt_3_quarter_end_gp_ratios(self):
        """Prompt 3: Quarter-end helper, GP reconciliation, canonical ratios"""
        print("\n" + "="*80)
        print("PROMPT 3: QUARTER-END, GP RECONCILIATION, CANONICAL RATIOS")
        print("="*80)
        
        queries = [
            # Quarter-end view
            """
            CREATE OR REPLACE VIEW vw_qe_date AS
            SELECT
              f.company_id,
              f.fiscal_year,
              f.fiscal_quarter,
              (
                date_trunc('quarter', make_date(f.fiscal_year, 3 * f.fiscal_quarter, 1))
                  + interval '3 months - 1 day'
              )::date AS quarter_end
            FROM fact_financials f
            GROUP BY 1,2,3
            """,
            
            # GP reconciliation
            """
            CREATE OR REPLACE VIEW vw_gross_profit_reconciled AS
            WITH base AS (
              SELECT company_id, fiscal_year, fiscal_quarter,
                     revenue, cogs, gross_profit AS gross_profit_reported,
                     (revenue - cogs) AS gross_profit_computed
              FROM fact_financials
            ),
            cmp AS (
              SELECT *,
                     ABS(gross_profit_reported - gross_profit_computed) AS delta_abs,
                     CASE WHEN NULLIF(revenue,0) IS NULL THEN NULL
                          ELSE ABS(gross_profit_reported - gross_profit_computed) / ABS(revenue)::numeric
                     END AS delta_pct
              FROM base
            )
            SELECT
              company_id, fiscal_year, fiscal_quarter,
              revenue, cogs, gross_profit_reported, gross_profit_computed,
              CASE
                WHEN delta_abs <= 300000000 OR (delta_pct IS NOT NULL AND delta_pct <= 0.005)
                THEN gross_profit_reported ELSE gross_profit_computed END AS gross_profit_authoritative,
              CASE
                WHEN delta_abs <= 300000000 OR (delta_pct IS NOT NULL AND delta_pct <= 0.005)
                THEN 'reported_within_tolerance' ELSE 'computed_due_to_variance' END AS gross_profit_source,
              delta_abs, delta_pct
            FROM cmp
            """,
            
            # Canonical ratios
            """
            CREATE OR REPLACE VIEW vw_ratios_canonical AS
            SELECT
              f.company_id, f.fiscal_year, f.fiscal_quarter,
              CASE WHEN NULLIF(f.equity,0) IS NULL THEN NULL ELSE f.net_income / NULLIF(f.equity,0) END AS roe,
              CASE WHEN NULLIF(f.total_assets,0) IS NULL THEN NULL ELSE f.net_income / NULLIF(f.total_assets,0) END AS roa,
              CASE WHEN NULLIF(f.revenue,0) IS NULL THEN NULL ELSE g.gross_profit_authoritative / NULLIF(f.revenue,0) END AS gross_margin,
              CASE WHEN NULLIF(f.revenue,0) IS NULL THEN NULL ELSE f.operating_income / NULLIF(f.revenue,0) END AS operating_margin,
              CASE WHEN NULLIF(f.revenue,0) IS NULL THEN NULL ELSE f.net_income / NULLIF(f.revenue,0) END AS net_margin,
              CASE WHEN NULLIF(f.equity,0) IS NULL THEN NULL ELSE f.total_liabilities / NULLIF(f.equity,0) END AS debt_to_equity,
              CASE WHEN NULLIF(f.total_assets,0) IS NULL THEN NULL ELSE f.total_liabilities / NULLIF(f.total_assets,0) END AS debt_to_assets,
              CASE WHEN NULLIF(f.revenue,0) IS NULL THEN NULL ELSE f.r_and_d_expenses / NULLIF(f.revenue,0) END AS rnd_to_revenue,
              CASE WHEN NULLIF(f.revenue,0) IS NULL THEN NULL ELSE f.sg_and_a_expenses / NULLIF(f.revenue,0) END AS sgna_to_revenue
            FROM fact_financials f
            JOIN vw_gross_profit_reconciled g USING (company_id, fiscal_year, fiscal_quarter)
            """
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\nExecuting view {i}/{len(queries)}...")
            if self.db.execute_ddl(query):
                print(f"✅ View {i} created")
            else:
                print(f"❌ ERROR at view {i}")
                return False
        
        # Verify
        print("\nVerifying GP reconciliation...")
        verify = "SELECT * FROM vw_gross_profit_reconciled ORDER BY company_id, fiscal_year, fiscal_quarter LIMIT 10"
        result = self.db.execute_query(verify)
        print(result[['company_id', 'fiscal_year', 'fiscal_quarter', 'gross_profit_source']].to_string(index=False))
        
        print("\n✅ Quarter-end, GP, and canonical ratios created!")
        return True
    
    def run_all(self):
        """Execute all migration prompts"""
        print("\n" + "="*80)
        print("STARTING DATABASE MIGRATION")
        print("="*80)
        
        # Prompt 1
        if not self.prompt_1_verify_tables():
            print("\n❌ Migration stopped at Prompt 1")
            return False
        
        # Prompt 2
        if not self.prompt_2_constraints_indexes():
            print("\n❌ Migration stopped at Prompt 2")
            return False
        
        # Prompt 3
        if not self.prompt_3_quarter_end_gp_ratios():
            print("\n❌ Migration stopped at Prompt 3")
            return False
        
        print("\n" + "="*80)
        print("✅ MIGRATION PHASE 1-3 COMPLETE!")
        print("="*80)
        print("\nNext: Run prompts 4-6 for annual/TTM views and final verification")
        return True


if __name__ == "__main__":
    migration = DatabaseMigration()
    migration.run_all()
