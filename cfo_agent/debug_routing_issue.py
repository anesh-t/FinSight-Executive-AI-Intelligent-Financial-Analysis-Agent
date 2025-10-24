"""
Debug why quarterly debt/intensity ratios have routing issues
"""
import asyncio
from db.pool import db_pool


async def debug_routing():
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("INVESTIGATING ROUTING ISSUE FOR QUARTERLY RATIOS")
    print("="*100)
    
    # 1. Check what's in mv_ratios_ttm (after recreation)
    print("\n[1] Checking mv_ratios_ttm structure:")
    print("-"*100)
    
    ttm_cols_query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'mv_ratios_ttm'
        ORDER BY ordinal_position
    """
    
    ttm_cols = await db_pool.execute_query(ttm_cols_query)
    print("Columns in mv_ratios_ttm:")
    for col in ttm_cols:
        print(f"  {col['column_name']:<40} {col['data_type']}")
    
    # 2. Check sample data from mv_ratios_ttm
    print("\n[2] Sample data from mv_ratios_ttm (Apple Q2 2023):")
    print("-"*100)
    
    ttm_sample_query = """
        SELECT r.*
        FROM mv_ratios_ttm r
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        AND r.fiscal_year = 2023
        AND r.fiscal_quarter = 2
    """
    
    ttm_sample = await db_pool.execute_query(ttm_sample_query)
    
    if ttm_sample:
        row = ttm_sample[0]
        print("Available ratios in mv_ratios_ttm:")
        for key, val in row.items():
            if key not in ['company_id', 'fiscal_year', 'fiscal_quarter'] and val is not None:
                print(f"  {key:<40} {val}")
    else:
        print("  ❌ NO DATA in mv_ratios_ttm!")
    
    # 3. Check what's in fact_ratios for comparison
    print("\n[3] Sample data from fact_ratios (Apple Q2 2023):")
    print("-"*100)
    
    fact_ratios_query = """
        SELECT fr.*
        FROM fact_ratios fr
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        AND fr.fiscal_year = 2023
        AND fr.fiscal_quarter = 2
    """
    
    fact_sample = await db_pool.execute_query(fact_ratios_query)
    
    if fact_sample:
        row = fact_sample[0]
        print("Available ratios in fact_ratios:")
        for key, val in row.items():
            if key not in ['ratio_id', 'company_id', 'fiscal_year', 'fiscal_quarter'] and val is not None:
                print(f"  {key:<40} {val}")
    
    # 4. Check what quarter_snapshot returns
    print("\n[4] Checking quarter_snapshot template output:")
    print("-"*100)
    
    quarter_snapshot_query = """
        SELECT 
            c.ticker, 
            c.name, 
            f.fiscal_year, 
            f.fiscal_quarter,
            f.net_income/NULLIF(f.equity,0) as roe,
            f.net_income/NULLIF(f.total_assets,0) as roa,
            f.total_assets,
            f.equity
        FROM fact_financials f
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        AND f.fiscal_year = 2023
        AND f.fiscal_quarter = 2
    """
    
    qs_result = await db_pool.execute_query(quarter_snapshot_query)
    
    if qs_result:
        row = qs_result[0]
        print("quarter_snapshot returns:")
        for key, val in row.items():
            print(f"  {key:<40} {val}")
    
    # 5. Summary
    print("\n" + "="*100)
    print("ANALYSIS:")
    print("="*100)
    print("\n📊 AVAILABLE DATA SOURCES FOR QUARTERLY RATIOS:")
    print("")
    print("Source 1: mv_ratios_ttm")
    if ttm_sample:
        print("  Status: ✅ Has data")
        print("  Ratios: Only 5 (gross_margin_ttm, operating_margin_ttm, net_margin_ttm, roe_ttm, roa_ttm)")
        print("  Missing: debt_to_equity, debt_to_assets, rnd_to_revenue, sgna_to_revenue")
    else:
        print("  Status: ❌ NO DATA - This might be the issue!")
    
    print("\nSource 2: fact_ratios")
    if fact_sample:
        print("  Status: ✅ Has data")
        print("  Ratios: All 9 ratios including debt and intensity")
    
    print("\nSource 3: fact_financials (via quarter_snapshot)")
    if qs_result:
        print("  Status: ✅ Has data")
        print("  Ratios: Calculated ROE, ROA, margins (no debt or intensity)")
    
    print("\n🔍 LIKELY ROUTING ISSUE:")
    print("  - Quarterly debt/intensity queries need to route to fact_ratios")
    print("  - Currently routing to quarter_snapshot (which doesn't have those ratios)")
    print("  - Need to check template selection logic in decomposer")
    
    await db_pool.close()

asyncio.run(debug_routing())
