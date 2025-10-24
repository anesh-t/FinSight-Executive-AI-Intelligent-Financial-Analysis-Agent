"""
Check actual columns in mv_financials_annual
"""
import asyncio
from db.pool import db_pool

async def check():
    await db_pool.initialize()
    
    print("\n" + "="*80)
    print("[mv_financials_annual]")
    print("="*80)
    
    try:
        query = "SELECT * FROM mv_financials_annual LIMIT 1"
        result = await db_pool.execute_query(query)
        
        if result:
            print(f"\n✅ View exists with {len(result[0])} columns:\n")
            print(f"{'Column Name':<40}")
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
