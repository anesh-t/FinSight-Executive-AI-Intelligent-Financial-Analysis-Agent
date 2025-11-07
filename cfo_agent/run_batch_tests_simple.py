"""
Simple Batch Test Runner - Tests questions via API endpoint
"""
import requests
import json
import time
from datetime import datetime

API_URL = "http://localhost:8000/ask"

# Test questions in batches
BATCH_1_BASIC_FINANCIALS = [
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
]

BATCH_2_MARGINS = [
    "What is Apple's gross margin Q2 2023?",
    "Show Microsoft's gross profit margin for 2023",
    "Get Google's gross margin Q3 2023",
    "What is Apple's operating margin Q2 2023?",
    "Show Microsoft's EBIT margin for 2023",
    "What is Apple's net margin Q2 2023?",
    "Show Microsoft's profit margin for 2023",
    "Show Apple's margins Q2 2023",
    "Get Microsoft's gross, operating, and net margins for 2023",
    "What are Google's profitability margins Q3 2023?",
]

BATCH_3_RATIOS = [
    "What is Apple's ROE Q2 2023?",
    "Show Microsoft's return on equity for 2023",
    "Get Google's ROA Q3 2023",
    "What is Amazon's return on assets Q1 2023?",
    "What is Apple's debt-to-equity ratio Q2 2023?",
    "Show Microsoft's debt to equity for 2023",
    "Show Apple's key ratios Q2 2023",
    "Get Microsoft's financial ratios for 2023",
    "Show Amazon's ROE, ROA, and debt ratios Q1 2023",
    "What are Apple's return and debt ratios for 2023?",
]

BATCH_4_STOCK_PRICES = [
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
]

BATCH_5_MACRO = [
    "What was GDP in Q2 2023?",
    "Show CPI for Q3 2023",
    "What was the unemployment rate in Q1 2023?",
    "Show Fed rate Q4 2023",
    "What was S&P 500 in Q2 2023?",
    "What was GDP in 2023?",
    "Show CPI for 2023",
    "What was the unemployment rate in 2023?",
    "Show Fed rate for 2023",
    "What was S&P 500 performance in 2023?",
]

BATCH_6_FINANCIALS_RATIOS = [
    "Show Apple's revenue and ROE Q2 2023",
    "Get Microsoft's net income and ROA Q1 2023",
    "Show Google's revenue and debt-to-equity Q3 2023",
    "What is Amazon's net income and margins Q4 2023",
    "Show Meta's revenue, net income, and ROE Q2 2023",
]

BATCH_7_FINANCIALS_STOCK = [
    "Show Apple's revenue and stock price Q2 2023",
    "Get Microsoft's net income and stock price Q1 2023",
    "Show Google's revenue and stock return Q3 2023",
    "What is Amazon's net income and stock performance Q4 2023?",
    "Show Meta's revenue, net income, and stock price Q2 2023",
]

BATCH_8_STOCK_RATIOS = [
    "Show Apple's stock price and ROE Q2 2023",
    "Get Microsoft's stock price and ROA Q1 2023",
    "Show Google's stock return and margins Q3 2023",
    "What is Amazon's stock price and debt-to-equity Q4 2023?",
    "Show Meta's stock performance and ROE Q2 2023",
]

BATCH_9_REVENUE_MACRO = [
    "Show Apple's revenue with CPI for Q2 2023",
    "Get Microsoft's revenue with GDP Q1 2023",
    "Show Google's revenue with unemployment Q3 2023",
    "Show Apple's revenue with CPI for 2023",
    "Get Microsoft's revenue with GDP for 2023",
]

BATCH_10_STOCK_MACRO = [
    "Show Apple's stock price with CPI Q2 2023",
    "Get Microsoft's stock price with GDP Q1 2023",
    "Show Google's stock price with unemployment Q3 2023",
    "Show Apple's stock price with CPI for 2023",
    "Get Microsoft's stock price with GDP for 2023",
]

ALL_BATCHES = {
    "Batch 1: Basic Financials (10)": BATCH_1_BASIC_FINANCIALS,
    "Batch 2: Margins (10)": BATCH_2_MARGINS,
    "Batch 3: Ratios (10)": BATCH_3_RATIOS,
    "Batch 4: Stock Prices (10)": BATCH_4_STOCK_PRICES,
    "Batch 5: Macro Indicators (10)": BATCH_5_MACRO,
    "Batch 6: Financials + Ratios (5)": BATCH_6_FINANCIALS_RATIOS,
    "Batch 7: Financials + Stock (5)": BATCH_7_FINANCIALS_STOCK,
    "Batch 8: Stock + Ratios (5)": BATCH_8_STOCK_RATIOS,
    "Batch 9: Revenue + Macro (5)": BATCH_9_REVENUE_MACRO,
    "Batch 10: Stock + Macro (5)": BATCH_10_STOCK_MACRO,
}


