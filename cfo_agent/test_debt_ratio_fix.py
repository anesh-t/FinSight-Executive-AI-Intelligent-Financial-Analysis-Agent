"""Test if debt ratio formatting is fixed"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def test():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*100)
    print("TESTING DEBT RATIO FORMATTING FIX")
    print("="*100)
    
    tests = [
        ("Annual Debt-to-Equity", "show Apple debt to equity ratio for 2023"),
        ("Annual Debt-to-Assets", "show Apple debt to assets ratio for 2023"),
        ("Quarterly Debt-to-Equity", "show Apple debt to equity for Q2 2023"),
        ("Quarterly Debt-to-Assets", "show Apple debt to assets for Q2 2023"),
    ]
    
    for label, query in tests:
        print(f"\n{label}:")
        print(f"  Query: '{query}'")
        result = await cfo_agent_graph.run(query)
        first_line = result.split('\n')[0]
        print(f"  Result: {first_line}")
        
        # Check if clean (no extra equity/assets mentioned)
        if "equity of" in first_line and "debt-to-equity" in first_line:
            print(f"  ⚠️  Still showing equity value")
        elif "assets of" in first_line and "debt-to-assets" in first_line:
            print(f"  ⚠️  Still showing assets value")
        elif "debt-to-equity" in first_line or "debt-to-assets" in first_line:
            print(f"  ✅ Clean! Only showing the ratio")
        else:
            print(f"  ❌ No ratio found")
    
    await db_pool.close()

asyncio.run(test())
