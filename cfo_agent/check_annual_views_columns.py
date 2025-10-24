"""
Check what columns exist in mv_ratios_annual and mv_stock_prices_annual
"""
import asyncio
from db.pool import db_pool

async def check():
    await db_pool.initialize()
    
    views = ['mv_ratios_annual', 'mv_stock_prices_annual']
    
    for view in views:
        print(f"\n{'='*80}")
        print(f"[{view}]")
        print("="*80)
        
        # Try to select one row to see columns
        try:
            query = f"SELECT * FROM {view} LIMIT 1"
            result = await db_pool.execute_query(query)
            
            if result:
                print(f"\n✅ View exists with {len(result[0])} columns:")
                print(f"\n{'Column Name':<40}")
                print("-"*40)
                for col_name in result[0].keys():
                    print(f"{col_name:<40}")
            else:
                print("❌ View exists but has no data")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(check())
