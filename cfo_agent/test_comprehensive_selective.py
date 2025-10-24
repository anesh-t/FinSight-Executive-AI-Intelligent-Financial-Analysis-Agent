"""
Comprehensive test for selective metric display across all financial metrics
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_comprehensive_selective():
    """Test selective display for all types of financial metrics"""
    
    # Initialize
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*80)
    print("COMPREHENSIVE SELECTIVE METRIC DISPLAY TEST")
    print("="*80)
    
    test_cases = [
        # Income statement metrics
        {
            "name": "Test 1: Single metric - Revenue",
            "question": "show apple revenue for 2023",
            "should_contain": ["revenue"],
            "should_not_contain": ["net income", "R&D", "margin"]
        },
        {
            "name": "Test 2: Single metric - Net income",
            "question": "what is apple net income for 2023",
            "should_contain": ["net income"],
            "should_not_contain": ["revenue", "R&D", "COGS"]
        },
        {
            "name": "Test 3: Single metric - Operating income",
            "question": "apple operating income 2023",
            "should_contain": ["operating income"],
            "should_not_contain": ["revenue", "net income", "R&D"]
        },
        {
            "name": "Test 4: Single metric - Gross profit",
            "question": "what is google gross profit for 2023",
            "should_contain": ["gross profit"],
            "should_not_contain": ["revenue", "net income"]
        },
        
        # Expense metrics
        {
            "name": "Test 5: Single expense - R&D",
            "question": "show microsoft R&D expenses for 2023",
            "should_contain": ["R&D"],
            "should_not_contain": ["revenue", "SG&A", "COGS"]
        },
        {
            "name": "Test 6: Single expense - SG&A",
            "question": "apple SG&A for 2023",
            "should_contain": ["SG&A"],
            "should_not_contain": ["revenue", "R&D", "COGS"]
        },
        {
            "name": "Test 7: Single expense - COGS",
            "question": "amazon cost of goods sold 2023",
            "should_contain": ["COGS"],
            "should_not_contain": ["revenue", "R&D", "SG&A"]
        },
        
        # Margin metrics
        {
            "name": "Test 8: Single margin - Gross margin",
            "question": "what is apple gross margin for 2023",
            "should_contain": ["gross margin"],
            "should_not_contain": ["operating margin", "net margin", "revenue"]
        },
        {
            "name": "Test 9: Single margin - Operating margin",
            "question": "microsoft operating margin 2023",
            "should_contain": ["operating margin"],
            "should_not_contain": ["gross margin", "net margin"]
        },
        {
            "name": "Test 10: Single margin - Net margin",
            "question": "google net margin 2023",
            "should_contain": ["net margin"],
            "should_not_contain": ["gross margin", "operating margin"]
        },
        
        # Profitability ratios
        {
            "name": "Test 11: Single ratio - ROE",
            "question": "apple ROE for 2023",
            "should_contain": ["ROE"],
            "should_not_contain": ["revenue", "net income", "margin"]
        },
        {
            "name": "Test 12: Single ratio - ROA",
            "question": "microsoft return on assets 2023",
            "should_contain": ["ROA"],
            "should_not_contain": ["ROE", "revenue"]
        },
        
        # Multiple metrics
        {
            "name": "Test 13: Two metrics - Revenue and net income",
            "question": "apple revenue and net income for 2023",
            "should_contain": ["revenue", "net income"],
            "should_not_contain": ["R&D", "SG&A", "COGS", "margin"]
        },
        {
            "name": "Test 14: Two metrics - R&D and SG&A",
            "question": "show google R&D and SG&A expenses for 2023",
            "should_contain": ["R&D", "SG&A"],
            "should_not_contain": ["revenue", "net income", "COGS"]
        },
        {
            "name": "Test 15: Three metrics - Revenue, net income, and operating income",
            "question": "microsoft revenue, net income, and operating income for 2023",
            "should_contain": ["revenue", "net income", "operating income"],
            "should_not_contain": ["R&D", "SG&A"]
        },
        
        # Generic query - should show all
        {
            "name": "Test 16: Generic query - Show all metrics",
            "question": "show apple financial metrics for 2023",
            "should_contain": ["revenue", "net income", "R&D", "SG&A"],
            "should_not_contain": []
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
                # Show first 150 chars of response
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
    print(f"Pass Rate: {(passed/len(test_cases)*100):.1f}%")
    print("="*80)
    
    await db_pool.close()
    
    return passed, failed


if __name__ == "__main__":
    passed, failed = asyncio.run(test_comprehensive_selective())
    exit(0 if failed == 0 else 1)
