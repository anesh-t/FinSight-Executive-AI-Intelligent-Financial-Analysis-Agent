"""Check schema of mv_financials_annual"""
import asyncio
from db.pool import db_pool

async def check():
    await db_pool.initialize()
    
    # Get columns
    query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'mv_financials_annual'
        ORDER BY ordinal_position
    """
    
    cols = await db_pool.execute_query(query)
    
    print("\nColumns in mv_financials_annual:")
    for col in cols:
        print(f"  {col['column_name']:<40} {col['data_type']}")
    
    await db_pool.close()

asyncio.run(check())
