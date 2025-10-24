"""Test all 9 annual ratios"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def test():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*120)
    print("TESTING ALL ANNUAL RATIOS - mv_ratios_annual")
    print("="*120)
    
    ratios = [
        ("ROE", "show Apple ROE for 2023"),
        ("ROA", "show Apple ROA for 2023"),
        ("Gross Margin", "show Apple gross margin for 2023"),
        ("Operating Margin", "show Apple operating margin for 2023"),
        ("Net Margin", "show Apple net margin for 2023"),
        ("Debt-to-Equity", "show Apple debt to equity ratio for 2023"),
        ("Debt-to-Assets", "show Apple debt to assets ratio for 2023"),
        ("R&D Intensity", "show Apple R&D intensity for 2023"),
        ("SG&A Intensity", "show Apple SG&A intensity for 2023"),
    ]
    
    results = []
    
    for name, query in ratios:
        print(f"\n{'-'*120}")
        print(f"Test: {name}")
        print(f"Query: '{query}'")
        print("-"*120)
        
        response = await cfo_agent_graph.run(query)
        first_line = response.split('\n')[0]
        
        if "No data" in response or "No results" in response:
            status = "❌ FAILED"
        elif name.lower() in first_line.lower() or any(word in first_line.lower() for word in name.lower().split()):
            status = "✅ SUCCESS"
        else:
            status = "⚠️ PARTIAL"
        
        print(f"{status}")
        print(f"Response: {first_line}")
        results.append((name, status))
    
    # Summary
    print("\n" + "="*120)
    print("SUMMARY - ALL ANNUAL RATIOS")
    print("="*120)
    
    success = sum(1 for _, s in results if "✅" in s)
    total = len(results)
    
    print(f"\n{'Test':<30} {'Status':<20}")
    print("-"*120)
    for name, status in results:
        print(f"{name:<30} {status:<20}")
    
    print("\n" + "="*120)
    print(f"PASSED: {success}/{total} ({success/total*100:.1f}%)")
    print("="*120)
    
    await db_pool.close()

asyncio.run(test())
