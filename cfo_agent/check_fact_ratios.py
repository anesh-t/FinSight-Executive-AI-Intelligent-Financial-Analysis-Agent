"""
Check what's in fact_ratios table
"""
import asyncio
from db.pool import db_pool


async def check_fact_ratios():
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("CHECKING fact_ratios TABLE")
    print("="*100)
    
    # Check columns
    cols_query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'fact_ratios'
        ORDER BY ordinal_position
    """
    
    cols = await db_pool.execute_query(cols_query)
    
    print("\n[1] Columns in fact_ratios:")
    print("-"*100)
    for col in cols:
        print(f"  {col['column_name']:<40} {col['data_type']}")
    
    # Get sample data
    sample_query = """
        SELECT fr.*
        FROM fact_ratios fr
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        AND fr.fiscal_year = 2023
        AND fr.fiscal_quarter = 2
        LIMIT 1
    """
    
    sample = await db_pool.execute_query(sample_query)
    
    if sample:
        print("\n[2] Sample data (Apple Q2 2023):")
        print("-"*100)
        row = sample[0]
        for key, val in row.items():
            if val is not None and key not in ['company_id', 'fiscal_year', 'fiscal_quarter']:
                print(f"  {key:<40} {val}")
    else:
        print("\n[2] No data found in fact_ratios")
    
    # Compare with mv_ratios_ttm
    print("\n[3] Comparison:")
    print("-"*100)
    print("mv_ratios_ttm has: gross_margin_ttm, operating_margin_ttm, net_margin_ttm, roe_ttm, roa_ttm")
    print("\nFor quarterly ratios NOT in mv_ratios_ttm, should query fact_ratios")
    
    await db_pool.close()

asyncio.run(check_fact_ratios())
