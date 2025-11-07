"""
Test a sample of 20 questions to verify system is working
"""
import requests
import json
import time

API_URL = "http://localhost:8000/ask"

# Sample 20 questions covering different types
SAMPLE_QUESTIONS = [
    # Basic financials
    "What was Apple's revenue in Q2 2023?",
    "Show Microsoft's net income for 2023",
    # Margins
    "What is Apple's gross margin Q2 2023?",
    "Show Microsoft's operating margin for 2023",
    # Ratios
    "What is Apple's ROE Q2 2023?",
    "Get Google's ROA Q3 2023",
    # Stock prices
    "What was Apple's stock price Q2 2023?",
    "Show Microsoft's stock price for 2023",
    # Macro indicators
    "What was GDP in Q2 2023?",
    "Show CPI for 2023",
    "What was the unemployment rate in Q1 2023?",
    "Show Fed rate for 2023",
    # Combinations
    "Show Apple's revenue and ROE Q2 2023",
    "Get Microsoft's revenue and stock price for 2023",
    "Show Apple's stock price and ROE Q2 2023",
    # Revenue + Macro
    "Show Apple's revenue with CPI for Q2 2023",
    "Get Microsoft's revenue with GDP for 2023",
    # Stock + Macro
    "Show Apple's stock price with CPI Q2 2023",
    # Cash flow
    "What is Apple's operating cash flow Q2 2023?",
    "Show Microsoft's free cash flow for 2023",
]

def test_question(question: str):
    """Test a single question"""
    try:
        response = requests.post(
            API_URL,
            json={"question": question, "session_id": "sample_test"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "")
            
            # Check all 3 criteria
            sql_executed = True
            data_retrieved = len(answer) > 0
            response_shown = len(answer) > 20
            
            # Determine status
            if "no results for this task" in answer.lower():
                status = "FAIL"
                reason = "NO_RESULTS"
            elif not answer or len(answer.strip()) < 20:
                status = "FAIL"
                reason = "EMPTY_RESPONSE"
            elif any(err in answer.lower() for err in ["error", "failed", "could not"]):
                status = "FAIL"
                reason = "ERROR_IN_RESPONSE"
            else:
                has_numbers = any(char.isdigit() for char in answer)
                has_content = any(m in answer.lower() for m in [
                    "revenue", "income", "margin", "price", "stock", "gdp", "cpi",
                    "unemployment", "fed", "roe", "roa", "reported", "was", "for"
                ])
                
                if has_numbers and has_content:
                    status = "PASS"
                    reason = None
                else:
                    status = "FAIL"
                    reason = "LACKS_DATA"
            
            return {
                "status": status,
                "reason": reason,
                "answer": answer,
                "sql_executed": sql_executed,
                "data_retrieved": data_retrieved,
                "response_shown": response_shown
            }
        else:
            return {
                "status": "ERROR",
                "reason": f"HTTP_{response.status_code}",
                "answer": "",
                "sql_executed": False,
                "data_retrieved": False,
                "response_shown": False
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "reason": str(e),
            "answer": "",
            "sql_executed": False,
            "data_retrieved": False,
            "response_shown": False
        }

print("="*100)
print("🧪 TESTING SAMPLE OF 20 QUESTIONS")
print("="*100)

results = []
for i, question in enumerate(SAMPLE_QUESTIONS, 1):
    print(f"\n[{i}/20] {question}")
    
    start = time.time()
    result = test_question(question)
    elapsed = time.time() - start
    
    result["question"] = question
    result["time"] = elapsed
    results.append(result)
    
    emoji = "✅" if result["status"] == "PASS" else "❌"
    print(f"  {emoji} {result['status']}", end="")
    if result["reason"]:
        print(f" - {result['reason']}", end="")
    print(f" ({elapsed:.2f}s)")
    
    # Show validation
    print(f"     SQL: {'✅' if result['sql_executed'] else '❌'} | " +
          f"Data: {'✅' if result['data_retrieved'] else '❌'} | " +
          f"Shown: {'✅' if result['response_shown'] else '❌'}")
    
    # Show answer preview
    if result["answer"]:
        preview = result["answer"][:120].replace('\n', ' ')
        print(f"     💬 {preview}...")

# Summary
print("\n" + "="*100)
print("📊 SUMMARY")
print("="*100)

passed = sum(1 for r in results if r["status"] == "PASS")
failed = sum(1 for r in results if r["status"] == "FAIL")
errors = sum(1 for r in results if r["status"] == "ERROR")

print(f"\n✅ PASSED: {passed}/20 ({passed/20*100:.1f}%)")
print(f"❌ FAILED: {failed}/20")
print(f"⚠️  ERRORS: {errors}/20")

if failed > 0 or errors > 0:
    print("\n🔍 FAILURES:")
    for r in results:
        if r["status"] != "PASS":
            print(f"  ❌ {r['question']}")
            print(f"     Reason: {r['reason']}")

print("\n✅ Sample test complete!")
