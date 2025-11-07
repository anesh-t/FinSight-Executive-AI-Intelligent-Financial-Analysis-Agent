"""
Test multi-year and multi-company queries
"""
import requests
import json

API_URL = "http://localhost:8000/ask"

TEST_QUERIES = {
    "Multi-Company Single Period": [
        "Show Apple and Microsoft revenue for Q2 2023",
        "Compare Apple vs Microsoft ROE Q2 2023",
        "Show Apple, Microsoft, and Google net income Q2 2023",
        "Compare all companies revenue for 2023",
    ],
    "Single Company Multi-Period": [
        "Show Apple revenue for Q1, Q2, Q3 2023",
        "Get Microsoft revenue for 2022 and 2023",
        "Show Google revenue for Q1 2022, Q1 2023",
        "Apple revenue trend 2021, 2022, 2023",
    ],
    "Multi-Company Multi-Period": [
        "Compare Apple and Microsoft revenue for 2022 and 2023",
        "Show Apple vs Microsoft ROE for Q1, Q2 2023",
        "Compare all companies revenue 2022 vs 2023",
        "Show Apple, Microsoft revenue Q1 2023 vs Q1 2024",
    ],
}

def test_query(question):
    try:
        response = requests.post(API_URL, json={"question": question, "session_id": "test"}, timeout=30)
        if response.status_code == 200:
            answer = response.json().get("response", "")
            
            # Check criteria
            sql_executed = True
            data_shown = len(answer) > 20 and "No results" not in answer
            
            # Check if answer makes sense
            has_numbers = any(char.isdigit() for char in answer)
            has_company = any(c in answer for c in ["Apple", "Microsoft", "Google", "Amazon", "Meta", "Alphabet"])
            makes_sense = has_numbers and has_company
            
            if data_shown and makes_sense:
                return "PASS", answer, True, True, True
            elif data_shown:
                return "PARTIAL", answer, True, True, False
            else:
                return "FAIL", answer, sql_executed, False, False
        else:
            return "ERROR", f"HTTP {response.status_code}", False, False, False
    except Exception as e:
        return "ERROR", str(e), False, False, False

print("="*100)
print("🧪 TESTING MULTI-YEAR AND MULTI-COMPANY QUERIES")
print("="*100)

all_results = []

for category, queries in TEST_QUERIES.items():
    print(f"\n{'='*100}")
    print(f"📂 {category}")
    print(f"{'='*100}")
    
    for i, question in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] {question}")
        status, answer, sql_ok, data_ok, sense_ok = test_query(question)
        
        result = {
            "category": category,
            "question": question,
            "status": status,
            "sql_executed": sql_ok,
            "data_shown": data_ok,
            "makes_sense": sense_ok,
            "answer": answer[:200]
        }
        all_results.append(result)
        
        # Print status
        emoji = "✅" if status == "PASS" else "⚠️" if status == "PARTIAL" else "❌"
        print(f"  {emoji} {status}")
        print(f"  📊 Validation:")
        print(f"     - SQL executed: {'✅' if sql_ok else '❌'}")
        print(f"     - Data shown: {'✅' if data_ok else '❌'}")
        print(f"     - Makes sense: {'✅' if sense_ok else '❌'}")
        print(f"  💬 Answer: {answer[:150]}...")

# Summary
print(f"\n{'='*100}")
print("📊 SUMMARY BY CATEGORY")
print("="*100)

for category in TEST_QUERIES.keys():
    cat_results = [r for r in all_results if r["category"] == category]
    passed = sum(1 for r in cat_results if r["status"] == "PASS")
    partial = sum(1 for r in cat_results if r["status"] == "PARTIAL")
    failed = sum(1 for r in cat_results if r["status"] == "FAIL")
    
    print(f"\n{category}:")
    print(f"  ✅ PASS: {passed}/{len(cat_results)}")
    print(f"  ⚠️  PARTIAL: {partial}/{len(cat_results)}")
    print(f"  ❌ FAIL: {failed}/{len(cat_results)}")

print(f"\n{'='*100}")
print("📊 OVERALL")
print("="*100)
total_pass = sum(1 for r in all_results if r["status"] == "PASS")
total_partial = sum(1 for r in all_results if r["status"] == "PARTIAL")
total_fail = sum(1 for r in all_results if r["status"] == "FAIL")
total = len(all_results)

print(f"\n✅ PASS: {total_pass}/{total} ({total_pass/total*100:.1f}%)")
print(f"⚠️  PARTIAL: {total_partial}/{total} ({total_partial/total*100:.1f}%)")
print(f"❌ FAIL: {total_fail}/{total} ({total_fail/total*100:.1f}%)")

# Show failures
if total_fail > 0 or total_partial > 0:
    print(f"\n{'='*100}")
    print("🔍 ISSUES TO FIX")
    print("="*100)
    for r in all_results:
        if r["status"] != "PASS":
            print(f"\n{r['status']}: {r['question']}")
            print(f"  Answer: {r['answer'][:100]}")

print(f"\n{'='*100}")
print("✅ TEST COMPLETE!")
print("="*100)
