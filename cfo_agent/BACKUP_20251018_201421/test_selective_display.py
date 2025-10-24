"""
Test selective metric display based on user question
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_selective_display():
    """Test that only requested metrics are displayed"""
    
    # Initialize
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*80)
    print("TESTING SELECTIVE METRIC DISPLAY")
    print("="*80)
    
    test_cases = [
        {
            "name": "Test 1: Only revenue requested",
            "question": "show apple revenue for 2023",
            "should_show": ["revenue"],
            "should_not_show": ["net income", "R&D", "SG&A", "COGS", "ROE"]
        },
        {
            "name": "Test 2: Only R&D requested",
            "question": "show apple R&D expenses for 2023",
            "should_show": ["R&D"],
            "should_not_show": ["revenue", "net income", "SG&A", "COGS"]
        },
        {
            "name": "Test 3: Revenue and net income requested",
            "question": "show apple revenue and net income for 2023",
            "should_show": ["revenue", "net income"],
            "should_not_show": ["R&D", "SG&A", "COGS"]
        },
        {
            "name": "Test 4: Only SG&A requested",
            "question": "apple SG&A expenses 2023",
            "should_show": ["SG&A"],
            "should_not_show": ["revenue", "net income", "R&D", "COGS"]
        },
        {
            "name": "Test 5: Generic query - show all",
            "question": "show apple financial metrics for 2023",
            "should_show": ["revenue", "net income", "R&D", "SG&A"],
            "should_not_show": []
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{test['name']}")
        print(f"Question: \"{test['question']}\"")
        print(f"Should show: {test['should_show']}")
        print(f"Should NOT show: {test['should_not_show']}")
        print("-"*80)
        
        try:
            result = await cfo_agent_graph.run(test['question'])
            
            # Check if expected metrics are shown
            all_shown = all(metric in result for metric in test['should_show'])
            none_hidden = not any(metric in result for metric in test['should_not_show'])
            
            if all_shown and none_hidden:
                print("✅ PASSED")
                print(f"Response: {result[:300]}...")
                passed += 1
            else:
                print("❌ FAILED")
                if not all_shown:
                    missing = [m for m in test['should_show'] if m not in result]
                    print(f"  Missing expected metrics: {missing}")
                if not none_hidden:
                    unexpected = [m for m in test['should_not_show'] if m in result]
                    print(f"  Showing unexpected metrics: {unexpected}")
                print(f"Response: {result[:400]}")
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
    passed, failed = asyncio.run(test_selective_display())
    exit(0 if failed == 0 else 1)
