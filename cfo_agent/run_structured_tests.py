"""
Automated test runner for structured data queries
Tests all 110 structured queries and validates results
"""
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from decomposer import QueryDecomposer
from router import IntentRouter
from planner import TaskPlanner
from sql_exec import SQLExecutor
from formatter import ResponseFormatter
from citations import CitationFetcher
from dotenv import load_dotenv

load_dotenv()


# All 110 structured test queries organized by category
STRUCTURED_QUERIES = {
    "1. Basic Financial Metrics": [
        # Revenue Queries
        "What is Apple's revenue in Q2 2023?",
        "Show Microsoft's revenue for Q1 2023",
        "Get Google's revenue last quarter",
        "What was Amazon's revenue in FY 2023?",
        "Show Meta's revenue Q3 2023",
        
        # Net Income Queries
        "What is Apple's net income Q2 2023?",
        "Show Microsoft's profit for Q1 2023",
        "Get Google's net income FY 2023",
        "What was Amazon's earnings Q2 2023?",
        "Show Meta's net income last quarter",
        
        # Operating Income
        "What is Apple's operating income Q2 2023?",
        "Show Microsoft's EBIT Q1 2023",
        
        # Gross Profit
        "What is Apple's gross profit Q2 2023?",
        "Show Google's gross profit FY 2023",
        
        # Multiple Metrics
        "Show Apple's revenue and net income Q2 2023",
        "Get Microsoft's revenue, net income, and operating income Q1 2023",
        "What are Google's key financials Q3 2023?",
        
        # Balance Sheet
        "What is Apple's total assets Q2 2023?",
        "Show Microsoft's total debt Q1 2023",
        "Get Google's equity Q3 2023",
    ],
    
    "2. Growth Analysis": [
        # QoQ
        "What is Apple's revenue QoQ growth Q2 2023?",
        "Show Microsoft's net income QoQ change Q1 2023",
        "Get Google's revenue quarter over quarter growth Q3 2023",
        "What is Amazon's margin QoQ improvement Q2 2023?",
        "Show Meta's revenue sequential growth Q1 2023",
        
        # YoY
        "What is Apple's revenue YoY growth Q2 2023?",
        "Show Microsoft's net income year over year change Q1 2023",
        "Get Google's revenue YoY Q3 2023",
        "What is Amazon's annual revenue growth FY 2023?",
        "Show Meta's net income year-on-year growth Q2 2023",
        
        # CAGR
        "What is Apple's 3-year revenue CAGR ending 2023?",
        "Calculate Microsoft's 5-year revenue CAGR ending FY 2023",
        "Show Google's revenue CAGR from 2020 to 2023",
        
        # Growth with Values
        "Show Apple's revenue and YoY growth Q2 2023",
        "Get Microsoft's net income with QoQ and YoY growth Q1 2023",
    ],
    
    "3. Peer Comparisons": [
        # Rankings
        "Who led on revenue last quarter?",
        "Who had the highest net margin Q2 2023?",
        "Rank companies by operating margin Q3 2023",
        "Who led on net income FY 2023?",
        "Show revenue leaders Q2 2023",
        
        # Two-Company
        "Compare Apple and Microsoft revenue Q2 2023",
        "Compare Google and Meta net margin Q3 2023",
        "Show Apple vs Amazon revenue Q2 2023",
        "Compare Microsoft and Google operating margin Q1 2023",
        "Apple vs Microsoft: who has better ROE Q2 2023?",
        
        # Multi-Company
        "Compare Apple, Microsoft, and Google revenue Q2 2023",
        "Show margins for all companies Q3 2023",
        "Compare revenue for AAPL, MSFT, AMZN, GOOG Q2 2023",
        
        # Statistics
        "Show Apple's revenue percentile Q2 2023",
        "What is the average revenue across all companies Q2 2023?",
    ],
    
    "4. Macro-Economic": [
        # Company + Single Macro
        "Show Apple's revenue with CPI for Q2 2023",
        "Get Microsoft's performance with GDP context Q1 2023",
        "Show Google's revenue with unemployment rate Q3 2023",
        "What is Amazon's revenue with Fed rate Q2 2023?",
        "Show Meta's margins with CPI Q1 2023",
        
        # Company + Multiple Macro
        "Show Apple's revenue with GDP and CPI Q2 2023",
        "Get Microsoft's performance with CPI, unemployment, and Fed rate Q1 2023",
        "Show Google's financials with macro context Q3 2023",
        
        # Macro Sensitivity
        "What is Apple's net margin beta to CPI?",
        "Show Microsoft's margin sensitivity to inflation",
        "Get Google's operating margin beta to Fed rate",
        "What is Amazon's sensitivity to unemployment?",
        
        # Pure Macro
        "What was GDP in Q2 2023?",
        "Show CPI and unemployment for Q3 2023",
        "What was the Fed rate in Q1 2023?",
    ],
    
    "5. Stock Market": [
        # Prices
        "What is Apple's stock price Q2 2023?",
        "Show Microsoft's closing price Q1 2023",
        "Get Google's opening price Q3 2023",
        "What was Amazon's high price Q2 2023?",
        "Show Meta's low price Q1 2023",
        
        # Returns
        "What is Apple's stock return Q2 2023?",
        "Show Microsoft's price change Q1 2023",
        
        # Stock + Financials
        "Show Apple's revenue and stock price Q2 2023",
        "Get Microsoft's net income and stock return Q1 2023",
        "Compare Google's revenue growth and stock performance Q3 2023",
    ],
    
    "6. Time Series": [
        # Last N Quarters
        "Show Apple's revenue for the last 4 quarters",
        "Get Microsoft's net income over the last 6 quarters",
        "Show Google's margins for the last 8 quarters",
        "What is Amazon's revenue trend last 4 quarters?",
        
        # Last N Years
        "Show Apple's annual revenue for the last 3 years",
        "Get Microsoft's net income over the last 2 years",
        
        # Date Ranges
        "Show Apple's revenue from Q1 2022 to Q4 2023",
        "Get Microsoft's margins for all of 2023",
        "Show Google's quarterly revenue for 2023",
        "What was Amazon's revenue each quarter in 2023?",
    ],
    
    "7. Ratios & Margins": [
        # Margins
        "What is Apple's gross margin Q2 2023?",
        "Show Microsoft's operating margin Q1 2023",
        "Get Google's net margin Q3 2023",
        "Show Amazon's profit margin Q2 2023",
        "What are Meta's margins Q1 2023?",
        
        # Return Ratios
        "What is Apple's ROE Q2 2023?",
        "Show Microsoft's return on equity Q1 2023",
        "Get Google's ROA Q3 2023",
        "What is Amazon's return on assets Q2 2023?",
        
        # Debt Ratios
        "What is Apple's debt-to-equity ratio Q2 2023?",
        "Show Microsoft's debt to equity Q1 2023",
        "Get Google's debt-to-assets ratio Q3 2023",
        
        # Expense Ratios
        "What is Apple's R&D intensity Q2 2023?",
        "Show Microsoft's R&D to revenue ratio Q1 2023",
        "Get Google's SG&A intensity Q3 2023?",
    ],
    
    "8. Edge Cases": [
        # Ambiguous
        "Show Apple's performance Q2 2023",
        "Get Microsoft's metrics Q1 2023",
        "What is Google doing?",
        
        # Invalid Periods
        "Show Apple's revenue Q5 2023",
        "Get Microsoft's data for Q1 2030",
        
        # Invalid Companies
        "What is Tesla's revenue Q2 2023?",
        "Show Netflix's net income Q1 2023",
        
        # Incomplete
        "Apple revenue",
        "Microsoft Q2",
        "Show margins",
    ],
}


