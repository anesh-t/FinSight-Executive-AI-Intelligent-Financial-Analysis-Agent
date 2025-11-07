"""
Live test of hybrid queries with LLM synthesis
"""
import requests
import json
import time

API_URL = "http://localhost:8000/ask/hybrid"

# Test queries
test_queries = [
    {
        "name": "Margin Analysis (Your Query)",
        "question": "What drove the margin swing last quarter—show me the numbers, macro context, and 10-K citations?",
        "expected": "Should combine margin data from SQL + business context from 10-K"
    },
    {
        "name": "Apple Margin Analysis",
        "question": "What drove Apple's margin changes in 2022? Show me the numbers and explain the business context.",
        "expected": "Should show Apple's margin data + 10-K context"
    },
    {
        "name": "Risk Impact on Financials",
        "question": "How did supply chain risks affect Apple's margins? Show the financial impact and 10-K citations.",
        "expected": "Should combine risk factors from 10-K + actual margin impact"
    },
    {
        "name": "Revenue Drivers",
        "question": "Show me Apple's revenue for 2022 and explain what drove it from their 10-K.",
        "expected": "Should combine revenue numbers + business drivers from MD&A"
    }
]

print("="*100)
print("🧪 TESTING HYBRID QUERIES WITH LLM SYNTHESIS")
print("="*100)
print()

for i, test in enumerate(test_queries, 1):
    print(f"\n{'='*100}")
    print(f"TEST {i}/{len(test_queries)}: {test['name']}")
    print(f"{'='*100}")
    print(f"\n📝 Question:")
    print(f"   {test['question']}")
    print(f"\n🎯 Expected:")
    print(f"   {test['expected']}")
    print(f"\n⏳ Processing...")
    
    try:
        start_time = time.time()
        response = requests.post(
            API_URL,
            json={"question": test['question'], "session_id": f"test_{i}"},
            timeout=30
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('response', 'No response')
            metadata = result.get('viz_metadata', {})
            
            print(f"\n✅ SUCCESS (took {elapsed:.2f}s)")
            print(f"\n📊 Metadata:")
            print(f"   Intent: {metadata.get('intent', 'N/A')}")
            print(f"   Agents Used: {', '.join(metadata.get('agents_used', []))}")
            print(f"   Success: {metadata.get('success', 'N/A')}")
            
            print(f"\n💬 SYNTHESIZED ANSWER:")
            print("─" * 100)
            print(answer)
            print("─" * 100)
            
        else:
            print(f"\n❌ FAILED: Status {response.status_code}")
            print(f"   Error: {response.text[:200]}")
    
    except requests.exceptions.Timeout:
        print(f"\n⏱️  TIMEOUT: Query took longer than 30 seconds")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
    
    # Wait between queries
    if i < len(test_queries):
        print(f"\n⏳ Waiting 3 seconds before next query...")
        time.sleep(3)

print(f"\n\n{'='*100}")
print("📊 TEST SUMMARY")
print(f"{'='*100}")
print(f"\n✅ All hybrid queries tested!")
print(f"\n🎯 Key Features Demonstrated:")
print(f"   • Query classification (HYBRID detection)")
print(f"   • Parallel RAG + SQL execution")
print(f"   • LLM-powered synthesis (GPT-4o)")
print(f"   • Integration of structured + unstructured data")
print(f"   • Professional CFO-level responses")
print(f"\n{'='*100}\n")
