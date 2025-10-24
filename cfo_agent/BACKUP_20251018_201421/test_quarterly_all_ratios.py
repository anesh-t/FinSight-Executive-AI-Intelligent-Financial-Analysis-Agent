"""
Test all quarterly ratios from vw_ratios_quarter
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_all_quarterly_ratios():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*120)
    print("TESTING ALL QUARTERLY RATIOS - vw_ratios_quarter")
    print("="*120)
    
    test_cases = [
        # All 9 ratios from vw_ratios_quarter
        ("Quarterly Gross Margin", "show Apple gross margin for Q2 2023", ["gross margin"], "vw_ratios_quarter"),
        ("Quarterly Operating Margin", "show Apple operating margin for Q2 2023", ["operating margin"], "vw_ratios_quarter"),
        ("Quarterly Net Margin", "show Apple net margin for Q2 2023", ["net margin"], "vw_ratios_quarter"),
        ("Quarterly ROE", "show Apple ROE for Q2 2023", ["roe"], "vw_ratios_quarter"),
        ("Quarterly ROA", "show Apple ROA for Q2 2023", ["roa"], "vw_ratios_quarter"),
        ("Quarterly Debt-to-Equity", "show Apple debt to equity for Q2 2023", ["debt-to-equity", "debt to equity"], "vw_ratios_quarter"),
        ("Quarterly Debt-to-Assets", "show Apple debt to assets for Q2 2023", ["debt-to-assets", "debt to assets"], "vw_ratios_quarter"),
        ("Quarterly R&D Intensity", "show Apple R&D intensity for Q2 2023", ["r&d intensity", "intensity"], "vw_ratios_quarter"),
        ("Quarterly SG&A Intensity", "show Apple SG&A intensity for Q2 2023", ["sg&a intensity", "sga intensity", "intensity"], "vw_ratios_quarter"),
    ]
    
    results = []
    
    for label, query, keywords, source in test_cases:
        print(f"\n{'-'*120}")
        print(f"Test: {label}")
        print(f"Query: '{query}'")
        print(f"Expected source: {source}")
        print("-"*120)
        
        try:
            response = await cfo_agent_graph.run(query)
            
            # Check if response contains expected keywords
            response_lower = response.lower()
            found_keywords = [kw for kw in keywords if kw in response_lower]
            
            if "no data" in response_lower or "no results" in response_lower:
                status = "❌ NO DATA"
                print(f"{status}")
                results.append((label, status))
            elif not found_keywords:
                status = "⚠️  METRIC MISSING"
                print(f"{status}")
                print(f"Response: {response[:150]}")
                results.append((label, status))
            else:
                status = "✅ SUCCESS"
                first_line = response.split('\n')[0]
                print(f"{status}")
                print(f"Response: {first_line}")
                results.append((label, status))
                
        except Exception as e:
            status = "❌ ERROR"
            print(f"{status}: {str(e)[:100]}")
            results.append((label, status))
    
    # Summary
    print("\n" + "="*120)
    print("SUMMARY - ALL QUARTERLY RATIOS")
    print("="*120)
    
    success_count = sum(1 for _, status in results if "✅" in status)
    total = len(results)
    
    print(f"\n{'Test':<60} {'Status':<20}")
    print("-"*120)
    for label, status in results:
        print(f"{label:<60} {status:<20}")
    
    print("\n" + "="*120)
    print(f"PASSED: {success_count}/{total} ({success_count/total*100:.1f}%)")
    print("="*120)
    
    # Data source summary
    print("\n📊 DATA SOURCE:")
    print("  - All 9 Quarterly Ratios: vw_ratios_quarter")
    print("    └─ roe, roa, gross_margin, operating_margin, net_margin")
    print("    └─ debt_to_equity, debt_to_assets, rnd_to_revenue, sgna_to_revenue")
    
    await db_pool.close()

asyncio.run(test_all_quarterly_ratios())
