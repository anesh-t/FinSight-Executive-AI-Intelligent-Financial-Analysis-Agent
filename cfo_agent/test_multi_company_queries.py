"""
Test queries asking for same metric across multiple companies
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_multi_company_queries():
    """Test queries that ask for metrics from multiple companies"""
    
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*120)
    print("TESTING MULTI-COMPANY QUERIES - Same Metric Across Multiple Companies")
    print("="*120)
    
    # Test cases: (label, query, expected_companies, expected_metric)
    test_cases = [
        # 2 companies
        ("Annual: R&D for 2 companies",
         "show R&D expenses for amazon and microsoft in 2023",
         ["Amazon", "Microsoft"],
         "R&D"),
        
        ("Annual: Revenue for 2 companies",
         "show revenue for apple and google in 2023",
         ["Apple", "Google"],
         "revenue"),
        
        ("Annual: Net income for 2 companies",
         "show net income for microsoft and meta in 2023",
         ["Microsoft", "Meta"],
         "net income"),
        
        # 3 companies
        ("Annual: Revenue for 3 companies",
         "show revenue for apple, microsoft and google in 2023",
         ["Apple", "Microsoft", "Google"],
         "revenue"),
        
        ("Annual: Operating cash flow for 3 companies",
         "show operating cash flow for amazon, apple, and microsoft in 2023",
         ["Amazon", "Apple", "Microsoft"],
         "operating cash flow"),
        
        ("Annual: EPS for 3 companies",
         "show EPS for apple, microsoft, and google in 2023",
         ["Apple", "Microsoft", "Google"],
         "EPS"),
        
        # Quarterly queries
        ("Quarterly: Revenue for 2 companies",
         "show revenue for microsoft and apple in Q2 2023",
         ["Microsoft", "Apple"],
         "revenue"),
        
        ("Quarterly: Net income for 3 companies",
         "show net income for apple, google, and amazon in Q2 2023",
         ["Apple", "Google", "Amazon"],
         "net income"),
        
        # Different variations
        ("Annual: Total assets for 2 companies",
         "show total assets for amazon and meta in 2023",
         ["Amazon", "Meta"],
         "total assets"),
        
        ("Annual: SG&A for 3 companies",
         "show SG&A expenses for microsoft, apple, and google in 2023",
         ["Microsoft", "Apple", "Google"],
         "SG&A"),
    ]
    
    results = []
    
    for label, query, expected_companies, expected_metric in test_cases:
        print(f"\n{'='*120}")
        print(f"Test: {label}")
        print(f"Query: '{query}'")
        print(f"Expected: {expected_metric} for {', '.join(expected_companies)}")
        print("="*120)
        
        try:
            result = await cfo_agent_graph.run(query)
            
            # Check if we got a response
            if not result or "No data" in result or "No results" in result:
                print("❌ FAILED: No data returned")
                results.append({
                    'label': label,
                    'status': '❌ FAILED',
                    'reason': 'No data',
                    'found': 0,
                    'expected': len(expected_companies)
                })
                continue
            
            # Print the response
            print("\nResponse:")
            print("-"*120)
            print(result)
            print("-"*120)
            
            # Check if all expected companies are present
            result_lower = result.lower()
            found_companies = []
            missing_companies = []
            
            for company in expected_companies:
                # Check for company name variations
                company_variations = [
                    company.lower(),
                    company.upper(),
                    # Specific mappings
                    "amazon.com" if company.lower() == "amazon" else "",
                    "alphabet" if company.lower() == "google" else "",
                    "meta platforms" if company.lower() == "meta" else "",
                ]
                
                if any(var in result_lower for var in company_variations if var):
                    found_companies.append(company)
                else:
                    missing_companies.append(company)
            
            # Check if metric is present
            metric_present = expected_metric.lower() in result_lower
            
            # Check if there are extra companies (should only show requested ones)
            all_companies = ["apple", "microsoft", "google", "amazon", "meta"]
            extra_companies = []
            for company in all_companies:
                if company in result_lower and company not in [c.lower() for c in expected_companies]:
                    extra_companies.append(company)
            
            # Evaluate result
            if missing_companies:
                status = "⚠️  PARTIAL"
                reason = f"Missing: {', '.join(missing_companies)}"
                print(f"\n{status} {reason}")
            elif not metric_present:
                status = "⚠️  NO METRIC"
                reason = f"'{expected_metric}' not found in response"
                print(f"\n{status} {reason}")
            elif extra_companies:
                status = "⚠️  EXTRA"
                reason = f"Showing extra companies: {', '.join(extra_companies)}"
                print(f"\n{status} {reason}")
            else:
                status = "✅ SUCCESS"
                reason = f"All {len(found_companies)} companies with {expected_metric}"
                print(f"\n{status} {reason}")
            
            results.append({
                'label': label,
                'status': status,
                'found': len(found_companies),
                'expected': len(expected_companies),
                'metric': metric_present
            })
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)[:100]}")
            results.append({
                'label': label,
                'status': '❌ ERROR',
                'reason': str(e)[:50],
                'found': 0,
                'expected': len(expected_companies)
            })
    
    # Summary
    print("\n" + "="*120)
    print("SUMMARY: MULTI-COMPANY QUERY TEST RESULTS")
    print("="*120)
    
    print(f"\n{'Test Case':<50} {'Status':<15} {'Found/Expected':<20} {'Metric OK':<15}")
    print("-"*120)
    
    success_count = 0
    partial_count = 0
    failed_count = 0
    
    for result in results:
        label = result['label'][:48]
        status = result['status']
        
        found_expected = f"{result['found']}/{result['expected']}"
        metric = "✅" if result.get('metric', False) else "❌"
        
        print(f"{label:<50} {status:<15} {found_expected:<20} {metric:<15}")
        
        if "✅" in status:
            success_count += 1
        elif "⚠️" in status:
            partial_count += 1
        else:
            failed_count += 1
    
    total = len(results)
    print("\n" + "="*120)
    print(f"RESULTS: ✅ Success: {success_count}/{total} | ⚠️  Partial: {partial_count}/{total} | ❌ Failed: {failed_count}/{total}")
    
    if success_count > 0:
        print(f"Success Rate: {(success_count/total*100):.1f}%")
    
    print("="*120)
    
    # Recommendations
    if failed_count > 0 or partial_count > 0:
        print("\n⚠️  NOTE: Multi-company queries may require multiple separate queries or comparison templates.")
        print("   Current system may be designed for single-company queries.")
    
    await db_pool.close()
    
    return results


if __name__ == "__main__":
    asyncio.run(test_multi_company_queries())
