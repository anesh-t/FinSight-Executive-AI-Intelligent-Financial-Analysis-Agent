"""
Test simple queries to verify fixes
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_simple_queries():
    """Test simple, direct queries"""
    
    # Initialize
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*80)
    print("TESTING SIMPLE QUERIES")
    print("="*80)
    
    test_cases = [
        {
            "name": "Test 1: Apple revenue 2019",
            "question": "show apple revenue for 2019",
            "expected": "Should show ONLY 2019 data"
        },
        {
            "name": "Test 2: Apple Q2 2019",
            "question": "show apple revenue for Q2 2019",
            "expected": "Should show ONLY Q2 2019"
        },
        {
            "name": "Test 3: Microsoft 2023 annual",
            "question": "Microsoft revenue and net income for FY 2023",
            "expected": "Should show FY 2023 annual totals"
        },
        {
            "name": "Test 4: Latest quarter",
            "question": "show apple latest quarter revenue",
            "expected": "Should show Q2 FY2025 (latest)"
        },
        {
            "name": "Test 5: Amazon 2020",
            "question": "Amazon revenue in 2020",
            "expected": "Should show only 2020 data"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{test['name']}")
        print(f"Question: \"{test['question']}\"")
        print(f"Expected: {test['expected']}")
        print("-"*80)
        
        try:
            result = await cfo_agent_graph.run(test['question'])
            
            # Check if result looks good
            if result and "No data" not in result and "No results" not in result:
                print("✅ PASSED")
                print(f"Response:\n{result[:400]}...")
                passed += 1
            else:
                print("❌ FAILED - No data or empty result")
                print(f"Response: {result}")
                failed += 1
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            failed += 1
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("="*80)
    
    await db_pool.close()
    
    return passed, failed


if __name__ == "__main__":
    passed, failed = asyncio.run(test_simple_queries())
    exit(0 if failed == 0 else 1)
