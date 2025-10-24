"""
Check complete schema of fact_stock_prices and related views
"""
import asyncio
from db.pool import db_pool

async def check():
    await db_pool.initialize()
    
    tables = [
        'fact_stock_prices',
        'vw_stock_prices_quarter',
        'mv_stock_prices_annual',
        'mv_ratios_annual'
    ]
    
    for table in tables:
        print(f"\n{'='*80}")
        print(f"[{table}]")
        print("="*80)
        
        query = f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table}'
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """
        
        cols = await db_pool.execute_query(query)
        
        if cols:
            print(f"\n{'Column':<40} {'Type':<20}")
            print("-"*60)
            for col in cols:
                print(f"{col['column_name']:<40} {col['data_type']:<20}")
        else:
            print("NOT FOUND")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(check())
