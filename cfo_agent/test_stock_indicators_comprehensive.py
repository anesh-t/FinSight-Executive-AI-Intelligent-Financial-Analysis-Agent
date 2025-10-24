"""Comprehensive test for all stock indicators in quarterly and annual queries"""
import asyncio
from graph import CFOAgentGraph

async def test_all_stock_indicators():
    agent = CFOAgentGraph()
    graph = agent.graph
    
    print("="*80)
    print("COMPREHENSIVE STOCK INDICATORS TEST")
    print("="*80)
    
    test_cases = [
        # Quarterly stock indicators
        {
            "category": "QUARTERLY STOCK INDICATORS",
            "queries": [
                "Apple opening stock price Q2 2023",
                "Apple closing stock price Q2 2023",
                "Apple high stock price Q2 2023",
                "Apple low stock price Q2 2023",
                "Apple opening and closing price Q2 2023",
                "Apple high and low price Q2 2023"
            ]
        },
        # Annual stock indicators
        {
            "category": "ANNUAL STOCK INDICATORS",
            "queries": [
                "Apple opening stock price 2023",
                "Apple closing stock price 2023",
                "Apple high stock price 2023",
                "Apple low stock price 2023",
                "Apple opening and closing price 2023",
                "Apple high and low price 2023"
            ]
        },
        # Combined queries (financials + stock)
        {
            "category": "COMBINED QUERIES - Financials + Stock",
            "queries": [
                "Show Apple revenue and closing stock price for 2023",
                "Show Apple revenue, net margin, and closing stock price for 2023",
                "Apple net income and opening price 2023",
                "Apple gross margin and high price 2023",
                "Show Microsoft revenue, ROE, and closing price 2023"
            ]
        },
        # Combined quarterly queries
        {
            "category": "COMBINED QUARTERLY QUERIES",
            "queries": [
                "Show Apple revenue and closing stock price Q2 2023",
                "Apple net income and opening price Q3 2023"
            ]
        }
    ]
    
    results_summary = {"passed": 0, "failed": 0, "details": []}
    
    for test_group in test_cases:
        print(f"\n{'='*80}")
        print(f"{test_group['category']}")
        print(f"{'='*80}\n")
        
        for query in test_group["queries"]:
            print(f"Query: '{query}'")
            print("-"*80)
            
            state = {
                "question": query,
                "session_id": "test_session",
                "errors": []
            }
            
            try:
                result = await graph.ainvoke(state)
                response = result.get("final_response", "No response")
                
                # Check if response is valid
                has_price = "$" in response and any(word in response.lower() for word in ["price", "opening", "closing", "high", "low"])
                is_not_generic = "data found" not in response.lower()
                
                # For combined queries, check multiple metrics
                if "revenue" in query.lower() or "margin" in query.lower() or "income" in query.lower():
                    has_financial = any(word in response.lower() for word in ["revenue", "margin", "income", "roe"])
                    is_valid = has_price and has_financial and is_not_generic
                else:
                    is_valid = has_price and is_not_generic
                
                if is_valid:
                    print(f"✅ PASSED")
                    results_summary["passed"] += 1
                else:
                    print(f"❌ FAILED")
                    results_summary["failed"] += 1
                
                print(f"\nResponse:\n{response}\n")
                
                results_summary["details"].append({
                    "query": query,
                    "status": "PASSED" if is_valid else "FAILED",
                    "response": response
                })
                
            except Exception as e:
                print(f"❌ ERROR: {str(e)}\n")
                results_summary["failed"] += 1
                results_summary["details"].append({
                    "query": query,
                    "status": "ERROR",
                    "error": str(e)
                })
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    total = results_summary["passed"] + results_summary["failed"]
    print(f"Total Tests: {total}")
    print(f"Passed: {results_summary['passed']} ({results_summary['passed']/total*100:.1f}%)")
    print(f"Failed: {results_summary['failed']} ({results_summary['failed']/total*100:.1f}%)")
    print("="*80)
    
    # Show failed queries
    if results_summary["failed"] > 0:
        print("\n❌ FAILED QUERIES:")
        for detail in results_summary["details"]:
            if detail["status"] != "PASSED":
                print(f"  - {detail['query']}")
    else:
        print("\n✅ ALL TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(test_all_stock_indicators())
