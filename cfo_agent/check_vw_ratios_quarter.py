"""Check the structure of vw_ratios_quarter"""
import asyncio
from db.pool import db_pool

async def check():
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("CHECKING vw_ratios_quarter STRUCTURE")
    print("="*100)
    
    # 1. Get columns
    cols_query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'vw_ratios_quarter'
        ORDER BY ordinal_position
    """
    
    cols = await db_pool.execute_query(cols_query)
    
    print("\nColumns in vw_ratios_quarter:")
    print("-"*100)
    for col in cols:
        print(f"  {col['column_name']:<40} {col['data_type']}")
    
    # 2. Get sample data
    sample_query = """
        SELECT *
        FROM vw_ratios_quarter r
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        AND r.fiscal_year = 2023
        AND r.fiscal_quarter = 2
    """
    
    result = await db_pool.execute_query(sample_query)
    
    if result:
        print("\n\nSample data (Apple Q2 2023):")
        print("-"*100)
        row = result[0]
        for key, val in row.items():
            if val is not None and key not in ['company_id', 'ticker', 'name']:
                if isinstance(val, float):
                    print(f"  {key:<40} {val:.6f}")
                else:
                    print(f"  {key:<40} {val}")
    else:
        print("\n❌ No sample data found")
    
    await db_pool.close()

asyncio.run(check())
