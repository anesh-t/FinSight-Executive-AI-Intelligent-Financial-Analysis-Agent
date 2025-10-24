"""
Check mv_ratios_ttm structure and data
"""
import asyncio
from db.pool import db_pool


async def check_ratios_ttm():
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("CHECKING mv_ratios_ttm VIEW")
    print("="*100)
    
    # Get columns
    cols_query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'mv_ratios_ttm'
        ORDER BY ordinal_position
    """
    
    cols = await db_pool.execute_query(cols_query)
    
    print("\n[1] Columns in mv_ratios_ttm:")
    print("-"*100)
    for col in cols:
        print(f"  {col['column_name']:<40} {col['data_type']}")
    
    # Get sample data
    sample_query = """
        SELECT r.*
        FROM mv_ratios_ttm r
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        ORDER BY r.fiscal_year DESC, r.fiscal_quarter DESC
        LIMIT 1
    """
    
    sample = await db_pool.execute_query(sample_query)
    
    if sample:
        print("\n[2] Sample data (Apple latest quarter):")
        print("-"*100)
        row = sample[0]
        for key, val in row.items():
            if val is not None:
                print(f"  {key:<40} {val}")
    
    await db_pool.close()

asyncio.run(check_ratios_ttm())
