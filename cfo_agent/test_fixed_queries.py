"""
Test the queries we just fixed
"""
import requests
import json

API_URL = "http://localhost:8000/ask"

# Queries we fixed
FIXED_QUERIES = {
    "Growth QoQ/YoY (10 queries)": [
        "What is Apple's revenue growth QoQ Q2 2023?",
        "Show Microsoft's quarter-over-quarter growth Q1 2023",
        "Get Google's QoQ net income growth Q3 2023",
        "What is Amazon's revenue QoQ Q4 2023?",
        "Show Meta's QoQ margin improvement Q2 2023",
        "What is Apple's revenue growth YoY Q2 2023?",
        "Show Microsoft's year-over-year growth Q1 2023",
        "Get Google's YoY net income growth Q3 2023",
        "What is Amazon's revenue YoY Q4 2023?",
        "Show Meta's YoY performance Q2 2023",
    ],
    "Peer Comparisons (8 queries)": [
        "Show ROE for all companies Q1 2023",
        "What are the debt ratios for all companies Q3 2023?",
        "Show top performer by revenue for 2023",
        "Who led on net income FY2023?",
        "Rank companies by margins for 2023",
        "Who has the best ROE in 2023?",
        "Show stock performance rankings for 2023",
        "Show all companies with complete macro context Q3 2023",
    ],
}

def test_query(question):
    try:
        response = requests.post(API_URL, json={"question": question, "session_id": "test"}, timeout=30)
        if response.status_code == 200:
            answer = response.json().get("response", "")
            if "No results for this task" in answer or len(answer) < 20:
                return "FAIL", answer[:100]
            else:
                return "PASS", answer[:150]
        else:
            return "ERROR", f"HTTP {response.status_code}"
    except Exception as e:
        return "ERROR", str(e)[:100]

print("="*100)
print("🧪 TESTING FIXED QUERIES")
print("="*100)

total_pass = 0
total_fail = 0
total_queries = 0

for category, queries in FIXED_QUERIES.items():
    print(f"\n{'='*100}")
    print(f"📂 {category}")
    print(f"{'='*100}")
    
    cat_pass = 0
    for i, question in enumerate(queries, 1):
        total_queries += 1
        print(f"\n[{i}/{len(queries)}] {question}")
        status, answer = test_query(question)
        
        if status == "PASS":
            cat_pass += 1
            total_pass += 1
            print(f"  ✅ PASS")
            print(f"  💬 {answer}...")
        else:
            total_fail += 1
            print(f"  ❌ {status}")
            print(f"  💬 {answer}")
    
    print(f"\n📊 Category: {cat_pass}/{len(queries)} passed ({cat_pass/len(queries)*100:.1f}%)")

print(f"\n{'='*100}")
print(f"📊 OVERALL RESULTS")
print(f"{'='*100}")
print(f"\n✅ PASSED: {total_pass}/{total_queries} ({total_pass/total_queries*100:.1f}%)")
print(f"❌ FAILED: {total_fail}/{total_queries}")
print(f"\n{'='*100}")
print("✅ TEST COMPLETE!")
print("="*100)