async def test_query(query: str, category: str):
    """Test a single query and validate results"""
    
    result = {
        "query": query,
        "category": category,
        "status": "UNKNOWN",
        "sql_executed": False,
        "data_retrieved": False,
        "response_generated": False,
        "citations_present": False,
        "makes_sense": False,
        "error": None,
        "response": None,
        "execution_time": 0,
    }
    
    start_time = time.time()
    
    try:
        # Step 1: Decompose
        decomposer = QueryDecomposer()
        decomposed = await decomposer.decompose(query)
        
        if not decomposed.get('tasks'):
            result["error"] = "No tasks generated from decomposition"
            result["status"] = "FAIL"
            return result
        
        task = decomposed['tasks'][0]
        
        # Step 2: Route
        router = IntentRouter()
        routed = router.route_task(task)
        
        # Step 3: Plan
        planner = TaskPlanner()
        plan = await planner.plan_task(routed)
        
        if not plan.get('sql'):
            result["error"] = "No SQL generated"
            result["status"] = "FAIL"
            return result
        
        result["sql_executed"] = True
        
        # Step 4: Execute SQL
        executor = SQLExecutor()
        results = await executor.execute(plan['sql'], plan['params'])
        
        if results is None or len(results) == 0:
            result["error"] = "No data retrieved from database"
            result["status"] = "FAIL"
            return result
        
        result["data_retrieved"] = True
        
        # Step 5: Fetch Citations
        citation_fetcher = CitationFetcher()
        citations = await citation_fetcher.fetch_citations(results, plan)
        citation_line = citations.get('citation_line', '')
        
        if citation_line:
            result["citations_present"] = True
        
        # Step 6: Format Response
        formatter = ResponseFormatter()
        context = {
            'question': query,
            'intent': plan['intent'],
            'citation_line': citation_line
        }
        response = await formatter.format_response(results, context, {})
        
        if response and len(response) > 10:
            result["response_generated"] = True
            result["response"] = response
            
            # Check if response makes sense
            # Basic validation: has numbers, company names, or meaningful content
            has_numbers = any(char.isdigit() for char in response)
            has_company = any(company in response for company in ['Apple', 'Microsoft', 'Amazon', 'Google', 'Meta', 'AAPL', 'MSFT', 'AMZN', 'GOOG', 'META'])
            has_content = len(response.split()) > 5
            
            if has_numbers or has_company or has_content:
                result["makes_sense"] = True
        
        # Determine overall status
        if result["sql_executed"] and result["data_retrieved"] and result["response_generated"]:
            result["status"] = "PASS"
        else:
            result["status"] = "PARTIAL"
            
    except Exception as e:
        result["error"] = str(e)
        result["status"] = "FAIL"
    
    result["execution_time"] = time.time() - start_time
    
    return result


