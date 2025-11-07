"""
Comprehensive Test Runner for CFO Agent
Tests all 445 questions in batches and validates:
1. SQL should source out the data
2. Sourced data should be shown in chat
3. Answer should make sense
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from decomposer import QueryDecomposer
from router import IntentRouter
from planner import TaskPlanner
from sql_exec import SQLExecutor
from formatter import ResponseFormatter
from citations import CitationFetcher
from dotenv import load_dotenv

load_dotenv()

# All 445 test questions organized by category
TEST_QUESTIONS = {
    "Category 1: Basic Financial Metrics (20)": [
        "What was Apple's revenue in Q2 2023?",
        "Show Microsoft's revenue for 2023",
        "Get Google's total revenue Q3 2023",
        "What is Amazon's quarterly revenue Q1 2023?",
        "Show Meta's annual revenue for FY2023",
        "What was Apple's net income Q2 2023?",
        "Show Microsoft's profit for 2023",
        "Get Google's net income in Q3 2023",
        "What is Amazon's earnings Q1 2023?",
        "Show Meta's bottom line for 2023",
        "What was Apple's operating income Q2 2023?",
        "Show Microsoft's EBIT for 2023",
        "Get Google's operating profit Q3 2023",
        "What was Apple's gross profit Q2 2023?",
        "Show Microsoft's gross income for 2023",
        "Show Apple's revenue and net income Q2 2023",
        "Get Microsoft's revenue, operating income, and net income for 2023",
        "What are Google's revenue, gross profit, and net income Q3 2023?",
        "Show Amazon's complete financials Q1 2023",
        "Get Meta's revenue, profit, and margins Q4 2023",
    ],
    
    "Category 2: Margins & Profitability (15)": [
        "What is Apple's gross margin Q2 2023?",
        "Show Microsoft's gross profit margin for 2023",
        "Get Google's gross margin Q3 2023",
        "What is Apple's operating margin Q2 2023?",
        "Show Microsoft's EBIT margin for 2023",
        "Get Google's operating profit margin Q3 2023",
        "What is Apple's net margin Q2 2023?",
        "Show Microsoft's profit margin for 2023",
        "Get Google's net profit margin Q3 2023",
        "Show Apple's margins Q2 2023",
        "Get Microsoft's gross, operating, and net margins for 2023",
        "What are Google's profitability margins Q3 2023?",
        "Show Apple's margin trends for last 4 quarters",
        "Get Microsoft's margin evolution over 2023",
        "What is Google's margin performance for last 3 years?",
    ],
    
    "Category 3: Balance Sheet (15)": [
        "What are Apple's total assets Q2 2023?",
        "Show Microsoft's assets for 2023",
        "Get Google's total assets Q3 2023",
        "What are Apple's total liabilities Q2 2023?",
        "Show Microsoft's liabilities for 2023",
        "Get Google's total liabilities Q3 2023",
        "What is Apple's equity Q2 2023?",
        "Show Microsoft's shareholder equity for 2023",
        "Get Google's total equity Q3 2023",
        "What is Apple's total debt Q2 2023?",
        "Show Microsoft's debt for 2023",
        "Get Google's debt levels Q3 2023",
        "Show Apple's balance sheet Q2 2023",
        "Get Microsoft's assets, liabilities, and equity for 2023",
        "What is Google's financial position Q3 2023?",
    ],
    
    "Category 4: Financial Ratios (20)": [
        "What is Apple's ROE Q2 2023?",
        "Show Microsoft's return on equity for 2023",
        "Get Google's ROA Q3 2023",
        "What is Amazon's return on assets Q1 2023?",
        "What is Apple's debt-to-equity ratio Q2 2023?",
        "Show Microsoft's debt to equity for 2023",
        "Get Google's debt-to-assets ratio Q3 2023",
        "What is Amazon's leverage Q1 2023?",
        "What is Apple's current ratio Q2 2023?",
        "Show Microsoft's quick ratio for 2023",
        "Get Google's liquidity ratios Q3 2023",
        "What is Apple's asset turnover Q2 2023?",
        "Show Microsoft's efficiency ratios for 2023",
        "Show Apple's key ratios Q2 2023",
        "Get Microsoft's financial ratios for 2023",
        "What are Google's performance ratios Q3 2023?",
        "Show Amazon's ROE, ROA, and debt ratios Q1 2023",
        "Get Meta's profitability and leverage ratios Q4 2023",
        "What are Apple's return and debt ratios for 2023?",
        "Show Microsoft's complete ratio analysis Q2 2023",
    ],
    
    "Category 5: Cash Flow (15)": [
        "What is Apple's operating cash flow Q2 2023?",
        "Show Microsoft's cash from operations for 2023",
        "Get Google's OCF Q3 2023",
        "What is Apple's investing cash flow Q2 2023?",
        "Show Microsoft's cash flow from investing for 2023",
        "Get Google's investing activities Q3 2023",
        "What is Apple's financing cash flow Q2 2023?",
        "Show Microsoft's cash flow from financing for 2023",
        "Get Google's financing activities Q3 2023",
        "What is Apple's free cash flow Q2 2023?",
        "Show Microsoft's FCF for 2023",
        "Get Google's free cash flow Q3 2023",
        "Show Apple's cash flow statement Q2 2023",
        "Get Microsoft's complete cash flows for 2023",
        "What are Google's operating, investing, and financing cash flows Q3 2023?",
    ],
    
    "Category 6: R&D and Expenses (15)": [
        "What is Apple's R&D spending Q2 2023?",
        "Show Microsoft's research and development for 2023",
        "Get Google's R&D expenses Q3 2023",
        "What is Apple's SG&A Q2 2023?",
        "Show Microsoft's selling and administrative expenses for 2023",
        "Get Google's SG&A Q3 2023",
        "What is Apple's cost of goods sold Q2 2023?",
        "Show Microsoft's COGS for 2023",
        "Get Google's cost of revenue Q3 2023",
        "What is Apple's R&D intensity Q2 2023?",
        "Show Microsoft's R&D to revenue ratio for 2023",
        "Get Google's SG&A intensity Q3 2023",
        "What is Amazon's R&D and SG&A intensity Q1 2023?",
        "Show Apple's expense breakdown Q2 2023",
        "Get Microsoft's R&D, SG&A, and COGS for 2023",
    ],
    
    "Category 7: Stock Market Data (20)": [
        "What was Apple's stock price Q2 2023?",
        "Show Microsoft's share price Q1 2023",
        "Get Google's stock price Q3 2023",
        "What was Amazon's trading price Q4 2023?",
        "Show Meta's stock price Q2 2023",
        "What was Apple's stock price in 2023?",
        "Show Microsoft's share price for 2023",
        "Get Google's stock price for FY2023",
        "What was Apple's closing price Q2 2023?",
        "Show Microsoft's opening price Q1 2023",
        "Get Google's high and low prices Q3 2023",
        "What was Amazon's average price Q4 2023?",
        "What was Apple's stock return Q2 2023?",
        "Show Microsoft's stock performance Q1 2023",
        "Get Google's return Q3 2023",
        "What was Amazon's stock return for 2023?",
        "Show Apple's revenue and stock price Q2 2023",
        "Get Microsoft's net income and stock return Q1 2023",
        "What are Google's financials and stock performance Q3 2023?",
        "Show Amazon's revenue, profit, and stock price Q4 2023",
    ],
}

# Add more categories (continuing from where we left off)
TEST_QUESTIONS_PART2 = {
    "Category 8A: Pure Macro - Quarterly (10)": [
        "What was GDP in Q2 2023?",
        "Show CPI for Q3 2023",
        "What was the unemployment rate in Q1 2023?",
        "Show Fed rate Q4 2023",
        "What was S&P 500 in Q2 2023?",
        "Show GDP and CPI for Q3 2023",
        "Get unemployment and Fed rate Q1 2023",
        "What were all macro indicators Q2 2023?",
        "Show economic indicators Q3 2023",
        "Get macro context for Q4 2023",
    ],
    
    "Category 8B: Pure Macro - Annual (10)": [
        "What was GDP in 2023?",
        "Show CPI for 2023",
        "What was the unemployment rate in 2023?",
        "Show Fed rate for 2023",
        "What was S&P 500 performance in 2023?",
        "Show GDP and CPI for 2023",
        "Get unemployment and Fed rate for 2023",
        "What were all macro indicators in 2023?",
        "Show economic indicators for 2023",
        "Get macro context for 2023",
    ],
    
    "Category 8C: Revenue + Macro - Quarterly (10)": [
        "Show Apple's revenue with CPI for Q2 2023",
        "Get Microsoft's revenue with GDP Q1 2023",
        "Show Google's revenue with unemployment Q3 2023",
        "What is Amazon's revenue with Fed rate Q4 2023?",
        "Show Meta's revenue with S&P 500 Q2 2023",
        "Get Apple's revenue with GDP and CPI Q2 2023",
        "Show Microsoft's revenue with all macro indicators Q1 2023",
        "What is Google's revenue with economic context Q3 2023?",
        "Show Amazon's revenue with CPI, GDP, unemployment Q4 2023",
        "Get Meta's revenue with macro indicators Q2 2023",
    ],
    
    "Category 8D: Revenue + Macro - Annual (10)": [
        "Show Apple's revenue with CPI for 2023",
        "Get Microsoft's revenue with GDP for 2023",
        "Show Google's revenue with unemployment for 2023",
        "What is Amazon's revenue with Fed rate for 2023?",
        "Show Meta's revenue with S&P 500 for 2023",
        "Get Apple's revenue with GDP and CPI for 2023",
        "Show Microsoft's revenue with all macro indicators for 2023",
        "What is Google's revenue with economic context for 2023?",
        "Show Amazon's revenue with CPI, GDP, unemployment for 2023",
        "Get Meta's revenue with macro indicators for 2023",
    ],
    
    "Category 8E: Stock + Macro - Quarterly (10)": [
        "Show Apple's stock price with CPI Q2 2023",
        "Get Microsoft's stock price with GDP Q1 2023",
        "Show Google's stock price with unemployment Q3 2023",
        "What is Amazon's stock price with Fed rate Q4 2023?",
        "Show Meta's stock price with S&P 500 Q2 2023",
        "Get Apple's stock price with GDP and CPI Q2 2023",
        "Show Microsoft's stock price with all macro indicators Q1 2023",
        "What is Google's stock price with economic context Q3 2023?",
        "Show Amazon's stock price with macro indicators Q4 2023",
        "Get Meta's stock price with CPI, unemployment, Fed rate Q2 2023",
    ],
}

# Metric Combinations
TEST_QUESTIONS_PART3 = {
    "Category 13A: Financials + Ratios - Quarterly (10)": [
        "Show Apple's revenue and ROE Q2 2023",
        "Get Microsoft's net income and ROA Q1 2023",
        "Show Google's revenue and debt-to-equity Q3 2023",
        "What is Amazon's net income and margins Q4 2023",
        "Show Meta's revenue, net income, and ROE Q2 2023",
        "Get Apple's gross profit and operating margin Q1 2023",
        "Show Microsoft's revenue and net margin Q2 2023",
        "What is Google's operating income and ROA Q3 2023?",
        "Show Amazon's revenue, margins, and debt ratios Q4 2023",
        "Get Meta's complete financials and ratios Q2 2023",
    ],
    
    "Category 13B: Financials + Stock - Quarterly (10)": [
        "Show Apple's revenue and stock price Q2 2023",
        "Get Microsoft's net income and stock price Q1 2023",
        "Show Google's revenue and stock return Q3 2023",
        "What is Amazon's net income and stock performance Q4 2023?",
        "Show Meta's revenue, net income, and stock price Q2 2023",
        "Get Apple's margins and stock price Q1 2023",
        "Show Microsoft's operating income and stock return Q2 2023",
        "What is Google's gross profit and stock price Q3 2023?",
        "Show Amazon's complete financials and stock data Q4 2023",
        "Get Meta's revenue, margins, and stock performance Q2 2023",
    ],
    
    "Category 13C: Stock + Ratios - Quarterly (10)": [
        "Show Apple's stock price and ROE Q2 2023",
        "Get Microsoft's stock price and ROA Q1 2023",
        "Show Google's stock return and margins Q3 2023",
        "What is Amazon's stock price and debt-to-equity Q4 2023?",
        "Show Meta's stock performance and ROE Q2 2023",
        "Get Apple's stock price and net margin Q1 2023",
        "Show Microsoft's stock return and operating margin Q2 2023",
        "What is Google's stock price and debt ratios Q3 2023?",
        "Show Amazon's stock performance and profitability ratios Q4 2023",
        "Get Meta's stock price, ROE, and margins Q2 2023",
    ],
    
    "Category 13D: Financials + Ratios + Stock - Quarterly (5)": [
        "Show Apple's revenue, ROE, and stock price Q2 2023",
        "Get Microsoft's net income, ROA, and stock price Q1 2023",
        "Show Google's revenue, margins, and stock return Q3 2023",
        "What is Amazon's financials, ratios, and stock performance Q4 2023?",
        "Show Meta's complete picture: financials, ratios, stock Q2 2023",
    ],
}

# Edge cases
TEST_QUESTIONS_PART4 = {
    "Category 15: Edge Cases (20)": [
        "How did Apple do in Q2 2023?",
        "Tell me about Microsoft's performance last quarter",
        "What's Google's financial situation?",
        "Give me Amazon's numbers for Q4 2023",
        "Show me Meta's results",
        "Apple revenue Q2 23",
        "MSFT net income 2023",
        "GOOG margins Q3",
        "AMZN stock price Q4 2023",
        "FB profit 2023",
        "Show Apple's revenue last quarter",
        "Get Microsoft's net income this year",
        "What was Google's stock price recently?",
        "Show Apple's revenue",
        "What is the stock price for Q2 2023?",
        "Show margins",
        "Show Tesla's revenue Q2 2023",
        "Get Apple's revenue for Q5 2023",
        "What is Microsoft's data for 2030?",
        "Show Netflix's net income Q1 2023",
    ],
}

# Combine all test questions
ALL_TEST_QUESTIONS = {}
ALL_TEST_QUESTIONS.update(TEST_QUESTIONS)
ALL_TEST_QUESTIONS.update(TEST_QUESTIONS_PART2)
ALL_TEST_QUESTIONS.update(TEST_QUESTIONS_PART3)
ALL_TEST_QUESTIONS.update(TEST_QUESTIONS_PART4)


async def test_single_question(decomposer, router, planner, sql_exec, formatter, citation_fetcher, question: str, category: str) -> Dict:
    """Test a single question and validate all 3 criteria"""
    start_time = time.time()
    
    result = {
        "question": question,
        "category": category,
        "status": "UNKNOWN",
        "sql_executed": False,
        "data_retrieved": False,
        "response_shown": False,
        "answer_makes_sense": False,
        "response": "",
        "error": None,
        "execution_time": 0,
        "failure_reason": None,
    }
    
    try:
        # Step 1: Decompose query
        decomposed = await decomposer.decompose(question)
        
        # Step 2: Route intent
        intent = router.route(decomposed)
        
        # Step 3: Plan execution
        plan = await planner.plan(intent, decomposed)
        
        # Step 4: Execute SQL
        sql_results = await sql_exec.execute(plan)
        execution_time = time.time() - start_time
        
        result["execution_time"] = execution_time
        
        # Criterion 1: SQL should source out the data
        if sql_results and len(sql_results) > 0:
            result["sql_executed"] = True
            result["data_retrieved"] = True
        
        # Step 5: Format response
        response_text = await formatter.format_response(sql_results, decomposed, {})
        result["response"] = response_text
        
        # Criterion 1: SQL executed successfully
        if result["sql_executed"]:
            pass  # Already set above
        
        # Criterion 2: Data should be retrieved and shown
        response_text = result["response"].lower()
        
        # Check for "data found" without actual data (this is an issue!)
        if "data found for" in response_text and len(response_text) < 100:
            result["data_retrieved"] = False
            result["response_shown"] = False
            result["failure_reason"] = "DATA_FOUND_BUT_NOT_SHOWN"
        # Check for empty or very short responses
        elif not result["response"] or len(result["response"].strip()) < 20:
            result["data_retrieved"] = False
            result["response_shown"] = False
            result["failure_reason"] = "EMPTY_RESPONSE"
        # Check for error messages
        elif any(err in response_text for err in ["error", "failed", "could not", "unable to"]):
            result["data_retrieved"] = False
            result["response_shown"] = False
            result["failure_reason"] = "ERROR_IN_RESPONSE"
        else:
            result["data_retrieved"] = True
            result["response_shown"] = True
        
        # Criterion 3: Answer should make sense
        # Check if response contains actual data (numbers, company names, metrics)
        has_numbers = any(char.isdigit() for char in result["response"])
        has_company = any(company in result["response"] for company in ["Apple", "Microsoft", "Google", "Amazon", "Meta", "AAPL", "MSFT", "GOOG", "AMZN", "META"])
        has_metrics = any(metric in response_text for metric in ["revenue", "income", "margin", "price", "stock", "gdp", "cpi", "roe", "roa"])
        
        if has_numbers and (has_company or has_metrics):
            result["answer_makes_sense"] = True
        else:
            result["answer_makes_sense"] = False
            if not result["failure_reason"]:
                result["failure_reason"] = "ANSWER_LACKS_DATA"
        
        # Overall status
        if result["sql_executed"] and result["data_retrieved"] and result["response_shown"] and result["answer_makes_sense"]:
            result["status"] = "PASS"
        else:
            result["status"] = "FAIL"
            
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
        result["failure_reason"] = "EXCEPTION"
        result["execution_time"] = time.time() - start_time
    
    return result


async def run_batch_tests(batch_name: str, questions: List[str], category: str):
    """Run a batch of tests"""
    print(f"\n{'='*80}")
    print(f"🧪 Testing: {batch_name}")
    print(f"{'='*80}")
    
    # Initialize components
    decomposer = QueryDecomposer()
    router = IntentRouter()
    planner = TaskPlanner()
    sql_exec = SQLExecutor()
    formatter = ResponseFormatter()
    citation_fetcher = CitationFetcher()
    
    results = []
    
    for i, question in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] Testing: {question[:60]}...")
        result = await test_single_question(decomposer, router, planner, sql_exec, formatter, citation_fetcher, question, category)
        results.append(result)
        
        # Print result
        status_emoji = "✅" if result["status"] == "PASS" else "❌"
        print(f"  {status_emoji} Status: {result['status']}")
        if result["status"] == "FAIL":
            print(f"  ⚠️  Reason: {result['failure_reason']}")
        if result["status"] == "ERROR":
            print(f"  ❌ Error: {result['error'][:100]}")
        print(f"  ⏱️  Time: {result['execution_time']:.2f}s")
    
    return results


async def main():
    """Run all tests in batches"""
    print("="*80)
    print("🚀 COMPREHENSIVE CFO AGENT TEST SUITE")
    print("="*80)
    print(f"Total Questions: {sum(len(q) for q in ALL_TEST_QUESTIONS.values())}")
    print(f"Total Batches: {len(ALL_TEST_QUESTIONS)}")
    print("="*80)
    
    all_results = []
    batch_summaries = []
    
    # Run each batch
    for batch_name, questions in ALL_TEST_QUESTIONS.items():
        batch_results = await run_batch_tests(batch_name, questions, batch_name)
        all_results.extend(batch_results)
        
        # Batch summary
        passed = sum(1 for r in batch_results if r["status"] == "PASS")
        failed = sum(1 for r in batch_results if r["status"] == "FAIL")
        errors = sum(1 for r in batch_results if r["status"] == "ERROR")
        
        batch_summary = {
            "batch": batch_name,
            "total": len(batch_results),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": (passed / len(batch_results) * 100) if batch_results else 0
        }
        batch_summaries.append(batch_summary)
        
        print(f"\n📊 Batch Summary: {passed}/{len(batch_results)} passed ({batch_summary['pass_rate']:.1f}%)")
    
    # Overall summary
    print("\n" + "="*80)
    print("📊 OVERALL TEST RESULTS")
    print("="*80)
    
    total_tests = len(all_results)
    total_passed = sum(1 for r in all_results if r["status"] == "PASS")
    total_failed = sum(1 for r in all_results if r["status"] == "FAIL")
    total_errors = sum(1 for r in all_results if r["status"] == "ERROR")
    overall_pass_rate = (total_passed / total_tests * 100) if total_tests else 0
    
    print(f"\n✅ Passed: {total_passed}/{total_tests} ({overall_pass_rate:.1f}%)")
    print(f"❌ Failed: {total_failed}/{total_tests}")
    print(f"⚠️  Errors: {total_errors}/{total_tests}")
    
    # Categorize failures
    print("\n" + "="*80)
    print("🔍 FAILURE ANALYSIS")
    print("="*80)
    
    failure_categories = {}
    for result in all_results:
        if result["status"] != "PASS":
            reason = result["failure_reason"] or "UNKNOWN"
            if reason not in failure_categories:
                failure_categories[reason] = []
            failure_categories[reason].append(result)
    
    for reason, failures in failure_categories.items():
        print(f"\n❌ {reason}: {len(failures)} questions")
        for failure in failures[:5]:  # Show first 5
            print(f"   - {failure['question'][:70]}")
        if len(failures) > 5:
            print(f"   ... and {len(failures) - 5} more")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_results_comprehensive_{timestamp}.json"
    
    output_data = {
        "timestamp": timestamp,
        "summary": {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "errors": total_errors,
            "pass_rate": overall_pass_rate
        },
        "batch_summaries": batch_summaries,
        "failure_categories": {k: len(v) for k, v in failure_categories.items()},
        "detailed_results": all_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("\n" + "="*80)
    print("✅ TEST SUITE COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
