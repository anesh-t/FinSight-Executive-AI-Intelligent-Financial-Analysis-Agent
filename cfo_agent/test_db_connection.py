"""Test database connection"""
import asyncio
from db.pool import db_pool

async def test_connection():
    print("Testing database connection...")
    try:
        await db_pool.initialize()
        print("✅ Database pool initialized")
        
        # Test a simple query
        result = await db_pool.fetch_one("SELECT 1 as test")
        print(f"✅ Query successful: {result}")
        
        await db_pool.close()
        print("✅ Connection closed")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())