async def run_all_tests():
    """Run all structured tests"""
    
    print("=" * 80)
    print("🧪 STRUCTURED DATA TEST SUITE")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    all_results = []
    category_stats = {}
    
    total_queries = sum(len(queries) for queries in STRUCTURED_QUERIES.values())
    current_query = 0
    
    for category, queries in STRUCTURED_QUERIES.items():
        print(f"\n{'='*80}")
        print(f"📊 {category}")
        print(f"{'='*80}")
        
        category_results = []
        
        for query in queries:
            current_query += 1
            print(f"\n[{current_query}/{total_queries}] Testing: {query}")
            
            result = await test_query(query, category)
            category_results.append(result)
            all_results.append(result)
            
            # Print result
            status_emoji = "✅" if result["status"] == "PASS" else "⚠️" if result["status"] == "PARTIAL" else "❌"
            print(f"   {status_emoji} Status: {result['status']}")
            print(f"   ⏱️  Time: {result['execution_time']:.2f}s")
            
            if result["status"] == "PASS":
                print(f"   ✓ SQL Executed: {result['sql_executed']}")
                print(f"   ✓ Data Retrieved: {result['data_retrieved']}")
                print(f"   ✓ Response Generated: {result['response_generated']}")
                print(f"   ✓ Citations Present: {result['citations_present']}")
                print(f"   ✓ Makes Sense: {result['makes_sense']}")
                
                # Show snippet of response
                if result["response"]:
                    snippet = result["response"][:150] + "..." if len(result["response"]) > 150 else result["response"]
                    print(f"   📝 Response: {snippet}")
            else:
                print(f"   ❌ Error: {result['error']}")
        
        # Category statistics
        passed = sum(1 for r in category_results if r["status"] == "PASS")
        failed = sum(1 for r in category_results if r["status"] == "FAIL")
        partial = sum(1 for r in category_results if r["status"] == "PARTIAL")
        total = len(category_results)
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        category_stats[category] = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "partial": partial,
            "pass_rate": pass_rate
        }
        
        print(f"\n📊 Category Summary:")
        print(f"   Total: {total}")
        print(f"   Passed: {passed} ({pass_rate:.1f}%)")
        print(f"   Failed: {failed}")
        print(f"   Partial: {partial}")
    
    # Overall statistics
    print(f"\n{'='*80}")
    print("📊 OVERALL RESULTS")
    print(f"{'='*80}")
    
    total_passed = sum(1 for r in all_results if r["status"] == "PASS")
    total_failed = sum(1 for r in all_results if r["status"] == "FAIL")
    total_partial = sum(1 for r in all_results if r["status"] == "PARTIAL")
    overall_pass_rate = (total_passed / total_queries * 100) if total_queries > 0 else 0
    
    print(f"\nTotal Queries: {total_queries}")
    print(f"Passed: {total_passed} ({overall_pass_rate:.1f}%)")
    print(f"Failed: {total_failed}")
    print(f"Partial: {total_partial}")
    
    print(f"\n{'='*80}")
    print("📊 CATEGORY BREAKDOWN")
    print(f"{'='*80}")
    
    for category, stats in category_stats.items():
        print(f"\n{category}:")
        print(f"  Pass Rate: {stats['pass_rate']:.1f}% ({stats['passed']}/{stats['total']})")
    
    # Save results to file
    output_file = Path(__file__).parent / "test_results_structured.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_queries": total_queries,
            "passed": total_passed,
            "failed": total_failed,
            "partial": total_partial,
            "pass_rate": overall_pass_rate,
            "category_stats": category_stats,
            "detailed_results": all_results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    # Generate summary report
    print(f"\n{'='*80}")
    print("📝 SUMMARY REPORT")
    print(f"{'='*80}")
    
    if overall_pass_rate >= 95:
        print("\n🎉 EXCELLENT! Pass rate exceeds target (95%)")
    elif overall_pass_rate >= 90:
        print("\n✅ GOOD! Pass rate is acceptable (90%+)")
    elif overall_pass_rate >= 80:
        print("\n⚠️  NEEDS IMPROVEMENT! Pass rate below target")
    else:
        print("\n❌ CRITICAL! Pass rate significantly below target")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return all_results


if __name__ == "__main__":
    print("\n🚀 Starting Structured Data Test Suite...")
    print("This will test all 110 structured queries")
    print("Estimated time: 10-15 minutes\n")
    
    input("Press Enter to start testing...")
    
    asyncio.run(run_all_tests())
