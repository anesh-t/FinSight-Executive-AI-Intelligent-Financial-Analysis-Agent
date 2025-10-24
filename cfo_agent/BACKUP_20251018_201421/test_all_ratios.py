"""
Test all 9 ratio metrics from dim_ratio table
- Quarterly (TTM): 5 ratios from mv_ratios_ttm
- Annual: 9 ratios from mv_ratios_annual
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_all_ratios():
    """Test all 9 ratios for both quarterly and annual queries"""
    
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*120)
    print("TESTING ALL 9 RATIO METRICS - Quarterly (TTM) vs Annual")
    print("="*120)
    
    # All 9 ratios from dim_ratio table (from user's image)
    ratios = [
        # code, name, query_term, available_ttm, available_annual
        ("roe", "Return on Equity (ROE)", "ROE", True, True),
        ("roa", "Return on Assets (ROA)", "ROA", True, True),
        ("gross_margin", "Gross Margin", "gross margin", True, True),
        ("operating_margin", "Operating Margin", "operating margin", True, True),
        ("net_margin", "Net Profit Margin", "net margin", True, True),
        ("debt_to_equity", "Debt-to-Equity Ratio", "debt to equity ratio", False, True),
        ("debt_to_assets", "Debt-to-Assets Ratio", "debt to assets ratio", False, True),
        ("rnd_to_revenue", "R&D Intensity", "R&D intensity", False, True),
        ("sgna_to_revenue", "SG&A Intensity", "SG&A intensity", False, True),
    ]
    
    test_company = "AAPL"
    test_year = 2023
    test_quarter = 2
    
    results = []
    
    for code, name, query_term, avail_ttm, avail_annual in ratios:
        print(f"\n{'='*120}")
        print(f"Testing: {name} ({code})")
        print(f"{'='*120}")
        
        # Test Quarterly (TTM)
        if avail_ttm:
            quarterly_query = f"show {test_company} {query_term} for Q{test_quarter} {test_year}"
            print(f"\n📊 QUARTERLY (TTM): {quarterly_query}")
            
            try:
                q_result = await cfo_agent_graph.run(quarterly_query)
                q_lines = q_result.split('\n')
                q_value = q_lines[0] if q_lines else "No response"
                
                # Check if data was returned
                if "No data" in q_result or "No results" in q_result:
                    q_status = "❌ NO DATA"
                    q_display = "N/A"
                elif query_term.lower() not in q_result.lower() and code not in q_result.lower():
                    q_status = "⚠️  NO METRIC"
                    q_display = q_value[:80]
                else:
                    q_status = "✅"
                    q_display = q_value[:100]
                
                print(f"  {q_status} {q_display}")
            except Exception as e:
                q_status = "❌ ERROR"
                q_display = str(e)[:50]
                print(f"  {q_status} {q_display}")
        else:
            q_status = "⏸️  N/A"
            q_display = "Not available for TTM"
            print(f"\n📊 QUARTERLY (TTM): Not available in mv_ratios_ttm")
            print(f"  {q_status} {q_display}")
        
        # Test Annual
        annual_query = f"show {test_company} {query_term} for {test_year}"
        print(f"\n📅 ANNUAL: {annual_query}")
        
        try:
            a_result = await cfo_agent_graph.run(annual_query)
            a_lines = a_result.split('\n')
            a_value = a_lines[0] if a_lines else "No response"
            
            # Check if data was returned
            if "No data" in a_result or "No results" in a_result:
                a_status = "❌ NO DATA"
                a_display = "N/A"
            elif query_term.lower() not in a_result.lower() and code not in a_result.lower():
                a_status = "⚠️  NO METRIC"
                a_display = a_value[:80]
            else:
                a_status = "✅"
                a_display = a_value[:100]
            
            print(f"  {a_status} {a_display}")
        except Exception as e:
            a_status = "❌ ERROR"
            a_display = str(e)[:50]
            print(f"  {a_status} {a_display}")
        
        results.append({
            'code': code,
            'name': name,
            'quarterly': q_status,
            'annual': a_status,
            'avail_ttm': avail_ttm,
            'avail_annual': avail_annual
        })
    
    # Summary Table
    print("\n" + "="*120)
    print("SUMMARY: ALL 9 RATIO METRICS TEST RESULTS")
    print("="*120)
    print(f"\n{'#':<4} {'Ratio':<35} {'Code':<25} {'Quarterly (TTM)':<20} {'Annual':<20}")
    print("-"*120)
    
    for i, result in enumerate(results, 1):
        q_display = result['quarterly'] if result['avail_ttm'] else "⏸️  N/A (not in TTM)"
        a_display = result['annual']
        print(f"{i:<4} {result['name']:<35} {result['code']:<25} {q_display:<20} {a_display:<20}")
    
    # Count successes
    ttm_available = sum(1 for r in results if r['avail_ttm'])
    ttm_success = sum(1 for r in results if r['avail_ttm'] and "✅" in r['quarterly'])
    
    annual_available = sum(1 for r in results if r['avail_annual'])
    annual_success = sum(1 for r in results if r['avail_annual'] and "✅" in r['annual'])
    
    total = len(results)
    
    print("\n" + "="*120)
    print(f"RESULTS:")
    print(f"  Quarterly (TTM): {ttm_success}/{ttm_available} available ratios working")
    print(f"  Annual: {annual_success}/{annual_available} available ratios working")
    print(f"  Total: {ttm_success + annual_success}/{ttm_available + annual_available} tests passed")
    print("="*120)
    
    # Data source verification
    print("\n" + "="*120)
    print("DATA SOURCE VERIFICATION")
    print("="*120)
    
    print("\n📊 QUARTERLY (TTM) DATA SOURCE (mv_ratios_ttm):")
    ttm_check = """
        SELECT COUNT(*) as count
        FROM mv_ratios_ttm
        WHERE company_id = (SELECT company_id FROM dim_company WHERE ticker = 'AAPL')
        AND fiscal_year = 2023 AND fiscal_quarter = 2
    """
    ttm_source = await db_pool.execute_query(ttm_check)
    print(f"  Found {ttm_source[0]['count']} records in mv_ratios_ttm for AAPL Q2 2023")
    print(f"  Available ratios: {ttm_available} (margins + ROE + ROA)")
    
    print("\n📅 ANNUAL DATA SOURCE (mv_ratios_annual):")
    annual_check = """
        SELECT COUNT(*) as count
        FROM mv_ratios_annual
        WHERE company_id = (SELECT company_id FROM dim_company WHERE ticker = 'AAPL')
        AND fiscal_year = 2023
    """
    annual_source = await db_pool.execute_query(annual_check)
    print(f"  Found {annual_source[0]['count']} records in mv_ratios_annual for AAPL 2023")
    print(f"  Available ratios: {annual_available} (all 9 ratios)")
    
    await db_pool.close()
    
    return results


if __name__ == "__main__":
    asyncio.run(test_all_ratios())