def test_question(question: str, session_id: str = "test_session"):
    """Test a single question"""
    try:
        response = requests.post(
            API_URL,
            json={"question": question, "session_id": session_id},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "")
            
            # Check criteria
            sql_executed = True  # If we got 200, SQL ran
            data_retrieved = len(answer) > 0
            response_shown = len(answer) > 20
            
            # Check for "data found" issue
            if "data found for" in answer.lower() and len(answer) < 100:
                failure_reason = "DATA_FOUND_BUT_NOT_SHOWN"
                status = "FAIL"
            elif not answer or len(answer.strip()) < 20:
                failure_reason = "EMPTY_RESPONSE"
                status = "FAIL"
            elif any(err in answer.lower() for err in ["error", "failed", "could not"]):
                failure_reason = "ERROR_IN_RESPONSE"
                status = "FAIL"
            else:
                # Check if answer makes sense
                has_numbers = any(char.isdigit() for char in answer)
                has_company = any(c in answer for c in ["Apple", "Microsoft", "Google", "Amazon", "Meta", "Alphabet"])
                has_metrics = any(m in answer.lower() for m in [
                    "revenue", "income", "margin", "price", "stock", "gdp", "cpi",
                    "unemployment", "fed", "federal funds", "s&p", "sp500", "index",
                    "roe", "roa", "debt", "ratio", "assets", "liabilities", "equity",
                    "cash flow", "r&d", "sg&a", "cogs", "dividend", "buyback", "eps"
                ])
                
                if has_numbers and (has_company or has_metrics):
                    failure_reason = None
                    status = "PASS"
                else:
                    failure_reason = "ANSWER_LACKS_DATA"
                    status = "FAIL"
            
            return {
                "status": status,
                "answer": answer,
                "failure_reason": failure_reason,
                "sql_executed": sql_executed,
                "data_retrieved": data_retrieved,
                "response_shown": response_shown
            }
        else:
            return {
                "status": "ERROR",
                "answer": "",
                "failure_reason": f"HTTP_{response.status_code}",
                "sql_executed": False,
                "data_retrieved": False,
                "response_shown": False
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "answer": "",
            "failure_reason": str(e),
            "sql_executed": False,
            "data_retrieved": False,
            "response_shown": False
        }


def run_batch(batch_name: str, questions: list):
    """Run a batch of tests"""
    print(f"\n{'='*80}")
    print(f"🧪 {batch_name}")
    print(f"{'='*80}")
    
    results = []
    for i, question in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] {question[:70]}...")
        
        start_time = time.time()
        result = test_question(question)
        execution_time = time.time() - start_time
        
        result["question"] = question
        result["execution_time"] = execution_time
        results.append(result)
        
        # Print result
        status_emoji = "✅" if result["status"] == "PASS" else "❌"
        print(f"  {status_emoji} Status: {result['status']}")
        if result["failure_reason"]:
            print(f"  ⚠️  Reason: {result['failure_reason']}")
        print(f"  ⏱️  Time: {execution_time:.2f}s")
        
        # Show first 150 chars of answer
        if result["answer"]:
            print(f"  💬 Answer: {result['answer'][:150]}...")
    
    # Batch summary
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    pass_rate = (passed / len(results) * 100) if results else 0
    
    print(f"\n📊 Batch Summary: {passed}/{len(results)} passed ({pass_rate:.1f}%)")
    
    return results


def main():
    """Run all batches"""
    print("="*80)
    print("🚀 CFO AGENT BATCH TEST SUITE")
    print("="*80)
    print(f"Total Batches: {len(ALL_BATCHES)}")
    print(f"Total Questions: {sum(len(q) for q in ALL_BATCHES.values())}")
    print("="*80)
    
    all_results = []
    batch_summaries = []
    
    for batch_name, questions in ALL_BATCHES.items():
        batch_results = run_batch(batch_name, questions)
        all_results.extend(batch_results)
        
        passed = sum(1 for r in batch_results if r["status"] == "PASS")
        batch_summaries.append({
            "batch": batch_name,
            "total": len(batch_results),
            "passed": passed,
            "failed": sum(1 for r in batch_results if r["status"] == "FAIL"),
            "errors": sum(1 for r in batch_results if r["status"] == "ERROR"),
            "pass_rate": (passed / len(batch_results) * 100) if batch_results else 0
        })
    
    # Overall summary
    print("\n" + "="*80)
    print("📊 OVERALL RESULTS")
    print("="*80)
    
    total = len(all_results)
    passed = sum(1 for r in all_results if r["status"] == "PASS")
    failed = sum(1 for r in all_results if r["status"] == "FAIL")
    errors = sum(1 for r in all_results if r["status"] == "ERROR")
    pass_rate = (passed / total * 100) if total else 0
    
    print(f"\n✅ Passed: {passed}/{total} ({pass_rate:.1f}%)")
    print(f"❌ Failed: {failed}/{total}")
    print(f"⚠️  Errors: {errors}/{total}")
    
    # Failure analysis
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
        for failure in failures[:3]:
            print(f"   - {failure['question'][:70]}")
        if len(failures) > 3:
            print(f"   ... and {len(failures) - 3} more")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"batch_test_results_{timestamp}.json"
    
    output_data = {
        "timestamp": timestamp,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": pass_rate
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
    main()
