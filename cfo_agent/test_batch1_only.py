"""
Test Batch 1 Only - Basic Financials
"""
import requests
import json
import time
from datetime import datetime

API_URL = "http://localhost:8000/ask"

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


def main():
    """Run Batch 1 tests"""
    print("="*80)
    print("🚀 BATCH 1: BASIC FINANCIALS (10 questions)")
    print("="*80)
    
    results = []
    for i, question in enumerate(BATCH_1_BASIC_FINANCIALS, 1):
        print(f"\n[{i}/{len(BATCH_1_BASIC_FINANCIALS)}] {question}")
        
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
        
        # Show answer
        if result["answer"]:
            print(f"  💬 Answer: {result['answer'][:200]}...")
        
        # Validation details
        print(f"  📊 Validation:")
        print(f"     - SQL executed: {'✅' if result['sql_executed'] else '❌'}")
        print(f"     - Data retrieved: {'✅' if result['data_retrieved'] else '❌'}")
        print(f"     - Response shown: {'✅' if result['response_shown'] else '❌'}")
    
    # Summary
    print("\n" + "="*80)
    print("📊 BATCH 1 RESULTS")
    print("="*80)
    
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    pass_rate = (passed / len(results) * 100) if results else 0
    
    print(f"\n✅ Passed: {passed}/{len(results)} ({pass_rate:.1f}%)")
    print(f"❌ Failed: {failed}/{len(results)}")
    print(f"⚠️  Errors: {errors}/{len(results)}")
    
    # Show failures
    if failed > 0 or errors > 0:
        print("\n" + "="*80)
        print("🔍 FAILURES")
        print("="*80)
        for result in results:
            if result["status"] != "PASS":
                print(f"\n❌ {result['question']}")
                print(f"   Reason: {result['failure_reason']}")
                print(f"   Answer: {result['answer'][:150]}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"batch1_results_{timestamp}.json"
    
    output_data = {
        "timestamp": timestamp,
        "batch": "Batch 1: Basic Financials",
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "pass_rate": pass_rate,
        "results": results
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("\n" + "="*80)
    print("✅ BATCH 1 TEST COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    main()
