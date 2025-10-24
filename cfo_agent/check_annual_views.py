"""
Check which annual views actually exist
"""
import asyncio
from db.pool import db_pool

async def check():
    await db_pool.initialize()
    
    print("\n" + "="*80)
    print("CHECKING WHICH ANNUAL VIEWS EXIST")
    print("="*80)
    
    views = [
        'mv_financials_annual',
        'mv_ratios_annual',
        'mv_stock_prices_annual',
        'mv_macro_annual',
        'mv_macro_sensitivity_annual'
    ]
    
    for view in views:
        query = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = '{view}'
            ) as exists
        """
        result = await db_pool.execute_query(query)
        exists = result[0]['exists']
        
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"{status} - {view}")
        
        if exists:
            # Get row count
            count_query = f"SELECT COUNT(*) as count FROM {view}"
            count_result = await db_pool.execute_query(count_query)
            count = count_result[0]['count']
            print(f"         ({count} rows)")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(check())
