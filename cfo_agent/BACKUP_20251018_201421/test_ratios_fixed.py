"""
Test all ratios with better detection logic
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_ratios_comprehensive():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*120)
    print("COMPREHENSIVE RATIO TEST - All 9 Ratios")
    print("="*120)
    
    test_cases = [
        # (label, query, expected_keywords, source)
        
        # Annual ratios (all 9 should work)
        ("Annual ROE", "show Apple ROE for 2023", ["roe", "156"], "mv_ratios_annual"),
        ("Annual ROA", "show Apple ROA for 2023", ["roa", "29"], "mv_ratios_annual"),
        ("Annual Gross Margin", "show Apple gross margin for 2023", ["gross margin", "45"], "mv_ratios_annual"),
        ("Annual Operating Margin", "show Apple operating margin for 2023", ["operating margin", "30"], "mv_ratios_annual"),
        ("Annual Net Margin", "show Apple net margin for 2023", ["net margin", "26"], "mv_ratios_annual"),
        ("Annual Debt-to-Equity", "show Apple debt to equity ratio for 2023", ["debt-to-equity", "3.7"], "mv_ratios_annual"),
        ("Annual Debt-to-Assets", "show Apple debt to assets ratio for 2023", ["debt-to-assets", "0.79"], "mv_ratios_annual"),
        ("Annual R&D Intensity", "show Apple R&D intensity for 2023", ["r&d intensity", "7."], "mv_ratios_annual"),
        ("Annual SG&A Intensity", "show Apple SG&A intensity for 2023", ["sg&a intensity", "6."], "mv_ratios_annual"),
        
        # Quarterly (TTM) ratios (5 should work)
        ("Quarterly Gross Margin", "show Apple gross margin for Q2 2023", ["gross margin"], "fact_financials"),
        ("Quarterly Operating Margin", "show Apple operating margin for Q2 2023", ["operating margin"], "fact_financials"),
        ("Quarterly Net Margin", "show Apple net margin for Q2 2023", ["net margin"], "fact_financials"),
        ("Quarterly ROE (TTM)", "show Apple ROE for Q2 2023", ["roe"], "mv_ratios_ttm"),
        ("Quarterly ROA (TTM)", "show Apple ROA for Q2 2023", ["roa"], "mv_ratios_ttm"),
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
            found_keywords = [kw for kw in keywords if kw.lower() in response_lower]
            
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
                # Extract first line
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
    print("SUMMARY")
    print("="*120)
    
    success_count = sum(1 for _, status in results if "✅" in status)
    total = len(results)
    
    print(f"\n{'Test':<50} {'Status':<20}")
    print("-"*120)
    for label, status in results:
        print(f"{label:<50} {status:<20}")
    
    print("\n" + "="*120)
    print(f"PASSED: {success_count}/{total} ({success_count/total*100:.1f}%)")
    print("="*120)
    
    await db_pool.close()

asyncio.run(test_ratios_comprehensive())
