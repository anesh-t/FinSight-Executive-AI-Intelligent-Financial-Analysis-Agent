"""
Check what columns exist in fact_financials table
"""
import asyncio
from db.pool import db_pool

async def check_columns():
    await db_pool.initialize()
    
    print("\n" + "="*80)
    print("CHECKING fact_financials COLUMNS")
    print("="*80)
    
    query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'fact_financials'
        AND table_schema = 'public'
        ORDER BY ordinal_position
    """
    
    cols = await db_pool.execute_query(query)
    
    print(f"\n{'Column Name':<30} {'Data Type':<20}")
    print("-"*50)
    for col in cols:
        print(f"{col['column_name']:<30} {col['data_type']:<20}")
    
    print(f"\nTotal columns: {len(cols)}")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(check_columns())
