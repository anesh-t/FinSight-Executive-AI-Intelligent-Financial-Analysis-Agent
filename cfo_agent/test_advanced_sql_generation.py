"""
Test Advanced SQL Generation with LLM
Tests the upgraded generative SQL system with diverse queries
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generative_sql import GenerativeSQLBuilder
from db.whitelist import validate_sql, load_schema_cache
from dotenv import load_dotenv

load_dotenv()


# Test queries covering different scenarios
TEST_QUERIES = [
    # Test 1: Multiple metrics (should use vw_company_complete_quarter)
    {
        "name": "Multiple Metrics - Basic",
        "context": {
            "intent": "Get multiple financial metrics for a single quarter",
            "surfaces": ["vw_company_complete_quarter"],
            "entities_resolved": {"Apple": "AAPL"},
            "params": {"ticker": "AAPL", "fy": 2023, "fq": 2, "limit": 10}
        },
        "expected_view": "vw_company_complete_quarter"
    },
    
    # Test 2: With macro context (should use vw_company_macro_context_quarter)
    {
        "name": "Multiple Metrics with Macro Context",
        "context": {
            "intent": "Get revenue and margins with GDP and CPI context",
            "surfaces": ["vw_company_macro_context_quarter"],
            "entities_resolved": {"Microsoft": "MSFT"},
            "params": {"ticker": "MSFT", "fy": 2023, "fq": 1, "limit": 10}
        },
        "expected_view": "vw_company_macro_context_quarter"
    },
    
    # Test 3: Growth analysis (should use vw_growth_quarter)
    {
        "name": "Growth Analysis - YoY",
        "context": {
            "intent": "Get revenue growth YoY for last 4 quarters",
            "surfaces": ["vw_growth_quarter"],
            "entities_resolved": {"Apple": "AAPL"},
            "params": {"ticker": "AAPL", "fy": 2023, "fq": None, "limit": 10}
        },
        "expected_view": "vw_growth_quarter"
    },
    
    # Test 4: Peer comparison (should use vw_peer_stats_quarter)
    {
        "name": "Peer Comparison",
        "context": {
            "intent": "Compare gross margins across companies",
            "surfaces": ["vw_company_complete_quarter", "vw_peer_stats_quarter"],
            "entities_resolved": {"Apple": "AAPL", "Microsoft": "MSFT"},
            "params": {"t1": "AAPL", "t2": "MSFT", "fy": 2023, "fq": 2, "limit": 10}
        },
        "expected_view": "vw_peer_stats_quarter"
    },
    
    # Test 5: Sensitivity analysis (should use vw_company_full_quarter)
    {
        "name": "Sensitivity Analysis",
        "context": {
            "intent": "How sensitive is margin to CPI changes",
            "surfaces": ["vw_company_full_quarter"],
            "entities_resolved": {"Apple": "AAPL"},
            "params": {"ticker": "AAPL", "fy": 2023, "fq": 2, "limit": 10}
        },
        "expected_view": "vw_company_full_quarter"
    },
    
    # Test 6: Annual data (should use mv_company_complete_annual)
    {
        "name": "Annual Metrics",
        "context": {
            "intent": "Get annual revenue and margins for 2023",
            "surfaces": ["mv_company_complete_annual"],
            "entities_resolved": {"Google": "GOOGL"},
            "params": {"ticker": "GOOGL", "fy": 2023, "fq": None, "limit": 10}
        },
        "expected_view": "mv_company_complete_annual"
    },
    
    # Test 7: Latest period (should use vw_latest_company_quarter)
    {
        "name": "Latest Period",
        "context": {
            "intent": "Get latest available quarter data",
            "surfaces": ["vw_company_complete_quarter", "vw_latest_company_quarter"],
            "entities_resolved": {"Amazon": "AMZN"},
            "params": {"ticker": "AMZN", "fy": None, "fq": None, "limit": 10}
        },
        "expected_view": "vw_latest_company_quarter"
    },
    
    # Test 8: Specific expense details (should use fact_financials)
    {
        "name": "Specific Expenses - R&D",
        "context": {
            "intent": "Get R&D expenses and SG&A expenses",
            "surfaces": ["fact_financials"],
            "entities_resolved": {"Apple": "AAPL"},
            "params": {"ticker": "AAPL", "fy": 2023, "fq": 2, "limit": 10}
        },
        "expected_view": "fact_financials"
    },
    
    # Test 9: Stock price analysis (should use vw_stock_prices_quarter)
    {
        "name": "Stock Price Analysis",
        "context": {
            "intent": "Get stock price, returns, and volatility",
            "surfaces": ["vw_stock_prices_quarter"],
            "entities_resolved": {"Meta": "META"},
            "params": {"ticker": "META", "fy": 2023, "fq": 2, "limit": 10}
        },
        "expected_view": "vw_stock_prices_quarter"
    },
    
    # Test 10: Complex multi-company time series
    {
        "name": "Complex Multi-Company Time Series",
        "context": {
            "intent": "Compare revenue trends for multiple companies over time",
            "surfaces": ["vw_company_complete_quarter"],
            "entities_resolved": {"Apple": "AAPL", "Microsoft": "MSFT", "Google": "GOOGL"},
            "params": {"fy": 2023, "fq": None, "limit": 20}
        },
        "expected_view": "vw_company_complete_quarter"
    },
]


async def test_sql_generation():
    """Test SQL generation with various query types"""
    
    print("=" * 80)
    print("🧪 TESTING ADVANCED SQL GENERATION")
    print("=" * 80)
    
    # Load schema cache
    print("\n📋 Loading schema cache...")
    try:
        await load_schema_cache()
        print("✅ Schema cache loaded")
    except Exception as e:
        print(f"⚠️  Warning: Could not load schema cache: {e}")
        print("   Continuing without schema validation...")
    
    # Initialize builder
    builder = GenerativeSQLBuilder()
    
    # Track results
    total_tests = len(TEST_QUERIES)
    passed = 0
    failed = 0
    results = []
    
    print(f"\n🚀 Running {total_tests} test queries...\n")
    
    for i, test in enumerate(TEST_QUERIES, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{total_tests}: {test['name']}")
        print(f"{'='*80}")
        
        context = test['context']
        expected_view = test.get('expected_view')
        
        print(f"\n📝 Context:")
        print(f"   Intent: {context['intent']}")
        print(f"   Entities: {context['entities_resolved']}")
        print(f"   Parameters: {context['params']}")
        
        try:
            # Generate SQL
            print(f"\n⏳ Generating SQL...")
            candidates = await builder.generate_sql(context)
            
            if not candidates:
                print(f"❌ FAILED: No SQL candidates generated")
                failed += 1
                results.append({
                    "test": test['name'],
                    "status": "FAILED",
                    "error": "No candidates generated"
                })
                continue
            
            # Test each candidate
            valid_candidate = None
            for j, (sql, params) in enumerate(candidates, 1):
                print(f"\n🔍 Candidate {j}:")
                print(f"{'─'*80}")
                print(sql)
                print(f"{'─'*80}")
                print(f"Parameters: {params}")
                
                # Validate SQL
                is_valid, error_msg = validate_sql(sql, params)
                
                if is_valid:
                    print(f"✅ VALID SQL")
                    valid_candidate = (sql, params)
                    
                    # Check if expected view is used
                    if expected_view:
                        if expected_view.lower() in sql.lower():
                            print(f"✅ Uses expected view: {expected_view}")
                        else:
                            print(f"⚠️  Warning: Expected {expected_view} but not found in SQL")
                    
                    break
                else:
                    print(f"❌ INVALID: {error_msg}")
            
            if valid_candidate:
                passed += 1
                results.append({
                    "test": test['name'],
                    "status": "PASSED",
                    "sql": valid_candidate[0],
                    "params": valid_candidate[1]
                })
                print(f"\n✅ TEST PASSED")
            else:
                failed += 1
                results.append({
                    "test": test['name'],
                    "status": "FAILED",
                    "error": "All candidates failed validation"
                })
                print(f"\n❌ TEST FAILED: All candidates invalid")
                
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            failed += 1
            results.append({
                "test": test['name'],
                "status": "ERROR",
                "error": str(e)
            })
    
    # Print summary
    print(f"\n\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    print(f"\nTotal Tests: {total_tests}")
    print(f"✅ Passed: {passed} ({passed/total_tests*100:.1f}%)")
    print(f"❌ Failed: {failed} ({failed/total_tests*100:.1f}%)")
    
    # Print detailed results
    print(f"\n\n{'='*80}")
    print("📋 DETAILED RESULTS")
    print(f"{'='*80}")
    
    for result in results:
        status_icon = "✅" if result['status'] == "PASSED" else "❌"
        print(f"\n{status_icon} {result['test']}: {result['status']}")
        if result['status'] == "FAILED" or result['status'] == "ERROR":
            print(f"   Error: {result.get('error', 'Unknown')}")
    
    # Print recommendations
    print(f"\n\n{'='*80}")
    print("💡 RECOMMENDATIONS")
    print(f"{'='*80}")
    
    if passed == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your advanced SQL generation is working perfectly!")
        print("✅ Ready for production use")
    elif passed >= total_tests * 0.9:
        print(f"\n✅ Excellent! {passed}/{total_tests} tests passed")
        print("✅ System is production-ready with minor issues")
        print("💡 Review failed tests and refine prompt if needed")
    elif passed >= total_tests * 0.7:
        print(f"\n⚠️  Good progress: {passed}/{total_tests} tests passed")
        print("💡 Review failed tests and update prompt")
        print("💡 May need to add more examples for failed patterns")
    else:
        print(f"\n⚠️  Needs improvement: {passed}/{total_tests} tests passed")
        print("💡 Review prompt and add more guidance")
        print("💡 Check schema cache is loaded correctly")
        print("💡 Verify OpenAI API key is set")
    
    return passed, failed, results


async def main():
    """Main test runner"""
    try:
        passed, failed, results = await test_sql_generation()
        
        # Exit code based on results
        if failed == 0:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Some failures
            
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())
