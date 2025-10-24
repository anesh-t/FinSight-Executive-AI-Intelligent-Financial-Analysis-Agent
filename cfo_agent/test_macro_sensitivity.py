"""
Test macro sensitivity queries (quarterly & annual)
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def test_macro_sensitivity():
    """Test all macro sensitivity query types"""
    
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*100)
    print("TESTING MACRO SENSITIVITY QUERIES - Quarterly & Annual")
    print("="*100)
    
    test_cases = [
        # Quarterly queries
        ("Quarterly - General Sensitivity", "show Apple macro sensitivity Q2 2023"),
        ("Quarterly - Beta to CPI", "show Microsoft beta to inflation Q3 2023"),
        ("Quarterly - Beta to Fed Rate", "show Google beta to Fed rate Q2 2023"),
        ("Quarterly - Margin Response", "how does Amazon margins respond to CPI Q3 2023"),
        
        # Annual queries
        ("Annual - General Sensitivity", "show Apple macro sensitivity 2023"),
        ("Annual - Beta to CPI", "show Meta beta to inflation 2023"),
        ("Annual - Beta to Fed Rate", "show Microsoft sensitivity to Fed rate 2023"),
        ("Annual - Margin Sensitivity", "show Google margin sensitivity to macro 2023"),
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
            
            # Check if we got sensitivity data
            has_sensitivity = any(word in first_line.lower() for word in [
                'beta', 'sensitivity', 'cpi', 'fed rate', 'macro'
            ])
            
            if has_sensitivity:
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
    print(f"\n{'#':<4} {'Test Case':<40} {'Status':<15} {'Response Preview':<40}")
    print("-"*100)
    
    for i, r in enumerate(results, 1):
        preview = r['response'][:37] + "..." if len(r['response']) > 40 else r['response']
        print(f"{i:<4} {r['label']:<40} {r['status']:<15} {preview:<40}")
    
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
    print("\n[1] Quarterly View (vw_macro_sensitivity_rolling):")
    q_test = """
        SELECT 
            c.ticker,
            ms.fiscal_year,
            ms.fiscal_quarter,
            ROUND(ms.net_margin::numeric, 4) as net_margin,
            ROUND(ms.beta_nm_cpi_12q::numeric, 6) as beta_nm_cpi
        FROM vw_macro_sensitivity_rolling ms
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL' 
        AND ms.fiscal_year = 2023 
        AND ms.fiscal_quarter = 2
        LIMIT 1
    """
    
    try:
        result = await db_pool.execute_query(q_test)
        if result:
            r = result[0]
            print(f"  ✅ Found: {r['ticker']} Q{r['fiscal_quarter']} {r['fiscal_year']}")
            print(f"     Net Margin: {r['net_margin']}")
            print(f"     Beta (NM → CPI): {r['beta_nm_cpi']}")
        else:
            print(f"  ❌ No data found")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test annual view
    print("\n[2] Annual View (mv_macro_sensitivity_annual):")
    a_test = """
        SELECT 
            c.ticker,
            msa.fiscal_year,
            ROUND(msa.net_margin_annual::numeric, 4) as net_margin_annual,
            ROUND(msa.beta_nm_cpi_annual::numeric, 6) as beta_nm_cpi_annual,
            ROUND(msa.beta_nm_ffr_annual::numeric, 6) as beta_nm_ffr_annual
        FROM mv_macro_sensitivity_annual msa
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL' 
        AND msa.fiscal_year = 2023
        LIMIT 1
    """
    
    try:
        result = await db_pool.execute_query(a_test)
        if result:
            r = result[0]
            print(f"  ✅ Found: {r['ticker']} {r['fiscal_year']}")
            print(f"     Net Margin (annual avg): {r['net_margin_annual']}")
            print(f"     Beta (NM → CPI): {r['beta_nm_cpi_annual']}")
            print(f"     Beta (NM → Fed Rate): {r['beta_nm_ffr_annual']}")
        else:
            print(f"  ❌ No data found")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    await db_pool.close()
    
    print("\n" + "="*100)
    if success == total:
        print("✅ ALL MACRO SENSITIVITY TESTS PASSING!")
    elif success >= total * 0.75:
        print("⚠️ MOST TESTS PASSING - Some fixes needed")
    else:
        print("❌ MULTIPLE FAILURES - Investigation needed")
    print("="*100)

if __name__ == "__main__":
    asyncio.run(test_macro_sensitivity())
