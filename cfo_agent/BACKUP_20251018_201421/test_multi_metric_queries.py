"""
Test queries asking for multiple metrics at once
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_multi_metric_queries():
    """Test queries that ask for multiple financial metrics"""
    
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*120)
    print("TESTING MULTI-METRIC QUERIES - Asking for Multiple Values at Once")
    print("="*120)
    
    # Test cases: (label, query, expected_metrics)
    test_cases = [
        # Annual queries
        ("Annual: Revenue + Net Income", 
         "show microsoft revenue and net income for 2023",
         ["revenue", "net income"]),
        
        ("Annual: Revenue + Operating Income + Net Income",
         "show apple revenue, operating income and net income for 2023",
         ["revenue", "operating income", "net income"]),
        
        ("Annual: All Income Statement Items",
         "show google revenue, operating income, net income, and gross profit for 2023",
         ["revenue", "operating income", "net income", "gross profit"]),
        
        ("Annual: Expenses",
         "show microsoft R&D and SG&A expenses for 2023",
         ["R&D", "SG&A"]),
        
        ("Annual: Cash Flows",
         "show amazon operating cash flow and investing cash flow for 2023",
         ["operating cash flow", "investing cash flow"]),
        
        ("Annual: Balance Sheet",
         "show apple total assets, total liabilities and equity for 2023",
         ["total assets", "total liabilities", "equity"]),
        
        ("Annual: Mixed Metrics",
         "show meta revenue, net income, EPS and operating cash flow for 2023",
         ["revenue", "net income", "EPS", "operating cash flow"]),
        
        # Quarterly queries
        ("Quarterly: Revenue + Net Income",
         "show microsoft revenue and net income for Q2 2023",
         ["revenue", "net income"]),
        
        ("Quarterly: Multiple Income Items",
         "show apple revenue, operating income, and net income for Q3 2023",
         ["revenue", "operating income", "net income"]),
        
        ("Quarterly: Expenses",
         "show google R&D expenses and SG&A expenses for Q2 2023",
         ["R&D", "SG&A"]),
        
        ("Quarterly: Cash Flows",
         "show amazon operating cash flow, investing cash flow, and financing cash flow for Q2 2023",
         ["operating cash flow", "investing cash flow", "financing cash flow"]),
        
        ("Quarterly: Balance Sheet",
         "show microsoft total assets and equity for Q2 2023",
         ["total assets", "equity"]),
    ]
    
    results = []
    
    for label, query, expected_metrics in test_cases:
        print(f"\n{'='*120}")
        print(f"Test: {label}")
        print(f"Query: '{query}'")
        print(f"Expected metrics: {', '.join(expected_metrics)}")
        print("="*120)
        
        try:
            result = await cfo_agent_graph.run(query)
            
            # Check if we got a response
            if not result or "No data" in result or "No results" in result:
                print("❌ FAILED: No data returned")
                results.append({
                    'label': label,
                    'status': 'FAILED',
                    'reason': 'No data'
                })
                continue
            
            # Print the response
            print("\nResponse:")
            print("-"*120)
            print(result)
            print("-"*120)
            
            # Check if all expected metrics are present
            result_lower = result.lower()
            found_metrics = []
            missing_metrics = []
            
            for metric in expected_metrics:
                if metric.lower() in result_lower:
                    found_metrics.append(metric)
                else:
                    missing_metrics.append(metric)
            
            # Check if there are extra metrics (should be selective)
            all_possible_metrics = [
                "revenue", "operating income", "net income", "gross profit",
                "r&d", "sg&a", "cogs", "ebit", "ebitda",
                "operating cash flow", "investing cash flow", "financing cash flow",
                "total assets", "total liabilities", "equity",
                "eps", "capex", "dividends", "buybacks"
            ]
            
            extra_metrics = []
            for metric in all_possible_metrics:
                if metric.lower() in result_lower and metric not in [e.lower() for e in expected_metrics]:
                    extra_metrics.append(metric)
            
            # Evaluate result
            if missing_metrics:
                status = "⚠️  PARTIAL"
                reason = f"Missing: {', '.join(missing_metrics)}"
                print(f"\n{status} {reason}")
            elif extra_metrics:
                status = "⚠️  EXTRA"
                reason = f"Showing extra: {', '.join(extra_metrics[:3])}"
                print(f"\n{status} {reason}")
            else:
                status = "✅ SUCCESS"
                reason = f"All {len(found_metrics)} metrics returned correctly"
                print(f"\n{status} {reason}")
            
            results.append({
                'label': label,
                'status': status,
                'found': len(found_metrics),
                'expected': len(expected_metrics),
                'extra': len(extra_metrics)
            })
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)[:100]}")
            results.append({
                'label': label,
                'status': 'ERROR',
                'reason': str(e)[:50]
            })
    
    # Summary
    print("\n" + "="*120)
    print("SUMMARY: MULTI-METRIC QUERY TEST RESULTS")
    print("="*120)
    
    print(f"\n{'Test Case':<50} {'Status':<15} {'Found/Expected':<20} {'Extra Metrics':<15}")
    print("-"*120)
    
    success_count = 0
    partial_count = 0
    failed_count = 0
    
    for result in results:
        label = result['label'][:48]
        status = result['status']
        
        if 'found' in result:
            found_expected = f"{result['found']}/{result['expected']}"
            extra = str(result['extra'])
        else:
            found_expected = "N/A"
            extra = "N/A"
        
        print(f"{label:<50} {status:<15} {found_expected:<20} {extra:<15}")
        
        if "✅" in status:
            success_count += 1
        elif "⚠️" in status:
            partial_count += 1
        else:
            failed_count += 1
    
    total = len(results)
    print("\n" + "="*120)
    print(f"RESULTS: ✅ Success: {success_count}/{total} | ⚠️  Partial: {partial_count}/{total} | ❌ Failed: {failed_count}/{total}")
    print(f"Success Rate: {(success_count/total*100):.1f}%")
    print("="*120)
    
    await db_pool.close()
    
    return results


if __name__ == "__main__":
    asyncio.run(test_multi_metric_queries())
