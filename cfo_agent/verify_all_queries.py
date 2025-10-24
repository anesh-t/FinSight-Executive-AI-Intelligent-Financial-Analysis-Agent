"""
Comprehensive Query Verification Suite
Tests all query types and captures formatted output
"""
import asyncio
import yaml
from graph import CFOAgentGraph
from datetime import datetime

async def verify_all_queries():
    """Run all queries and capture formatted output"""
    
    # Load query catalog
    with open('query_catalog.yaml', 'r') as f:
        catalog = yaml.safe_load(f)
    
    agent = CFOAgentGraph()
    graph = agent.graph
    
    results = {
        "test_run": datetime.now().isoformat(),
        "categories": {},
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0
        }
    }
    
    print("\n" + "="*100)
    print("COMPREHENSIVE QUERY VERIFICATION SUITE")
    print("="*100)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)
    
    for category_name, queries in catalog['categories'].items():
        print(f"\n{'='*100}")
        print(f"CATEGORY: {category_name.upper().replace('_', ' ')}")
        print(f"{'='*100}\n")
        
        category_results = []
        
        for query in queries:
            results["summary"]["total"] += 1
            
            print(f"Query: '{query}'")
            print("-" * 100)
            
            state = {
                "question": query,
                "session_id": f"verify_{category_name}",
                "errors": []
            }
            
            try:
                result = await graph.ainvoke(state)
                response = result.get("final_response", "No response")
                
                # Validation checks
                has_data = "$" in response or "%" in response or any(word in response.lower() 
                                                                      for word in ["revenue", "margin", "income", "price"])
                is_not_generic = "data found" not in response.lower() or "Q" in query or "quarter" in query.lower()
                is_formatted = "\n" in response or "Sources:" in response
                
                is_valid = has_data and is_not_generic
                
                status = "✅ PASS" if is_valid else "❌ FAIL"
                
                print(f"\nStatus: {status}")
                print(f"\nFormatted Response:")
                print("┌" + "─" * 98 + "┐")
                for line in response.split('\n'):
                    print(f"│ {line:<96} │")
                print("└" + "─" * 98 + "┘\n")
                
                if is_valid:
                    results["summary"]["passed"] += 1
                else:
                    results["summary"]["failed"] += 1
                
                category_results.append({
                    "query": query,
                    "status": "PASS" if is_valid else "FAIL",
                    "response": response
                })
                
            except Exception as e:
                print(f"❌ ERROR: {str(e)}\n")
                results["summary"]["failed"] += 1
                category_results.append({
                    "query": query,
                    "status": "ERROR",
                    "error": str(e)
                })
        
        results["categories"][category_name] = category_results
    
    # Print final summary
    print("\n" + "="*100)
    print("FINAL SUMMARY")
    print("="*100)
    total = results["summary"]["total"]
    passed = results["summary"]["passed"]
    failed = results["summary"]["failed"]
    
    print(f"\nTotal Queries Tested: {total}")
    print(f"✅ Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"❌ Failed: {failed} ({failed/total*100:.1f}%)")
    
    # Category breakdown
    print(f"\n{'Category':<40} {'Queries':<10} {'Pass Rate'}")
    print("-" * 100)
    for category, cat_results in results["categories"].items():
        cat_total = len(cat_results)
        cat_passed = sum(1 for r in cat_results if r["status"] == "PASS")
        pass_rate = f"{cat_passed}/{cat_total} ({cat_passed/cat_total*100:.0f}%)"
        print(f"{category.replace('_', ' ').title():<40} {cat_total:<10} {pass_rate}")
    
    print("\n" + "="*100)
    
    if failed == 0:
        print("\n🎉 ALL QUERIES PASSED! System is fully functional!")
    else:
        print(f"\n⚠️  {failed} queries need attention.")
    
    print("="*100)
    
    # Save results to file
    with open('verification_results.yaml', 'w') as f:
        yaml.dump(results, f, default_flow_style=False)
    
    print("\n📁 Detailed results saved to: verification_results.yaml")
    
    return results

if __name__ == "__main__":
    asyncio.run(verify_all_queries())
