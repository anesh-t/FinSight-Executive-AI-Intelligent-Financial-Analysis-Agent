"""
Test expense queries
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_expense_queries():
    """Test R&D and expense queries"""
    
    # Initialize
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*80)
    print("TESTING EXPENSE QUERIES")
    print("="*80)
    
    test_cases = [
        {
            "name": "Test 1: R&D expenses for year",
            "question": "show r and d expenses for apple in 2023",
            "expected": "R&D annual total ~$29.9B"
        },
        {
            "name": "Test 2: R&D with abbreviation",
            "question": "apple R&D 2023",
            "expected": "R&D annual total ~$29.9B"
        },
        {
            "name": "Test 3: SG&A expenses",
            "question": "show apple SG&A expenses for 2023",
            "expected": "SG&A annual total ~$25.1B"
        },
        {
            "name": "Test 4: Quarterly R&D",
            "question": "google R&D expenses Q2 2023",
            "expected": "Q2 FY2023 R&D data"
        },
        {
            "name": "Test 5: Research and development spelled out",
            "question": "microsoft research and development expenses 2023",
            "expected": "R&D annual total"
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
            
            # Check if result contains expense data
            if "R&D" in result or "SG&A" in result or "expenses" in result:
                print("✅ PASSED - Contains expense data")
                print(f"Response: {result[:400]}...")
                passed += 1
            else:
                print("❌ FAILED - No expense data found")
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
    passed, failed = asyncio.run(test_expense_queries())
    exit(0 if failed == 0 else 1)
