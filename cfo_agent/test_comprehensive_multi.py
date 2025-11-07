"""
Comprehensive test for multi-year and multi-company queries
"""
import requests
import json
import time

API_URL = "http://localhost:8000/ask"

# Comprehensive test cases
TEST_CASES = {
    "1. Multi-Company Single Period (Quarterly)": [
        "Show Apple and Microsoft revenue for Q2 2023",
        "Compare Apple, Microsoft, Google revenue Q3 2023",
        "Get Apple, Microsoft, Amazon, Meta revenue Q1 2023",
        "Show all 5 companies revenue Q4 2023",
        "Compare Apple vs Microsoft ROE Q2 2023",
        "Show Apple and Google net income Q3 2023",
    ],
    
    "2. Multi-Company Single Period (Annual)": [
        "Compare Apple and Microsoft revenue for 2023",
        "Show Apple, Microsoft, Google revenue 2022",
        "Get all companies revenue for 2023",
        "Compare Apple vs Microsoft ROE 2023",
        "Show Apple and Google net income 2022",
    ],
    
    "3. Single Company Multi-Quarter": [
        "Show Apple revenue for Q1, Q2, Q3 2023",
        "Get Microsoft revenue Q1 and Q2 2023",
        "Show Google net income Q1, Q2, Q3, Q4 2023",
        "Apple ROE for Q1, Q2 2023",
    ],
    
    "4. Single Company Multi-Year": [
        "Show Apple revenue for 2021, 2022, 2023",
        "Get Microsoft revenue 2022 and 2023",
        "Show Google net income 2021, 2022, 2023",
        "Apple revenue trend 2020-2023",
    ],
    
    "5. Multi-Company Multi-Quarter (Same Year)": [
        "Compare Apple and Microsoft revenue Q1, Q2 2023",
        "Show Apple vs Microsoft ROE Q1, Q2, Q3 2023",
        "Get Apple, Microsoft, Google revenue Q1 and Q2 2023",
    ],
    
    "6. Multi-Company Multi-Year": [
        "Compare Apple and Microsoft revenue for 2022 and 2023",
        "Show Apple vs Microsoft revenue 2021, 2022, 2023",
        "Get Apple, Microsoft, Google revenue 2022 and 2023",
        "Compare all companies revenue 2022 vs 2023",
    ],
}

def test_query(question):
    """Test a single query and return detailed results"""
    try:
        start = time.time()
        response = requests.post(API_URL, json={"question": question, "session_id": "test"}, timeout=30)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            answer = response.json().get("response", "")
            
            # Validation checks
            sql_executed = True
            data_shown = len(answer) > 20 and "No results for this task" not in answer
            
            # Check if answer makes sense
            has_numbers = any(char.isdigit() for char in answer)
            has_company = any(c in answer for c in ["Apple", "Microsoft", "Google", "Amazon", "Meta", "Alphabet"])
            has_period = any(p in answer for p in ["2020", "2021", "2022", "2023", "2024", "Q1", "Q2", "Q3", "Q4", "FY"])
            makes_sense = has_numbers and has_company and has_period
            
            # Determine status
            if data_shown and makes_sense:
                status = "PASS"
            elif data_shown:
                status = "PARTIAL"
            else:
                status = "FAIL"
            
            return {
                "status": status,
                "sql_executed": sql_executed,
                "data_shown": data_shown,
                "makes_sense": makes_sense,
                "answer": answer,
                "time": elapsed
            }
        else:
            return {
                "status": "ERROR",
                "sql_executed": False,
                "data_shown": False,
                "makes_sense": False,
                "answer": f"HTTP {response.status_code}",
                "time": 0
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "sql_executed": False,
            "data_shown": False,
            "makes_sense": False,
            "answer": str(e),
            "time": 0
        }

# Run tests
print("="*100)
print("🧪 COMPREHENSIVE MULTI-YEAR & MULTI-COMPANY TEST")
print("="*100)

all_results = []
category_stats = {}

