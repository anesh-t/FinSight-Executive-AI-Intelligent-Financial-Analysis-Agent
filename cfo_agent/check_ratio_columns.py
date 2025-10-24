"""
Check what ratio columns are available in mv_ratios_annual and mv_ratios_ttm
"""
import asyncio
from db.pool import db_pool


async def check_ratio_columns():
    """Check available columns in ratio views"""
    
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("CHECKING RATIO VIEW COLUMNS")
    print("="*100)
    
    # Check mv_ratios_annual
    print("\n[1] mv_ratios_annual columns:")
    print("-"*100)
    
    annual_query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'mv_ratios_annual'
        ORDER BY ordinal_position
    """
    
    annual_cols = await db_pool.execute_query(annual_query)
    for col in annual_cols:
        print(f"  {col['column_name']:<40} {col['data_type']}")
    
    # Check mv_ratios_ttm
    print("\n[2] mv_ratios_ttm columns:")
    print("-"*100)
    
    ttm_query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'mv_ratios_ttm'
        ORDER BY ordinal_position
    """
    
    ttm_cols = await db_pool.execute_query(ttm_query)
    for col in ttm_cols:
        print(f"  {col['column_name']:<40} {col['data_type']}")
    
    # Sample data from mv_ratios_annual
    print("\n[3] Sample data from mv_ratios_annual (Apple 2023):")
    print("-"*100)
    
    sample_query = """
        SELECT r.*
        FROM mv_ratios_annual r
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        AND r.fiscal_year = 2023
    """
    
    sample = await db_pool.execute_query(sample_query)
    if sample:
        row = sample[0]
        for key, value in row.items():
            if value is not None and key not in ['company_id', 'fiscal_year']:
                print(f"  {key:<40} {value}")
    
    await db_pool.close()


if __name__ == "__main__":
    asyncio.run(check_ratio_columns())
