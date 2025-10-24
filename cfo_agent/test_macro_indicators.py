"""
Test macro indicator queries (quarterly & annual)
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def test_macro_indicators():
    """Test all macro indicator query types"""
    
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*100)
    print("TESTING MACRO INDICATOR QUERIES - Quarterly & Annual")
    print("="*100)
    
    test_cases = [
        # Quarterly queries
        ("Quarterly - GDP", "show GDP Q2 2023"),
        ("Quarterly - Inflation", "show inflation Q3 2023"),
        ("Quarterly - CPI", "show CPI Q2 2023"),
        ("Quarterly - Unemployment", "show unemployment rate Q3 2023"),
        ("Quarterly - Fed Rate", "show Fed rate Q1 2024"),
        ("Quarterly - S&P 500", "show S&P 500 Q2 2023"),
        
        # Annual queries
        ("Annual - GDP", "show GDP 2023"),
        ("Annual - Inflation", "show inflation 2023"),
        ("Annual - Unemployment", "show unemployment rate 2023"),
        ("Annual - Fed Rate", "show Federal Funds rate 2023"),
        ("Annual - All Indicators", "show macro indicators 2023"),
    ]
    
    results = []
    
    for label, query in test_cases:
        print(f"\n{'='*100}")
        print(f"[{label}]")
        print(f"Query: '{query}'")
        print("-"*100)
        
        try:
            result = await cfo_agent_graph.run(query)
            
            # Get first line
            first_line = result.split('\n')[0] if result else "No response"
            
            # Check if we got macro indicator data
            has_macro = any(word in first_line.lower() for word in [
                'gdp', 'cpi', 'inflation', 'unemployment', 'fed', 'federal funds',
                's&p 500', 'vix', 'macro indicator'
            ])
            
            if has_macro:
                status = "✅ SUCCESS"
            elif "no data" in first_line.lower() or "not found" in first_line.lower():
                status = "❌ NO DATA"
            else:
                status = "⚠️ UNEXPECTED"
            
            print(f"{status}")
            print(f"Response: {first_line}")
            
            results.append({
                'label': label,
                'query': query,
                'status': status,
                'response': first_line
            })
            
        except Exception as e:
            print(f"❌ ERROR")
            print(f"Error: {str(e)[:100]}")
            results.append({
                'label': label,
                'query': query,
                'status': "❌ ERROR",
                'response': str(e)[:100]
            })
    
    # Summary
    print("\n" + "="*100)
    print("SUMMARY TABLE")
    print("="*100)
    print(f"\n{'#':<4} {'Test Case':<35} {'Status':<15} {'Response Preview':<45}")
    print("-"*100)
    
    for i, r in enumerate(results, 1):
        preview = r['response'][:42] + "..." if len(r['response']) > 45 else r['response']
        print(f"{i:<4} {r['label']:<35} {r['status']:<15} {preview:<45}")
    
    # Count successes
    success = sum(1 for r in results if "✅" in r['status'])
    total = len(results)
    
    print("\n" + "="*100)
    print(f"RESULTS: {success}/{total} tests passing ({success/total*100:.1f}%)")
    print("="*100)
    
    # Test direct database queries to verify views
    print("\n" + "="*100)
    print("DATABASE VERIFICATION - Direct View Queries")
    print("="*100)
    
    # Test quarterly view
    print("\n[1] Quarterly View (vw_macro_quarter):")
    q_test = """
        SELECT 
            fiscal_year,
            fiscal_quarter,
            ROUND(gdp::numeric, 2) as gdp,
            ROUND(cpi::numeric, 2) as cpi,
            ROUND(unemployment_rate::numeric, 2) as unemployment
        FROM vw_macro_quarter
        WHERE fiscal_year = 2023 AND fiscal_quarter = 2
        LIMIT 1
    """
    
    try:
        result = await db_pool.execute_query(q_test)
        if result:
            r = result[0]
            print(f"  ✅ Found: Q{r['fiscal_quarter']} {r['fiscal_year']}")
            print(f"     GDP: ${r['gdp']}B")
            print(f"     CPI: {r['cpi']}")
            print(f"     Unemployment: {r['unemployment']}%")
        else:
            print(f"  ❌ No data found")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test annual view
    print("\n[2] Annual View (mv_macro_annual):")
    a_test = """
        SELECT 
            fiscal_year,
            ROUND(gdp_annual::numeric, 2) as gdp_avg,
            ROUND(cpi_annual::numeric, 2) as cpi_avg,
            ROUND(unemployment_rate_annual::numeric, 2) as unemployment_avg,
            ROUND(fed_funds_rate_annual::numeric, 2) as fed_rate_avg
        FROM mv_macro_annual
        WHERE fiscal_year = 2023
        LIMIT 1
    """
    
    try:
        result = await db_pool.execute_query(a_test)
        if result:
            r = result[0]
            print(f"  ✅ Found: {r['fiscal_year']}")
            print(f"     GDP (avg): ${r['gdp_avg']}B")
            print(f"     CPI (avg): {r['cpi_avg']}")
            print(f"     Unemployment (avg): {r['unemployment_avg']}%")
            print(f"     Fed Rate (avg): {r['fed_rate_avg']}%")
        else:
            print(f"  ❌ No data found")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    await db_pool.close()
    
    print("\n" + "="*100)
    if success == total:
        print("✅ ALL MACRO INDICATOR TESTS PASSING!")
    elif success >= total * 0.75:
        print("⚠️ MOST TESTS PASSING - Some fixes needed")
    else:
        print("❌ MULTIPLE FAILURES - Investigation needed")
    print("="*100)

if __name__ == "__main__":
    asyncio.run(test_macro_indicators())
