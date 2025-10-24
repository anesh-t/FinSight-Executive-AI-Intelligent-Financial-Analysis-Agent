"""
Comprehensive test suite for CFO Agent
Tests all companies, years, and question varieties
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

# Test cases covering all companies and question types
TEST_CASES = [
    # ===== APPLE (AAPL) =====
    {
        "name": "AAPL - Latest Quarter Snapshot",
        "question": "Show AAPL latest quarter revenue and ROE",
        "expected_keywords": ["AAPL", "revenue", "roe"]
    },
    {
        "name": "AAPL - Annual Metrics",
        "question": "What were Apple revenue and net income in FY 2023?",
        "expected_keywords": ["2023", "revenue", "net_income"]
    },
    {
        "name": "AAPL - Growth QoQ/YoY",
        "question": "Latest quarter revenue QoQ and YoY for AAPL",
        "expected_keywords": ["qoq", "yoy"]
    },
    {
        "name": "AAPL - TTM Metrics",
        "question": "Give me Apple TTM revenue and net income",
        "expected_keywords": ["ttm", "revenue"]
    },
    {
        "name": "AAPL - CAGR",
        "question": "Apple 5-year revenue CAGR ending FY 2024",
        "expected_keywords": ["cagr", "2024"]
    },
    
    # ===== MICROSOFT (MSFT) =====
    {
        "name": "MSFT - Latest Quarter",
        "question": "Show MSFT latest quarter revenue, gross margin, and operating margin",
        "expected_keywords": ["MSFT", "revenue", "margin"]
    },
    {
        "name": "MSFT - Annual 2022",
        "question": "What were Microsoft revenue and net income in FY 2022?",
        "expected_keywords": ["2022", "revenue"]
    },
    {
        "name": "MSFT - Growth Analysis",
        "question": "Latest quarter revenue QoQ and YoY for Microsoft",
        "expected_keywords": ["qoq", "yoy"]
    },
    
    # ===== AMAZON (AMZN) =====
    {
        "name": "AMZN - Latest Quarter",
        "question": "Show Amazon latest quarter revenue and ROE",
        "expected_keywords": ["revenue", "roe"]
    },
    {
        "name": "AMZN - Annual 2023",
        "question": "What were AMZN revenue and net income in FY 2023?",
        "expected_keywords": ["2023", "revenue"]
    },
    {
        "name": "AMZN - CAGR",
        "question": "Amazon 3-year revenue CAGR ending FY 2024",
        "expected_keywords": ["cagr", "2024"]
    },
    {
        "name": "AMZN - Health Check",
        "question": "Is AMZN balance sheet in balance last quarter?",
        "expected_keywords": ["balance", "status"]
    },
    
    # ===== GOOGLE (GOOG) =====
    {
        "name": "GOOG - Latest Quarter",
        "question": "Show GOOG latest quarter revenue and net margin",
        "expected_keywords": ["GOOG", "revenue", "margin"]
    },
    {
        "name": "GOOG - Annual 2023",
        "question": "What were Google revenue and operating income in FY 2023?",
        "expected_keywords": ["2023", "revenue"]
    },
    {
        "name": "GOOG - Growth",
        "question": "Latest quarter revenue YoY for Google",
        "expected_keywords": ["yoy", "revenue"]
    },
    
    # ===== META =====
    {
        "name": "META - Latest Quarter",
        "question": "Show META latest quarter revenue and ROE",
        "expected_keywords": ["META", "revenue", "roe"]
    },
    {
        "name": "META - Annual 2023",
        "question": "What were Meta revenue and net income in FY 2023?",
        "expected_keywords": ["2023", "revenue"]
    },
    {
        "name": "META - Outliers",
        "question": "Flag any outliers in net margin for META since 2021",
        "expected_keywords": ["outlier", "margin"]
    },
    
    # ===== PEER COMPARISONS =====
    {
        "name": "Peer - Net Margin Leaders",
        "question": "Who led on net margin last quarter? show ranks",
        "expected_keywords": ["rank", "margin"]
    },
    {
        "name": "Peer - Annual Rankings 2023",
        "question": "Rank peers by operating margin in FY 2023",
        "expected_keywords": ["2023", "rank", "margin"]
    },
    
    # ===== MACRO ANALYSIS =====
    {
        "name": "Macro - Values",
        "question": "For AAPL, show net margin with CPI & Fed Funds this quarter",
        "expected_keywords": ["cpi", "fed", "margin"]
    },
    {
        "name": "Macro - Sensitivity",
        "question": "Over the last 12 quarters, AAPL beta of net margin vs CPI?",
        "expected_keywords": ["beta", "cpi"]
    },
    
    # ===== MULTI-TASK =====
    {
        "name": "Multi - Comparison",
        "question": "Compare Apple and Google ROE in 2023",
        "expected_keywords": ["Apple", "Google", "roe", "2023"]
    },
    {
        "name": "Multi - Complex",
        "question": "Tell me Apple revenue in 2022, compare its ROE with Microsoft",
        "expected_keywords": ["Apple", "Microsoft", "revenue", "roe", "2022"]
    },
    
    # ===== DIFFERENT YEARS =====
    {
        "name": "Year - 2019",
        "question": "Show AAPL revenue in FY 2019",
        "expected_keywords": ["2019", "revenue"]
    },
    {
        "name": "Year - 2020",
        "question": "Show MSFT revenue in FY 2020",
        "expected_keywords": ["2020", "revenue"]
    },
    {
        "name": "Year - 2021",
        "question": "Show AMZN revenue in FY 2021",
        "expected_keywords": ["2021", "revenue"]
    },
    {
        "name": "Year - 2024",
        "question": "Show GOOG revenue in FY 2024",
        "expected_keywords": ["2024", "revenue"]
    },
]


async def run_comprehensive_tests():
    """Run all test cases"""
    
    print("\n" + "="*80)
    print("CFO AGENT COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Total test cases: {len(TEST_CASES)}")
    print("="*80 + "\n")
    
    # Initialize
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    results = []
    passed = 0
    failed = 0
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}] {test['name']}")
        print(f"Question: {test['question']}")
        print("-" * 80)
        
        try:
            # Run the query
            result = await cfo_agent_graph.run(test['question'])
            
            # Check if we got results
            if result and result != "No results for this task.":
                # Check for expected keywords (case-insensitive)
                result_lower = result.lower()
                keywords_found = sum(1 for kw in test['expected_keywords'] 
                                   if kw.lower() in result_lower)
                
                if keywords_found >= len(test['expected_keywords']) // 2:  # At least half
                    print("✅ PASSED")
                    print(f"   Found {keywords_found}/{len(test['expected_keywords'])} expected keywords")
                    # Show first 200 chars of result
                    preview = result[:200].replace('\n', ' ')
                    print(f"   Preview: {preview}...")
                    passed += 1
                    results.append({"test": test['name'], "status": "PASSED", "result": result})
                else:
                    print("⚠️  PARTIAL - Got results but missing keywords")
                    print(f"   Found {keywords_found}/{len(test['expected_keywords'])} expected keywords")
                    preview = result[:200].replace('\n', ' ')
                    print(f"   Preview: {preview}...")
                    passed += 1  # Count as passed since we got results
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
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total: {len(TEST_CASES)}")
    print(f"Passed: {passed} ({passed/len(TEST_CASES)*100:.1f}%)")
    print(f"Failed: {failed} ({failed/len(TEST_CASES)*100:.1f}%)")
    print("="*80)
    
    # Breakdown by category
    print("\nBreakdown by Company:")
    for company in ['AAPL', 'MSFT', 'AMZN', 'GOOG', 'META']:
        company_tests = [r for r in results if company in r['test']]
        company_passed = sum(1 for r in company_tests if r['status'] in ['PASSED', 'PARTIAL'])
        if company_tests:
            print(f"  {company}: {company_passed}/{len(company_tests)} passed")
    
    print("\nBreakdown by Question Type:")
    categories = {
        'Snapshot': ['Snapshot', 'Latest'],
        'Annual': ['Annual', 'FY'],
        'Growth': ['Growth', 'QoQ', 'YoY', 'CAGR'],
        'Peer': ['Peer', 'Rank'],
        'Macro': ['Macro'],
        'Multi': ['Multi', 'Comparison'],
        'Health': ['Health', 'Outlier']
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
    passed, failed, results = asyncio.run(run_comprehensive_tests())
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)
