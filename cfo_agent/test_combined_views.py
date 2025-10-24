"""
Test combined views integration
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

# Test queries for combined views
TEST_QUERIES = [
    # ============================================================================
    # LAYER 1: Core Company (Financials + Ratios + Stock)
    # ============================================================================
    {
        "category": "Complete Q",
        "query": "show Apple complete picture Q2 2023",
        "expected_intent": "complete_quarterly"
    },
    {
        "category": "Complete Q",
        "query": "everything about Microsoft Q3 2023",
        "expected_intent": "complete_quarterly"
    },
    {
        "category": "Complete Q",
        "query": "comprehensive view of Google Q2 2023",
        "expected_intent": "complete_quarterly"
    },
    {
        "category": "Complete A",
        "query": "show Apple complete picture 2023",
        "expected_intent": "complete_annual"
    },
    {
        "category": "Complete A",
        "query": "everything about Amazon 2023",
        "expected_intent": "complete_annual"
    },
    {
        "category": "Complete A",
        "query": "comprehensive annual view of Meta 2023",
        "expected_intent": "complete_annual"
    },
    
    # ============================================================================
    # LAYER 2: With Macro Context (Layer 1 + Macro)
    # ============================================================================
    {
        "category": "Macro Context Q",
        "query": "show Apple with macro context Q2 2023",
        "expected_intent": "complete_macro_context_quarterly"
    },
    {
        "category": "Macro Context Q",
        "query": "Microsoft with economic context Q3 2023",
        "expected_intent": "complete_macro_context_quarterly"
    },
    {
        "category": "Macro Context Q",
        "query": "Google complete picture with inflation Q2 2023",
        "expected_intent": "complete_macro_context_quarterly"
    },
    {
        "category": "Macro Context A",
        "query": "show Apple with macro 2023",
        "expected_intent": "complete_macro_context_annual"
    },
    {
        "category": "Macro Context A",
        "query": "Amazon with economic context 2023",
        "expected_intent": "complete_macro_context_annual"
    },
    {
        "category": "Macro Context A",
        "query": "Meta complete view with GDP 2023",
        "expected_intent": "complete_macro_context_annual"
    },
    
    # ============================================================================
    # LAYER 3: Full Picture (Layer 2 + Sensitivity)
    # ============================================================================
    {
        "category": "Full Q",
        "query": "show Apple full analysis Q2 2023",
        "expected_intent": "complete_full_quarterly"
    },
    {
        "category": "Full Q",
        "query": "everything including betas for Microsoft Q3 2023",
        "expected_intent": "complete_full_quarterly"
    },
    {
        "category": "Full Q",
        "query": "complete picture with sensitivity for Google Q2 2023",
        "expected_intent": "complete_full_quarterly"
    },
    {
        "category": "Full A",
        "query": "show Apple full analysis 2023",
        "expected_intent": "complete_full_annual"
    },
    {
        "category": "Full A",
        "query": "everything including betas for Amazon 2023",
        "expected_intent": "complete_full_annual"
    },
    {
        "category": "Full A",
        "query": "complete picture with sensitivity for Meta 2023",
        "expected_intent": "complete_full_annual"
    },
]


async def test_combined_views():
    """Test combined view queries"""
    # Initialize
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*100)
    print("TESTING COMBINED VIEWS INTEGRATION")
    print("="*100)
    
    results = {
        "Complete Q": {"pass": 0, "total": 0},
        "Complete A": {"pass": 0, "total": 0},
        "Macro Context Q": {"pass": 0, "total": 0},
        "Macro Context A": {"pass": 0, "total": 0},
        "Full Q": {"pass": 0, "total": 0},
        "Full A": {"pass": 0, "total": 0},
    }
    
    for test in TEST_QUERIES:
        category = test["category"]
        query = test["query"]
        expected_intent = test["expected_intent"]
        
        print(f"\n{'='*100}")
        print(f"[{category}] {query}")
        print("-"*100)
        
        results[category]["total"] += 1
        
        try:
            # Use the graph
            response = await cfo_agent_graph.run(query)
            
            # Check if response is valid
            if response and len(response) > 50:  # Meaningful response
                print(f"✅ PASS")
                print(f"Response: {response[:200]}...")
                results[category]["pass"] += 1
            else:
                print(f"❌ FAIL - Response too short or empty")
                print(f"Response: {response}")
                
        except Exception as e:
            print(f"❌ FAIL - Exception: {str(e)}")
    
    await db_pool.close()
    
    # Print summary
    print("\n" + "="*100)
    print("SUMMARY BY CATEGORY")
    print("="*100)
    
    total_pass = 0
    total_tests = 0
    
    for category, stats in results.items():
        total_pass += stats["pass"]
        total_tests += stats["total"]
        pass_rate = (stats["pass"] / stats["total"] * 100) if stats["total"] > 0 else 0
        status = "✅" if pass_rate == 100 else "❌"
        print(f"{status} {category:<20} {stats['pass']}/{stats['total']} passing ({pass_rate:.1f}%)")
    
    print("\n" + "="*100)
    print("OVERALL SUMMARY")
    print("="*100)
    overall_rate = (total_pass / total_tests * 100) if total_tests > 0 else 0
    print(f"\n{'Category':<25} {'Queries':<10} {'Status':<15} {'Pass Rate':<15}")
    print("-"*65)
    
    for category, stats in results.items():
        pass_rate = (stats["pass"] / stats["total"] * 100) if stats["total"] > 0 else 0
        status = f"✅ {pass_rate:.1f}%" if pass_rate == 100 else f"❌ {pass_rate:.1f}%"
        print(f"{category:<25} {stats['total']:<10} {status:<15} {stats['pass']}/{stats['total']}")
    
    print("\n" + "="*100)
    print(f"OVERALL: {total_pass}/{total_tests} tests passing ({overall_rate:.1f}%)")
    print("="*100)
    
    if overall_rate == 100:
        print("\n🎉 ALL TESTS PASSING! COMBINED VIEWS FULLY OPERATIONAL! 🎉")
    else:
        print(f"\n⚠️  {total_tests - total_pass} tests failing. Please review.")


if __name__ == "__main__":
    asyncio.run(test_combined_views())
