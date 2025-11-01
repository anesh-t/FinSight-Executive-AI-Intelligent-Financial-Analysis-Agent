"""Test improved classification logic"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from master_agent.routing.query_classifier import QueryClassifier

classifier = QueryClassifier()

# Test the problematic queries from the comprehensive test
test_queries = [
    "How did Apple's supply chain risks affect their gross margins?",
    "What cybersecurity risks did Microsoft face in 2022, and how did these correlate with their R&D spending?",
    "What strategic priorities did Apple highlight, and how did these align with their revenue growth?",
    "Compare regulatory risks of Apple and Microsoft, and analyze impact on operating margins",
    "What operational challenges did Apple describe related to manufacturing, and what was their capex?",
    "What foreign exchange risks did Apple disclose, and what was their international revenue?",
    "How did Microsoft describe competitive pressures, and what was their revenue?",
    "What innovation strategies did Apple discuss, and how much did they invest in R&D?",
    "How did Apple address COVID-19 risks, and what was their cash position?",
    "What climate risks did Microsoft disclose, and what was their operating expenses?",
]

print("="*100)
print("🔍 IMPROVED CLASSIFICATION TEST")
print("="*100)

hybrid_count = 0
for i, query in enumerate(test_queries, 1):
    result = classifier.classify(query)
    
    is_hybrid = result.intent.value == 'hybrid'
    if is_hybrid:
        hybrid_count += 1
    
    status = "✅ HYBRID" if is_hybrid else f"❌ {result.intent.value.upper()}"
    
    print(f"\n{i}. {status} ({result.confidence:.0%})")
    print(f"   {query[:80]}...")
    print(f"   Reasoning: {result.reasoning}")

print(f"\n{'='*100}")
print(f"📊 RESULTS:")
print(f"   Hybrid Detected: {hybrid_count}/{len(test_queries)} ({hybrid_count/len(test_queries)*100:.0f}%)")
print(f"   Target: 10/10 (100%)")

if hybrid_count == len(test_queries):
    print(f"\n🎉 ✅ PERFECT! All hybrid queries correctly classified!")
elif hybrid_count >= 8:
    print(f"\n👍 GOOD! Most hybrid queries detected ({hybrid_count}/10)")
else:
    print(f"\n⚠️  NEEDS MORE WORK - Only {hybrid_count}/10 detected")

print(f"={'='*100}\n")
