"""
Check TTM ratio columns
"""
import asyncio
from db.pool import db_pool


async def check_ttm():
    await db_pool.initialize()
    
    # Check if mv_ratios_ttm exists and what columns it has
    query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'mv_ratios_ttm'
        ORDER BY ordinal_position
    """
    
    cols = await db_pool.execute_query(query)
    
    if cols:
        print("mv_ratios_ttm columns:")
        for col in cols:
            print(f"  - {col['column_name']}")
        
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
            print("\nSample data (Apple latest):")
            for key, val in sample[0].items():
                if key not in ['company_id', 'fiscal_year', 'fiscal_quarter']:
                    print(f"  {key}: {val}")
    else:
        print("❌ mv_ratios_ttm does not exist")
    
    await db_pool.close()

asyncio.run(check_ttm())
