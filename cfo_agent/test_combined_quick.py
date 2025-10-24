"""
Quick test of combined views
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def test_quick():
    """Quick test of combined view queries"""
    # Initialize
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*80)
    print("QUICK TEST: COMBINED VIEWS")
    print("="*80)
    
    tests = [
        ("Complete Q", "show Apple complete picture Q2 2023"),
        ("Complete A", "show Apple complete picture 2023"),
        ("Macro Context Q", "show Apple with macro context Q2 2023"),
    ]
    
    for category, query in tests:
        print(f"\n[{category}] {query}")
        print("-"*80)
        
        try:
            response = await cfo_agent_graph.run(query)
            print(f"✅ Response: {response[:150]}...")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    await db_pool.close()
    print("\n" + "="*80)
    print("DONE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_quick())
