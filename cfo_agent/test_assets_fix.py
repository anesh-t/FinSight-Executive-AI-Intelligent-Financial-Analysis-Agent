"""
Test if total assets now displays correctly
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_assets_fix():
    """Test total assets, liabilities, equity queries"""
    
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*100)
    print("TESTING BALANCE SHEET METRICS AFTER FIX")
    print("="*100)
    
    test_queries = [
        ("Amazon total assets 2023", "show amazon total assets for 2023"),
        ("Amazon total liabilities 2023", "show amazon total liabilities for 2023"),
        ("Amazon equity 2023", "show amazon equity for 2023"),
        ("Microsoft total assets 2023", "show microsoft total assets for 2023"),
        ("Apple total assets Q2 2023", "show apple total assets for Q2 2023"),
    ]
    
    for label, query in test_queries:
        print(f"\n{'-'*100}")
        print(f"Test: {label}")
        print(f"Query: '{query}'")
        print("-"*100)
        
        try:
            result = await cfo_agent_graph.run(query)
            lines = result.split('\n')
            print(f"✅ Response: {lines[0]}")
            
            if "Data found" in result and "total assets" not in result.lower() and "liabilities" not in result.lower() and "equity" not in result.lower():
                print("  ⚠️  WARNING: Generic response, value not displayed")
            elif "No data" in result or "No results" in result:
                print("  ❌ No data returned")
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
    
    print("\n" + "="*100)
    
    await db_pool.close()


if __name__ == "__main__":
    asyncio.run(test_assets_fix())
