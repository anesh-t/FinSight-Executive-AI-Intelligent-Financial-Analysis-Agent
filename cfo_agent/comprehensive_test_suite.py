"""
Comprehensive Test Suite for CFO Agent
Tests all query capabilities and verifies correct responses
"""
import asyncio
import json
from datetime import datetime
from graph import CFOAgentGraph

# Test queries organized by category
TEST_QUERIES = {
    "1. BASIC FINANCIALS - Single Company": [
        "What was Apple's revenue in 2023?",
        "Show Microsoft net income for 2023",
        "Google operating income 2023",
        "Amazon gross profit in 2023"
    ],
    
    "2. BASIC FINANCIALS - Multiple Metrics": [
        "Show Apple revenue and net income for 2023",
        "What was Microsoft's revenue, net income, and operating income in 2023?"
    ],
    
    "3. BASIC FINANCIALS - Multi-Company": [
        "Compare revenue for Apple and Microsoft in 2023",
        "Show net income for Apple, Microsoft, and Google 2023"
    ],
    
    "4. FINANCIAL RATIOS - Single Company": [
        "What is Apple's gross margin for 2023?",
        "Show Microsoft's ROE in 2023",
        "Google operating margin 2023",
        "Amazon net margin 2023"
    ],
    
    "5. FINANCIAL RATIOS - Multiple Ratios": [
        "Show Apple's gross margin, operating margin, and net margin for 2023",
        "What were Microsoft's ROE and ROA in 2023?"
    ],
    
    "6. FINANCIAL RATIOS - Multi-Company": [
        "Compare gross margin for Apple and Microsoft 2023",
        "Show net margin for Apple, Microsoft, Google 2023"
    ],
    
    "7. STOCK PRICES - Single Price Type": [
        "What was Apple's opening price in 2023?",
        "Show Microsoft closing price for 2023",
        "Google high price 2023",
        "Amazon low price 2023"
    ],
    
    "8. STOCK PRICES - Multiple Price Types": [
        "Show Apple opening and closing price for 2023",
        "What were Microsoft's high and low prices in 2023?"
    ],
    
    "9. STOCK PRICES - Multi-Company": [
        "Show closing price for Apple and Microsoft 2023",
        "Compare opening price for Apple, Microsoft, Google 2023"
    ],
    
    "10. STOCK PRICES - Average vs Actual": [
        "Show Apple closing price for 2023",
        "Show Apple average closing price for 2023",
        "Microsoft opening price 2023",
        "Microsoft average opening price 2023"
    ],
    
    "11. COMBINED QUERIES - Financials + Ratios + Stock": [
        "Show Apple revenue, net margin, and closing stock price for 2023",
        "What were Microsoft's revenue, ROE, and stock return in 2023?"
    ],
    
    "12. QUARTERLY DATA": [
        "What was Apple's revenue in Q4 2023?",
        "Show Microsoft net income for Q3 2023",
        "Apple closing stock price Q2 2023"
    ],
    
    "13. MACRO INDICATORS": [
        "What was GDP in 2023?",
        "Show CPI for 2023",
        "Unemployment rate in 2023",
        "Fed funds rate 2023"
    ],
    
    "14. MACRO WITH FINANCIALS": [
        "How did Apple perform in 2023 with GDP context?",
        "Compare Apple and Microsoft with macro indicators in 2023"
    ]
}

async def run_comprehensive_tests():
    """Run all test queries and capture responses"""
    
    # Initialize agent
    agent = CFOAgentGraph()
    graph = agent.graph
    
    # Results storage
    results = {
        "test_run": datetime.now().isoformat(),
        "total_queries": 0,
        "passed": 0,
        "failed": 0,
        "results": {}
    }
    
    print("="*80)
    print("CFO AGENT COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run tests by category
    for category, queries in TEST_QUERIES.items():
        print(f"\n{'='*80}")
        print(f"CATEGORY: {category}")
        print(f"{'='*80}\n")
        
        category_results = []
        
        for i, query in enumerate(queries, 1):
            results["total_queries"] += 1
            
            print(f"\nTest {i}/{len(queries)}: {query}")
            print("-" * 80)
            
            try:
                # Run query through agent
                state = {
                    "question": query,
                    "session_id": "test_session",
                    "errors": []
                }
                
                final_state = await graph.ainvoke(state)
                response = final_state.get("final_response", "No response")
                
                # Check if response is valid (not empty, not just "No data")
                is_valid = (
                    response and 
                    len(response) > 20 and 
                    "No data found" not in response and
                    "error" not in response.lower()
                )
                
                if is_valid:
                    results["passed"] += 1
                    status = "✅ PASSED"
                else:
                    results["failed"] += 1
                    status = "❌ FAILED"
                
                print(f"Status: {status}")
                print(f"\nResponse:\n{response}\n")
                
                # Store result
                category_results.append({
                    "query": query,
                    "status": "PASSED" if is_valid else "FAILED",
                    "response": response,
                    "sql_executed": final_state.get("sql_executed", []),
                    "errors": final_state.get("errors", [])
                })
                
            except Exception as e:
                results["failed"] += 1
                error_msg = str(e)
                print(f"Status: ❌ FAILED")
                print(f"Error: {error_msg}\n")
                
                category_results.append({
                    "query": query,
                    "status": "FAILED",
                    "response": None,
                    "error": error_msg
                })
        
        results["results"][category] = category_results
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Queries: {results['total_queries']}")
    print(f"Passed: {results['passed']} ({results['passed']/results['total_queries']*100:.1f}%)")
    print(f"Failed: {results['failed']} ({results['failed']/results['total_queries']*100:.1f}%)")
    print("="*80)
    
    # Save results to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"test_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    # Generate human-readable report
    report_file = f"test_report_{timestamp}.txt"
    with open(report_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("CFO AGENT COMPREHENSIVE TEST REPORT\n")
        f.write("="*80 + "\n")
        f.write(f"Test Run: {results['test_run']}\n")
        f.write(f"Total Queries: {results['total_queries']}\n")
        f.write(f"Passed: {results['passed']} ({results['passed']/results['total_queries']*100:.1f}%)\n")
        f.write(f"Failed: {results['failed']} ({results['failed']/results['total_queries']*100:.1f}%)\n")
        f.write("="*80 + "\n\n")
        
        for category, category_results in results["results"].items():
            f.write(f"\n{'='*80}\n")
            f.write(f"CATEGORY: {category}\n")
            f.write(f"{'='*80}\n\n")
            
            for i, result in enumerate(category_results, 1):
                f.write(f"\nQuery {i}: {result['query']}\n")
                f.write(f"Status: {result['status']}\n")
                f.write("-" * 80 + "\n")
                f.write(f"Response:\n{result.get('response', 'No response')}\n")
                f.write("-" * 80 + "\n\n")
    
    print(f"Human-readable report saved to: {report_file}")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())
