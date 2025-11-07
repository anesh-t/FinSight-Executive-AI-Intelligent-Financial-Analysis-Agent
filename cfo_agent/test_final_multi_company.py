"""
Final comprehensive test for multi-company queries (2-5 companies)
"""
import requests
import json

API_URL = "http://localhost:8000/ask"

TEST_QUERIES = [
    # 2 Companies
    ("2 companies - Apple, Microsoft", "Compare Apple and Microsoft revenue Q1 2023", 2),
    ("2 companies - Google, Amazon", "Show Google and Amazon net income Q2 2023", 2),
    
    # 3 Companies
    ("3 companies - AAPL, MSFT, GOOG", "Get Apple, Microsoft, Google revenue Q1 2023", 3),
    ("3 companies - AMZN, META, AAPL", "Show Amazon, Meta, Apple net income Q3 2023", 3),
    
    # 4 Companies
    ("4 companies - explicit names", "Get Apple, Microsoft, Amazon, Meta revenue Q1 2023", 4),
    ("4 companies - ROE metric", "Show Apple, Microsoft, Google, Amazon ROE Q2 2023", 4),
    
    # 5 Companies
    ("5 companies - all explicit", "Get Apple, Microsoft, Google, Amazon, Meta revenue Q1 2023", 5),
    ("5 companies - 'all' keyword", "Show revenue for all 5 companies Q1 2023", 5),
    ("5 companies - 'all companies'", "Show all companies revenue Q2 2023", 5),
]

def count_companies_in_response(response):
    """Count how many companies are mentioned in the response"""
    companies = ["Apple", "Microsoft", "Google", "Alphabet", "Amazon", "Meta"]
    count = sum(1 for company in companies if company in response)
    # Alphabet and Google are the same company
    if "Alphabet" in response and "Google" in response:
        count -= 1
    return count

print("="*100)
print("🧪 FINAL MULTI-COMPANY TEST - Verifying 2-5 Company Support")
print("="*100)

results = []
for test_name, question, expected_count in TEST_QUERIES:
    print(f"\n{'='*100}")
    print(f"📝 Test: {test_name}")
    print(f"❓ Question: {question}")
    print(f"🎯 Expected: {expected_count} companies")
    
    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": question, "session_id": "final_test"},
            timeout=30
        )
        
        if response.status_code == 200:
            answer = response.json().get("response", "")
            actual_count = count_companies_in_response(answer)
            
            # Check if we got the expected number of companies
            if actual_count >= expected_count:
                status = "✅ PASS"
                results.append(("PASS", test_name, expected_count, actual_count))
            else:
                status = "❌ FAIL"
                results.append(("FAIL", test_name, expected_count, actual_count))
            
            print(f"📊 Result: {status}")
            print(f"   Expected: {expected_count} companies")
            print(f"   Got: {actual_count} companies")
            
            # Show first few lines of response
            lines = answer.split('\n')[:5]
            print(f"   Response preview:")
            for line in lines:
                if line.strip():
                    print(f"   {line[:80]}")
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            results.append(("ERROR", test_name, expected_count, 0))
    
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        results.append(("ERROR", test_name, expected_count, 0))

# Summary
print(f"\n{'='*100}")
print("📊 FINAL SUMMARY")
print("="*100)

passed = sum(1 for r in results if r[0] == "PASS")
failed = sum(1 for r in results if r[0] == "FAIL")
errors = sum(1 for r in results if r[0] == "ERROR")
total = len(results)

print(f"\n✅ PASSED: {passed}/{total} ({passed/total*100:.1f}%)")
print(f"❌ FAILED: {failed}/{total}")
print(f"🚫 ERRORS: {errors}/{total}")

# Breakdown by company count
print(f"\n{'='*100}")
print("📈 RESULTS BY COMPANY COUNT")
print("="*100)

for count in [2, 3, 4, 5]:
    count_results = [r for r in results if r[2] == count]
    count_passed = sum(1 for r in count_results if r[0] == "PASS")
    if count_results:
        print(f"\n{count} Companies: {count_passed}/{len(count_results)} passed ({count_passed/len(count_results)*100:.1f}%)")
        for status, name, expected, actual in count_results:
            emoji = "✅" if status == "PASS" else "❌"
            print(f"  {emoji} {name}: Expected {expected}, Got {actual}")

# Final verdict
print(f"\n{'='*100}")
if passed == total:
    print("🎉 ALL TESTS PASSED! Multi-company queries (2-5 companies) working perfectly!")
elif passed >= total * 0.9:
    print("⚠️  MOSTLY WORKING - Some edge cases need attention")
else:
    print("❌ NEEDS MORE WORK - Multiple failures detected")
print("="*100)

# Save results
with open('test_final_multi_company_results.json', 'w') as f:
    json.dump({
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "pass_rate": passed/total*100,
        "details": [
            {
                "status": r[0],
                "test": r[1],
                "expected": r[2],
                "actual": r[3]
            }
            for r in results
        ]
    }, f, indent=2)

print("\n💾 Results saved to: test_final_multi_company_results.json")