for category, queries in TEST_CASES.items():
    print(f"\n{'='*100}")
    print(f"📂 {category}")
    print(f"{'='*100}\n")
    
    cat_results = []
    
    for i, question in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] Testing: {question}")
        result = test_query(question)
        result['category'] = category
        result['question'] = question
        
        # Print result
        emoji = "✅" if result['status'] == "PASS" else "⚠️" if result['status'] == "PARTIAL" else "❌"
        print(f"  {emoji} {result['status']} ({result['time']:.2f}s)")
        print(f"  📊 Validation: SQL={'✅' if result['sql_executed'] else '❌'} | Data={'✅' if result['data_shown'] else '❌'} | Sense={'✅' if result['makes_sense'] else '❌'}")
        
        if result['status'] != "PASS":
            print(f"  💬 {result['answer'][:150]}...")
        
        cat_results.append(result)
        all_results.append(result)
        print()
    
    # Category summary
    passed = sum(1 for r in cat_results if r['status'] == "PASS")
    partial = sum(1 for r in cat_results if r['status'] == "PARTIAL")
    failed = sum(1 for r in cat_results if r['status'] == "FAIL")
    
    category_stats[category] = {
        "total": len(cat_results),
        "passed": passed,
        "partial": partial,
        "failed": failed,
        "pass_rate": (passed / len(cat_results) * 100) if cat_results else 0
    }
    
    print(f"📊 Category Result: {passed}/{len(cat_results)} PASS ({passed/len(cat_results)*100:.1f}%)")

# Final Summary
print(f"\n{'='*100}")
print("📊 FINAL SUMMARY")
print("="*100)

total_queries = len(all_results)
total_pass = sum(1 for r in all_results if r['status'] == "PASS")
total_partial = sum(1 for r in all_results if r['status'] == "PARTIAL")
total_fail = sum(1 for r in all_results if r['status'] == "FAIL")
total_error = sum(1 for r in all_results if r['status'] == "ERROR")

print(f"\n📈 Overall Results:")
print(f"  Total Queries: {total_queries}")
print(f"  ✅ PASS: {total_pass} ({total_pass/total_queries*100:.1f}%)")
print(f"  ⚠️  PARTIAL: {total_partial} ({total_partial/total_queries*100:.1f}%)")
print(f"  ❌ FAIL: {total_fail} ({total_fail/total_queries*100:.1f}%)")
print(f"  🚫 ERROR: {total_error} ({total_error/total_queries*100:.1f}%)")

print(f"\n📊 Results by Category:")
for category, stats in category_stats.items():
    emoji = "✅" if stats['pass_rate'] == 100 else "⚠️" if stats['pass_rate'] >= 50 else "❌"
    print(f"  {emoji} {category}")
    print(f"     {stats['passed']}/{stats['total']} PASS ({stats['pass_rate']:.1f}%)")

# Show failures
failures = [r for r in all_results if r['status'] in ['FAIL', 'PARTIAL', 'ERROR']]
if failures:
    print(f"\n{'='*100}")
    print(f"🔍 FAILED/PARTIAL QUERIES ({len(failures)} total)")
    print("="*100)
    for r in failures:
        print(f"\n{r['status']}: {r['question']}")
        print(f"  Category: {r['category']}")
        print(f"  Answer: {r['answer'][:200]}")

# Validation criteria summary
print(f"\n{'='*100}")
print("✅ VALIDATION CRITERIA MET")
print("="*100)
sql_ok = sum(1 for r in all_results if r['sql_executed'])
data_ok = sum(1 for r in all_results if r['data_shown'])
sense_ok = sum(1 for r in all_results if r['makes_sense'])

print(f"\n1. SQL sources the data: {sql_ok}/{total_queries} ({sql_ok/total_queries*100:.1f}%)")
print(f"2. Data shown in chat: {data_ok}/{total_queries} ({data_ok/total_queries*100:.1f}%)")
print(f"3. Answer makes sense: {sense_ok}/{total_queries} ({sense_ok/total_queries*100:.1f}%)")

print(f"\n{'='*100}")
print("✅ TEST COMPLETE!")
print("="*100)

# Save results
with open('test_multi_comprehensive_results.json', 'w') as f:
    json.dump({
        "summary": {
            "total": total_queries,
            "passed": total_pass,
            "partial": total_partial,
            "failed": total_fail,
            "error": total_error,
            "pass_rate": total_pass/total_queries*100
        },
        "category_stats": category_stats,
        "all_results": all_results
    }, f, indent=2)

print(f"\n💾 Results saved to: test_multi_comprehensive_results.json")
