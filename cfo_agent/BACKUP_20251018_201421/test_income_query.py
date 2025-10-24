"""
Test that "income" alone means net income
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_income_query():
    """Test that 'income' defaults to net income only"""
    
    # Initialize
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*80)
    print("TESTING 'INCOME' KEYWORD")
    print("="*80)
    
    test_cases = [
        {
            "name": "Test 1: Generic 'income' (should be net income only)",
            "question": "show apple income for 2023",
            "should_contain": ["net income"],
            "should_not_contain": ["revenue", "operating income", "gross profit", "R&D", "SG&A", "margin"]
        },
        {
            "name": "Test 2: 'net income' (explicit)",
            "question": "show apple net income for 2023",
            "should_contain": ["net income"],
            "should_not_contain": ["revenue", "operating income", "R&D"]
        },
        {
            "name": "Test 3: 'operating income' (specific)",
            "question": "show apple operating income for 2023",
            "should_contain": ["operating income"],
            "should_not_contain": ["net income", "revenue", "R&D"]
        },
        {
            "name": "Test 4: Generic 'profit' (should be net income)",
            "question": "what is apple profit for 2023",
            "should_contain": ["net income"],
            "should_not_contain": ["revenue", "operating income", "R&D"]
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        print(f"\n{test['name']}")
        print(f"Question: \"{test['question']}\"")
        print("-"*80)
        
        try:
            result = await cfo_agent_graph.run(test['question'])
            
            # Check if expected metrics are shown
            all_shown = all(metric in result for metric in test['should_contain'])
            none_hidden = not any(metric in result for metric in test['should_not_contain'])
            
            if all_shown and none_hidden:
                print("✅ PASSED")
                print(f"Response: {result[:150]}...")
                passed += 1
            else:
                print("❌ FAILED")
                if not all_shown:
                    missing = [m for m in test['should_contain'] if m not in result]
                    print(f"  Missing: {missing}")
                if not none_hidden:
                    unexpected = [m for m in test['should_not_contain'] if m in result]
                    print(f"  Unexpected: {unexpected}")
                print(f"Full response: {result[:400]}")
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
    passed, failed = asyncio.run(test_income_query())
    exit(0 if failed == 0 else 1)
