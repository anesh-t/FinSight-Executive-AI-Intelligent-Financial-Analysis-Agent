"""
Simple database connection test
"""
import asyncio
from db.pool import db_pool

async def test():
    print("Testing database connection...")
    
    try:
        # Initialize
        await db_pool.initialize()
        print("✅ Pool initialized")
        
        # Test query
        result = await db_pool.execute_one("SELECT 1 as test")
        print(f"✅ Query successful: {dict(result)}")
        
        # Test actual data
        result = await db_pool.execute_one("SELECT ticker, name FROM dim_company LIMIT 1")
        print(f"✅ Data query successful: {dict(result)}")
        
        # Close
        await db_pool.close()
        print("✅ Connection closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
