"""
Test advanced query patterns:
1. Multi-company comparisons with macro
2. Multiple attributes for single company
3. Multiple companies for single attribute
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def test_advanced():
    """Test advanced query patterns"""
    # Initialize
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*100)
    print("TESTING ADVANCED QUERY PATTERNS")
    print("="*100)
    
    tests = [
        # ========================================================================
        # PATTERN 1: Multi-company comparison with macro
        # ========================================================================
        {
            "category": "Multi-Company + Macro",
            "query": "compare Apple with Google and how CPI affected both companies Q2 2023",
            "expected": ["Apple", "Google", "CPI", "inflation"]
        },
        {
            "category": "Multi-Company + Macro",
            "query": "compare Apple and Microsoft and show how GDP impacted them in 2023",
            "expected": ["Apple", "Microsoft", "GDP"]
        },
        {
            "category": "Multi-Company + Macro",
            "query": "show Apple vs Google with inflation Q2 2023",
            "expected": ["Apple", "Google", "inflation"]
        },
        
        # ========================================================================
        # PATTERN 2: Multiple attributes, single company
        # ========================================================================
        {
            "category": "Multiple Attributes",
            "query": "show Apple revenue, net income Q2 2023",
            "expected": ["Apple", "revenue", "net income"]
        },
        {
            "category": "Multiple Attributes",
            "query": "show Microsoft revenue and operating income Q3 2023",
            "expected": ["Microsoft", "revenue", "operating income"]
        },
        {
            "category": "Multiple Attributes",
            "query": "show Google revenue, net income, gross margin Q2 2023",
            "expected": ["Google", "revenue", "net income", "gross margin"]
        },
        {
            "category": "Multiple Attributes",
            "query": "show Amazon revenue, net income, ROE Q3 2023",
            "expected": ["Amazon", "revenue", "net income", "ROE"]
        },
        {
            "category": "Multiple Attributes",
            "query": "show Apple revenue and net income for 2023",
            "expected": ["Apple", "revenue", "net income"]
        },
        
        # ========================================================================
        # PATTERN 3: Multiple companies, single attribute
        # ========================================================================
        {
            "category": "Multiple Companies",
            "query": "show Google and Apple revenue Q2 2023",
            "expected": ["Google", "Apple", "revenue"]
        },
        {
            "category": "Multiple Companies",
            "query": "show Apple and Microsoft net income Q3 2023",
            "expected": ["Apple", "Microsoft", "net income"]
        },
        {
            "category": "Multiple Companies",
            "query": "show Apple, Microsoft, and Google revenue 2023",
            "expected": ["Apple", "Microsoft", "Google", "revenue"]
        },
        {
            "category": "Multiple Companies",
            "query": "compare Apple and Google gross margin Q2 2023",
            "expected": ["Apple", "Google", "gross margin"]
        },
        {
            "category": "Multiple Companies",
            "query": "show revenue for Apple, Microsoft, Google Q2 2023",
            "expected": ["Apple", "Microsoft", "Google", "revenue"]
        },
        
        # ========================================================================
        # PATTERN 4: Complex multi-company + multi-attribute
        # ========================================================================
        {
            "category": "Complex",
            "query": "show Apple and Google revenue and net income Q2 2023",
            "expected": ["Apple", "Google", "revenue", "net income"]
        },
        {
            "category": "Complex",
            "query": "compare Apple vs Microsoft revenue, margin, ROE 2023",
            "expected": ["Apple", "Microsoft", "revenue", "margin", "ROE"]
        },
    ]
    
    results = {
        "Multi-Company + Macro": {"pass": 0, "total": 0, "details": []},
        "Multiple Attributes": {"pass": 0, "total": 0, "details": []},
        "Multiple Companies": {"pass": 0, "total": 0, "details": []},
        "Complex": {"pass": 0, "total": 0, "details": []},
    }
    
    for i, test in enumerate(tests, 1):
        category = test["category"]
        query = test["query"]
        expected = test["expected"]
        
        print(f"\n{'='*100}")
        print(f"[{i}/{len(tests)}] [{category}]")
        print(f"Query: {query}")
        print(f"Expected: {', '.join(expected)}")
        print("-"*100)
        
        results[category]["total"] += 1
        
        try:
            response = await cfo_agent_graph.run(query)
            
            # Check if response contains expected keywords
            response_lower = response.lower()
            found_keywords = [kw for kw in expected if kw.lower() in response_lower]
            
            # Check if response is meaningful
            is_meaningful = len(response) > 50 and not any(word in response_lower for word in ["error", "failed", "no data"])
            
            # Pass if meaningful and has at least half the expected keywords
            passed = is_meaningful and len(found_keywords) >= len(expected) / 2
            
            if passed:
                status = "✅ PASS"
                results[category]["pass"] += 1
            else:
                status = "❌ FAIL"
            
            print(f"{status}")
            print(f"Response: {response[:250]}...")
            print(f"Keywords Found: {len(found_keywords)}/{len(expected)} - {found_keywords}")
            
            results[category]["details"].append({
                "query": query,
                "passed": passed,
                "response": response[:150],
                "keywords_found": len(found_keywords),
                "keywords_total": len(expected)
            })
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results[category]["details"].append({
                "query": query,
                "passed": False,
                "error": str(e)[:100]
            })
    
    await db_pool.close()
    
    # Summary
    print("\n" + "="*100)
    print("SUMMARY BY PATTERN")
    print("="*100)
    
    total_pass = 0
    total_tests = 0
    
    for category, stats in results.items():
        total_pass += stats["pass"]
        total_tests += stats["total"]
        pass_rate = (stats["pass"] / stats["total"] * 100) if stats["total"] > 0 else 0
        status = "✅" if pass_rate >= 70 else "⚠️" if pass_rate >= 40 else "❌"
        
        print(f"\n{status} {category}")
        print(f"   Pass Rate: {stats['pass']}/{stats['total']} ({pass_rate:.1f}%)")
        
        # Show failed queries
        failed = [d for d in stats["details"] if not d["passed"]]
        if failed:
            print(f"   Failed Queries:")
            for f in failed:
                print(f"     - {f['query'][:70]}...")
    
    # Overall
    print("\n" + "="*100)
    print("OVERALL SUMMARY")
    print("="*100)
    
    overall_rate = (total_pass / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{'Pattern':<30} {'Tests':<10} {'Passed':<10} {'Pass Rate':<15} {'Status'}")
    print("-"*75)
    
    for category, stats in results.items():
        pass_rate = (stats["pass"] / stats["total"] * 100) if stats["total"] > 0 else 0
        status_icon = "✅" if pass_rate >= 70 else "⚠️" if pass_rate >= 40 else "❌"
        print(f"{category:<30} {stats['total']:<10} {stats['pass']:<10} {pass_rate:>6.1f}%        {status_icon}")
    
    print("-"*75)
    print(f"{'TOTAL':<30} {total_tests:<10} {total_pass:<10} {overall_rate:>6.1f}%")
    
    print("\n" + "="*100)
    if overall_rate >= 70:
        print("✅ GOOD! Advanced patterns are working well.")
    elif overall_rate >= 40:
        print("⚠️  PARTIAL! Some patterns need enhancement.")
    else:
        print("❌ NEEDS WORK! Advanced patterns require implementation.")
    print("="*100)
    
    return results


if __name__ == "__main__":
    asyncio.run(test_advanced())
