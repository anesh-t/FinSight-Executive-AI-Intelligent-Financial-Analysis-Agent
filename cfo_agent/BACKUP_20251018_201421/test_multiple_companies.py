"""
Test all 19 attributes across multiple companies
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_multiple_companies():
    """Test key attributes across multiple companies"""
    
    # Initialize
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*100)
    print("MULTI-COMPANY ATTRIBUTE TEST - Testing 5 Key Metrics Across Different Companies")
    print("="*100)
    
    # Test companies
    companies = [
        ("Apple", "AAPL"),
        ("Microsoft", "MSFT"),
        ("Google/Alphabet", "GOOG"),
        ("Amazon", "AMZN"),
        ("Meta/Facebook", "META")
    ]
    
    # Key attributes to test
    attributes = [
        ("Revenue", "revenue"),
        ("Net Income", "net income"),
        ("R&D Expenses", "R&D expenses"),
        ("Operating Cash Flow", "cash flow ops"),
        ("Total Assets", "total assets")
    ]
    
    results = {}
    
    for company_name, ticker in companies:
        print(f"\n{'='*100}")
        print(f"TESTING COMPANY: {company_name} ({ticker})")
        print(f"{'='*100}")
        
        company_results = {}
        
        for attr_name, query_term in attributes:
            print(f"\n📊 {attr_name}:")
            print("-"*100)
            
            # Test Annual
            annual_query = f"show {ticker} {query_term} for 2023"
            try:
                annual_result = await cfo_agent_graph.run(annual_query)
                if "No data" in annual_result or "No results" in annual_result or "error" in annual_result.lower():
                    annual_status = "❌ NO DATA"
                    annual_value = "N/A"
                else:
                    annual_status = "✅"
                    # Extract value from response
                    lines = annual_result.split('\n')
                    annual_value = lines[0][:80] + "..." if len(lines[0]) > 80 else lines[0]
                print(f"  Annual 2023: {annual_status} {annual_value}")
            except Exception as e:
                annual_status = "❌ ERROR"
                annual_value = str(e)[:50]
                print(f"  Annual 2023: {annual_status} {annual_value}")
            
            # Test Quarterly
            quarterly_query = f"show {ticker} {query_term} for Q2 2023"
            try:
                quarterly_result = await cfo_agent_graph.run(quarterly_query)
                if "No data" in quarterly_result or "No results" in quarterly_result or "error" in quarterly_result.lower():
                    quarterly_status = "❌ NO DATA"
                    quarterly_value = "N/A"
                else:
                    quarterly_status = "✅"
                    lines = quarterly_result.split('\n')
                    quarterly_value = lines[0][:80] + "..." if len(lines[0]) > 80 else lines[0]
                print(f"  Q2 2023:     {quarterly_status} {quarterly_value}")
            except Exception as e:
                quarterly_status = "❌ ERROR"
                quarterly_value = str(e)[:50]
                print(f"  Q2 2023:     {quarterly_status} {quarterly_value}")
            
            company_results[attr_name] = {
                'annual': annual_status,
                'quarterly': quarterly_status
            }
        
        results[company_name] = company_results
    
    # Summary Table
    print("\n" + "="*100)
    print("SUMMARY TABLE - ALL COMPANIES")
    print("="*100)
    print(f"\n{'Company':<20} {'Metric':<20} {'Annual':<15} {'Quarterly':<15}")
    print("-"*100)
    
    total_tests = 0
    passed_tests = 0
    
    for company_name, company_data in results.items():
        for metric_name, statuses in company_data.items():
            annual = statuses['annual']
            quarterly = statuses['quarterly']
            print(f"{company_name:<20} {metric_name:<20} {annual:<15} {quarterly:<15}")
            
            total_tests += 2
            if "✅" in annual:
                passed_tests += 1
            if "✅" in quarterly:
                passed_tests += 1
    
    print("\n" + "="*100)
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    print("="*100)
    
    # Company-by-company breakdown
    print("\n" + "="*100)
    print("COMPANY BREAKDOWN")
    print("="*100)
    
    for company_name, company_data in results.items():
        company_passed = sum(1 for metric_data in company_data.values() 
                           for status in metric_data.values() if "✅" in status)
        company_total = len(company_data) * 2
        print(f"{company_name:<20} {company_passed}/{company_total} passed ({company_passed/company_total*100:.0f}%)")
    
    await db_pool.close()
    
    return results


if __name__ == "__main__":
    results = asyncio.run(test_multiple_companies())
