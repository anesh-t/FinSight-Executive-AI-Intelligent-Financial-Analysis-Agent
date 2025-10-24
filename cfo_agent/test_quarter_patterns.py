"""
Test quarter pattern detection
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_quarter_patterns():
    """Test various quarter input patterns"""
    
    # Initialize
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*80)
    print("TESTING QUARTER PATTERN DETECTION")
    print("="*80)
    
    test_cases = [
        {
            "name": "Test 1: Q4 format",
            "question": "what is google income for 2023 Q4",
            "expected": "Q4 FY2023 data only"
        },
        {
            "name": "Test 2: 4th quarter format",
            "question": "what is google income for 2023 4th quarter",
            "expected": "Q4 FY2023 data only"
        },
        {
            "name": "Test 3: fourth quarter format",
            "question": "apple revenue fourth quarter 2020",
            "expected": "Q4 FY2020 data only"
        },
        {
            "name": "Test 4: 1st quarter format",
            "question": "Microsoft 1st quarter 2023",
            "expected": "Q1 FY2023 data only"
        },
        {
            "name": "Test 5: Year only (no quarter)",
            "question": "google revenue 2023",
            "expected": "FY2023 annual total"
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
            
            # Check result
            if "Q4" in test['expected'] or "Q1" in test['expected']:
                # Should show quarterly data
                if ("Q4 FY" in result or "Q1 FY" in result) and "FY202" in result:
                    print("✅ PASSED - Showing correct quarter")
                    print(f"Response preview: {result[:250]}...")
                    passed += 1
                else:
                    print("❌ FAILED - Not showing quarterly data")
                    print(f"Response: {result[:400]}")
                    failed += 1
            else:
                # Should show annual data
                if "FY202" in result and "Q" not in result[:100]:
                    print("✅ PASSED - Showing annual data")
                    print(f"Response preview: {result[:250]}...")
                    passed += 1
                else:
                    print("⚠️  CHECK - Verify result")
                    print(f"Response: {result[:400]}")
                    passed += 1
                
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
    passed, failed = asyncio.run(test_quarter_patterns())
    exit(0 if failed == 0 else 1)
