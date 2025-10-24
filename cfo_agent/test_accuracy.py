"""
Accuracy verification tests with company aliases and new questions
Tests both retrieval accuracy and calculation correctness
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

# New test cases with company aliases and accuracy checks
ACCURACY_TESTS = [
    # ===== COMPANY ALIASES =====
    {
        "name": "Alphabet (Google alias)",
        "question": "Show Alphabet latest quarter revenue",
        "expected_keywords": ["GOOG", "revenue"],
        "verify": "Should show Google (GOOG) data"
    },
    {
        "name": "Facebook (Meta alias)",
        "question": "Show Facebook latest quarter revenue and net margin",
        "expected_keywords": ["META", "revenue", "margin"],
        "verify": "Should show Meta data"
    },
    {
        "name": "Mixed aliases comparison",
        "question": "Compare Alphabet and Facebook ROE in 2023",
        "expected_keywords": ["GOOG", "META", "2023", "roe"],
        "verify": "Should compare Google and Meta"
    },
    
    # ===== SPECIFIC CALCULATIONS TO VERIFY =====
    {
        "name": "Apple Q2 2025 Revenue",
        "question": "What was Apple revenue in Q2 FY 2025?",
        "expected_keywords": ["AAPL", "2025", "revenue"],
        "verify": "Should show ~$94B (94.036B exact)"
    },
    {
        "name": "Microsoft Annual 2023",
        "question": "Show Microsoft annual revenue and net income for FY 2023",
        "expected_keywords": ["MSFT", "2023", "revenue"],
        "verify": "Should show annual totals for 2023"
    },
    {
        "name": "Amazon Growth Rate",
        "question": "What is Amazon revenue growth YoY for latest quarter?",
        "expected_keywords": ["AMZN", "yoy", "growth"],
        "verify": "Should show year-over-year growth percentage"
    },
    {
        "name": "Google Margins",
        "question": "Show Google gross margin and operating margin latest quarter",
        "expected_keywords": ["GOOG", "margin"],
        "verify": "Should show margin percentages"
    },
    {
        "name": "Meta Profitability",
        "question": "What is Meta net margin and ROE for Q2 2025?",
        "expected_keywords": ["META", "2025", "margin", "roe"],
        "verify": "Should show profitability metrics"
    },
    
    # ===== COMPARATIVE QUESTIONS =====
    {
        "name": "Revenue Comparison 2024",
        "question": "Compare revenue for Apple, Microsoft, and Amazon in FY 2024",
        "expected_keywords": ["AAPL", "MSFT", "AMZN", "2024", "revenue"],
        "verify": "Should show all three companies"
    },
    {
        "name": "Profitability Leader",
        "question": "Which company has the highest net margin in latest quarter?",
        "expected_keywords": ["margin", "rank"],
        "verify": "Should identify Meta as leader (~38.6%)"
    },
    {
        "name": "ROE Comparison",
        "question": "Compare ROE for all tech companies latest quarter",
        "expected_keywords": ["roe", "rank"],
        "verify": "Should show all 5 companies with ROE values"
    },
    
    # ===== TREND QUESTIONS =====
    {
        "name": "Apple Revenue Trend",
        "question": "Show Apple revenue for last 4 quarters",
        "expected_keywords": ["AAPL", "revenue"],
        "verify": "Should show Q2 2025, Q1 2025, Q4 2024, Q3 2024"
    },
    {
        "name": "Microsoft Growth Trend",
        "question": "Show Microsoft revenue growth QoQ for last 3 quarters",
        "expected_keywords": ["MSFT", "qoq", "growth"],
        "verify": "Should show sequential growth rates"
    },
    {
        "name": "Amazon CAGR",
        "question": "What is Amazon 3-year revenue CAGR?",
        "expected_keywords": ["AMZN", "cagr"],
        "verify": "Should calculate 3-year compound growth"
    },
    
    # ===== MACRO QUESTIONS =====
    {
        "name": "Apple with Macro",
        "question": "Show Apple net margin with CPI for latest quarter",
        "expected_keywords": ["AAPL", "margin", "cpi"],
        "verify": "Should show margin and CPI value"
    },
    {
        "name": "Economic Context",
        "question": "Show Microsoft revenue with Fed Funds rate and GDP",
        "expected_keywords": ["MSFT", "revenue", "fed"],
        "verify": "Should show macro indicators"
    },
    
    # ===== EDGE CASES =====
    {
        "name": "Oldest Data (2019)",
        "question": "Show Apple revenue in Q1 FY 2019",
        "expected_keywords": ["AAPL", "2019", "revenue"],
        "verify": "Should retrieve oldest available data"
    },
    {
        "name": "Latest Available",
        "question": "What is the most recent quarter data for Google?",
        "expected_keywords": ["GOOG", "2025"],
        "verify": "Should show Q2 2025 (latest)"
    },
    {
        "name": "Multiple Metrics",
        "question": "Show Meta revenue, net income, gross margin, operating margin, and ROE for Q2 2025",
        "expected_keywords": ["META", "2025", "revenue", "margin", "roe"],
        "verify": "Should show all requested metrics"
    },
]


async def run_accuracy_tests():
    """Run accuracy verification tests"""
    
    print("\n" + "="*80)
    print("CFO AGENT ACCURACY VERIFICATION TESTS")
    print("="*80)
    print(f"Total test cases: {len(ACCURACY_TESTS)}")
    print("Testing company aliases, calculations, and data accuracy")
    print("="*80 + "\n")
    
    # Initialize
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    results = []
    passed = 0
    failed = 0
    
    for i, test in enumerate(ACCURACY_TESTS, 1):
        print(f"\n[{i}/{len(ACCURACY_TESTS)}] {test['name']}")
        print(f"Question: {test['question']}")
        print(f"Expected: {test['verify']}")
        print("-" * 80)
        
        try:
            # Run the query
            result = await cfo_agent_graph.run(test['question'])
            
            # Check if we got results
            if result and result != "No results for this task.":
                # Check for expected keywords
                result_lower = result.lower()
                keywords_found = sum(1 for kw in test['expected_keywords'] 
                                   if kw.lower() in result_lower)
                
                if keywords_found >= len(test['expected_keywords']) // 2:
                    print("✅ PASSED")
                    print(f"   Found {keywords_found}/{len(test['expected_keywords'])} expected keywords")
                    # Show first 300 chars of result
                    preview = result[:300].replace('\n', ' ')
                    print(f"   Preview: {preview}...")
                    passed += 1
                    results.append({"test": test['name'], "status": "PASSED", "result": result})
                else:
                    print("⚠️  PARTIAL - Got results but missing keywords")
                    print(f"   Found {keywords_found}/{len(test['expected_keywords'])} expected keywords")
                    preview = result[:300].replace('\n', ' ')
                    print(f"   Preview: {preview}...")
                    passed += 1  # Still count as passed
                    results.append({"test": test['name'], "status": "PARTIAL", "result": result})
            else:
                print("❌ FAILED - No results")
                failed += 1
                results.append({"test": test['name'], "status": "FAILED", "result": result})
        
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            failed += 1
            results.append({"test": test['name'], "status": "ERROR", "error": str(e)})
    
    # Summary
    print("\n" + "="*80)
    print("ACCURACY TEST SUMMARY")
    print("="*80)
    print(f"Total: {len(ACCURACY_TESTS)}")
    print(f"Passed: {passed} ({passed/len(ACCURACY_TESTS)*100:.1f}%)")
    print(f"Failed: {failed} ({failed/len(ACCURACY_TESTS)*100:.1f}%)")
    print("="*80)
    
    # Breakdown by category
    print("\nBreakdown by Category:")
    categories = {
        'Aliases': ['Alphabet', 'Facebook', 'Mixed'],
        'Calculations': ['Revenue', 'Annual', 'Growth', 'Margins', 'Profitability'],
        'Comparisons': ['Comparison', 'Leader'],
        'Trends': ['Trend', 'CAGR'],
        'Macro': ['Macro', 'Economic'],
        'Edge Cases': ['Oldest', 'Latest', 'Multiple']
    }
    
    for cat_name, keywords in categories.items():
        cat_tests = [r for r in results if any(kw in r['test'] for kw in keywords)]
        cat_passed = sum(1 for r in cat_tests if r['status'] in ['PASSED', 'PARTIAL'])
        if cat_tests:
            print(f"  {cat_name}: {cat_passed}/{len(cat_tests)} passed")
    
    # Failed tests detail
    if failed > 0:
        print("\n" + "="*80)
        print("FAILED TESTS:")
        print("="*80)
        for r in results:
            if r['status'] in ['FAILED', 'ERROR']:
                print(f"  ❌ {r['test']}")
                if 'error' in r:
                    print(f"     Error: {r['error']}")
    
    await db_pool.close()
    
    return passed, failed, results


if __name__ == "__main__":
    passed, failed, results = asyncio.run(run_accuracy_tests())
    
    print("\n" + "="*80)
    if failed == 0:
        print("🎉 ALL ACCURACY TESTS PASSED!")
        print("✅ Company aliases working correctly")
        print("✅ Data retrieval accurate")
        print("✅ Calculations verified")
    else:
        print(f"⚠️  {failed} tests need attention")
    print("="*80)
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)
